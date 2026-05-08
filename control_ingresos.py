import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
try:
    from database import crear_base_de_datos 
except ImportError:
    def crear_base_de_datos(): pass

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class VentanaIngresos(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        crear_base_de_datos()
        
        self.pagina_actual = 1
        self.clientes_por_pagina = 10
        self.datos_brutos = [] 
        self.datos_filtrados = [] 
        self.canvas_grafica = None 

        # --- CONTENEDOR DESPLAZABLE PRINCIPAL ---
        # Agregamos el scrollable frame que ocupará toda la ventana
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True)

        self.configurar_interfaz()
        self.cargar_y_procesar_ingresos()

    def configurar_interfaz(self):
        # NOTA: Todos los elementos ahora se empaquetan en 'self.main_scroll' en lugar de 'self'
        
        # --- CABECERA ---
        self.frame_top = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.frame_top.pack(pady=(20, 10), padx=20, fill="x")
        ctk.CTkLabel(self.frame_top, text="INGRESOS", font=("Arial", 28, "bold")).pack(side="left")

        # --- FILTROS ---
        self.frame_filtros = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.frame_filtros.pack(pady=10, padx=20, fill="x")

        self.entry_busqueda = ctk.CTkEntry(self.frame_filtros, placeholder_text="Nombre o Apellido...", width=180)
        self.entry_busqueda.pack(side="left", padx=5)
        self.entry_busqueda.bind("<KeyRelease>", lambda e: self.aplicar_filtros())

        self.combo_filtro_plan = ctk.CTkOptionMenu(self.frame_filtros, values=self.obtener_planes_db(),
                                                   command=lambda v: self.aplicar_filtros())
        self.combo_filtro_plan.pack(side="left", padx=5)
        self.combo_filtro_plan.set("Todos")

        ctk.CTkLabel(self.frame_filtros, text="Desde:").pack(side="left", padx=(10, 2))
        self.entry_desde = ctk.CTkEntry(self.frame_filtros, placeholder_text="dd/mm/aaaa", width=100)
        self.entry_desde.pack(side="left", padx=5)
        self.entry_desde.bind("<KeyRelease>", lambda e: self.aplicar_filtros())

        ctk.CTkLabel(self.frame_filtros, text="Hasta:").pack(side="left", padx=(10, 2))
        self.entry_hasta = ctk.CTkEntry(self.frame_filtros, placeholder_text="dd/mm/aaaa", width=100)
        self.entry_hasta.pack(side="left", padx=5)
        self.entry_hasta.bind("<KeyRelease>", lambda e: self.aplicar_filtros())

        self.btn_grafica = ctk.CTkButton(self.frame_filtros, text="Ver gráfica", width=100, 
                                         fg_color="#6610f2", hover_color="#520DC2", 
                                         command=self.alternar_vista_grafica)
        self.btn_grafica.pack(side="right", padx=10)

        # --- CONTENEDOR PRINCIPAL (TABLA/GRÁFICA) ---
        # Ajustamos la altura mínima para asegurar que el scroll sea necesario si el contenido crece
        self.contenedor_principal = ctk.CTkFrame(self.main_scroll)
        self.contenedor_principal.pack(pady=(10, 0), padx=20, fill="both", expand=True)
        self.crear_tabla()

        # --- SECCIÓN INFERIOR: TOTAL ---
        self.frame_total = ctk.CTkFrame(self.main_scroll, fg_color="#1a1a1a", height=50)
        self.frame_total.pack(pady=(10, 5), padx=20, fill="x")
        
        self.label_total_dinero = ctk.CTkLabel(self.frame_total, text="TOTAL INGRESOS: $0.00", 
                                               font=("Arial", 20, "bold"), text_color="#2ecc71")
        self.label_total_dinero.pack(side="right", padx=20, pady=10)

        # --- SECCIÓN INFERIOR: PAGINACIÓN ---
        self.frame_paginacion = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.frame_paginacion.pack(fill="x", pady=(5, 20))
        
        self.centro_paginacion = ctk.CTkFrame(self.frame_paginacion, fg_color="transparent")
        self.centro_paginacion.pack(expand=True)

        self.btn_ant = ctk.CTkButton(self.centro_paginacion, text="Anterior", command=self.pagina_anterior, width=80)
        self.btn_ant.pack(side="left", padx=2)
        
        self.label_paginas = ctk.CTkLabel(self.centro_paginacion, text="Página 1 de 1", font=("Arial", 14))
        self.label_paginas.pack(side="left", padx=15)
        
        self.btn_sig = ctk.CTkButton(self.centro_paginacion, text="Siguiente", command=self.pagina_siguiente, width=80)
        self.btn_sig.pack(side="left", padx=2)

    # ... (El resto de los métodos: cargar_y_procesar_ingresos, aplicar_filtros, etc., permanecen iguales)
    
    def cargar_y_procesar_ingresos(self):
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                query = """
                    SELECT p.fecha_inscripcion, c.nombre, c.apellido, p.plan_seleccionado, pl.precio, p.id_cliente
                    FROM plan_elegido p
                    JOIN clientes c ON p.id_cliente = c.id
                    JOIN planes pl ON p.plan_seleccionado = pl.nombre_plan
                    WHERE p.pago = 'Realizado'
                    ORDER BY p.fecha_inscripcion DESC
                """
                cursor.execute(query)
                planes_pagados = cursor.fetchall()
                self.datos_brutos = [(f[0], f[1], f[2], f[3], f[4]) for f in planes_pagados]
            self.aplicar_filtros()
        except Exception as e:
            print(f"Error: {e}")

    def aplicar_filtros(self):
        busqueda = self.entry_busqueda.get().lower().strip()
        plan_sel = self.combo_filtro_plan.get()
        f_desde = self.entry_desde.get().strip()
        f_hasta = self.entry_hasta.get().strip()
        
        self.datos_filtrados = []
        d_obj = h_obj = None
        
        try:
            if len(f_desde) == 10: d_obj = datetime.strptime(f_desde, "%d/%m/%Y")
            if len(f_hasta) == 10: h_obj = datetime.strptime(f_hasta, "%d/%m/%Y")
        except: pass

        for reg in self.datos_brutos:
            f_reg = datetime.strptime(reg[0], "%Y-%m-%d")
            match_txt = busqueda in reg[1].lower() or busqueda in reg[2].lower()
            match_plan = (plan_sel == "Todos" or reg[3] == plan_sel)
            match_fecha = True
            if d_obj and f_reg < d_obj: match_fecha = False
            if h_obj and f_reg > h_obj: match_fecha = False
            
            if match_txt and match_plan and match_fecha:
                self.datos_filtrados.append(reg)

        self.pagina_actual = 1
        self.recalcular_total()
        self.actualizar_tabla()

    def recalcular_total(self):
        total = sum(reg[4] for reg in self.datos_filtrados)
        self.label_total_dinero.configure(text=f"TOTAL INGRESOS: ${total:,.2f}")

    def actualizar_tabla(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        inicio = (self.pagina_actual - 1) * self.clientes_por_pagina
        fin = inicio + self.clientes_por_pagina
        datos_pagina = self.datos_filtrados[inicio:fin]
        
        for i, (fecha, nom, ape, plan, monto) in enumerate(datos_pagina, start=inicio + 1):
            try: f_fmt = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
            except: f_fmt = fecha
            self.tabla.insert("", "end", values=(i, f_fmt, nom, ape, plan, f"${monto:,.2f}"))

        total_pag = max(1, (len(self.datos_filtrados) + self.clientes_por_pagina - 1) // self.clientes_por_pagina)
        self.label_paginas.configure(text=f"Página {self.pagina_actual} de {total_pag}")

    def pagina_siguiente(self):
        total_pag = (len(self.datos_filtrados) + self.clientes_por_pagina - 1) // self.clientes_por_pagina
        if self.pagina_actual < total_pag:
            self.pagina_actual += 1
            self.actualizar_tabla()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_tabla()

    def obtener_planes_db(self):
        planes = ["Todos"]
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre_plan FROM planes")
                planes.extend([row[0] for row in cursor.fetchall()])
        except: planes.extend(["Mensual", "Anual"])
        return planes

    def crear_tabla(self):
        self.frame_tabla = ctk.CTkFrame(self.contenedor_principal, fg_color="transparent")
        self.frame_tabla.pack(fill="both", expand=True)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0, rowheight=30)
        style.map("Treeview", background=[('selected', '#3498db')])
        style.configure("Treeview.Heading", background="#1a1a1a", foreground="white", relief="flat")

        self.tabla = ttk.Treeview(self.frame_tabla, columns=("Nro", "Fecha", "Nombre", "Apellido", "Plan", "Ingreso"), show="headings")
        for col in ("Nro", "Fecha", "Nombre", "Apellido", "Plan", "Ingreso"):
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=120)
        self.tabla.pack(side="left", fill="both", expand=True)

    def alternar_vista_grafica(self):
        if self.canvas_grafica:
            self.canvas_grafica.get_tk_widget().destroy()
            self.canvas_grafica = None
            self.frame_tabla.pack(fill="both", expand=True)
            self.btn_grafica.configure(text="Ver gráfica")
        else:
            self.frame_tabla.pack_forget()
            self.btn_grafica.configure(text="Ver tabla")
            self.dibujar_grafica()

    def dibujar_grafica(self):
        meses_labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        totales_por_mes = {i: 0.0 for i in range(1, 13)}
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT CAST(strftime('%m', fecha) AS INTEGER) as mes, SUM(monto) FROM ingresos GROUP BY mes")
                for mes, suma in cursor.fetchall():
                    if mes: totales_por_mes[mes] = suma
        except: return

        valores = [totales_por_mes[i] for i in range(1, 13)]
        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')
        barras = ax.bar(meses_labels, valores, color='#2ecc71', width=0.7)
        for barra in barras:
            yval = barra.get_height()
            if yval > 0:
                ax.annotate(f'${yval:,.0f}', xy=(barra.get_x() + barra.get_width() / 2, yval),
                            xytext=(0, 5), textcoords="offset points", 
                            ha='center', va='bottom', color='white', fontsize=9, fontweight='bold')
        ax.set_title("Ingresos Totales por Mes", color='white', fontsize=16, pad=20)
        ax.tick_params(axis='both', colors='white')
        for spine in ax.spines.values(): spine.set_visible(False)
        self.canvas_grafica = FigureCanvasTkAgg(fig, master=self.contenedor_principal)
        self.canvas_grafica.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1100x750")
    VentanaIngresos(root).pack(fill="both", expand=True)
    root.mainloop()