import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class VentanaIngresos(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Variables de control
        self.pagina_actual = 1
        self.clientes_por_pagina = 10
        self.datos_brutos = [] # Datos de la DB
        self.datos_filtrados = [] # Datos con filtros aplicados

        # --- CABECERA ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(pady=(20, 10), padx=20, fill="x")
        ctk.CTkLabel(self.frame_top, text="REPORTE DE INGRESOS", font=("Arial", 28, "bold")).pack(side="left")

        # --- PANEL DE FILTROS ---
        self.frame_filtros = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_filtros.pack(pady=10, padx=20, fill="x")

        # Filtro por Plan
        ctk.CTkLabel(self.frame_filtros, text="Plan:", font=("Arial", 14)).pack(side="left", padx=5)
        self.combo_filtro_plan = ctk.CTkOptionMenu(self.frame_filtros, 
                                                   values=self.obtener_planes_db(),
                                                   command=lambda v: self.aplicar_filtros(),
                                                   width=160)
        self.combo_filtro_plan.pack(side="left", padx=10)
        self.combo_filtro_plan.set("Todos")

        # Buscador por texto
        self.entry_busqueda = ctk.CTkEntry(self.frame_filtros, placeholder_text="Buscar por nombre o apellido...", width=250, font=("Arial", 14))
        self.entry_busqueda.pack(side="left", padx=10)
        self.entry_busqueda.bind("<KeyRelease>", lambda e: self.aplicar_filtros())

        # --- TABLA ---
        self.frame_tabla = ctk.CTkFrame(self)
        self.frame_tabla.pack(pady=10, padx=20, fill="both", expand=True)
        self.crear_tabla()

        # --- RESUMEN TOTAL ---
        self.frame_total = ctk.CTkFrame(self, fg_color="#1a1a1a", height=50)
        self.frame_total.pack(pady=5, padx=20, fill="x")
        self.label_total_dinero = ctk.CTkLabel(self.frame_total, text="TOTAL INGRESOS: $0.00", font=("Arial", 18, "bold"), text_color="#2ecc71")
        self.label_total_dinero.pack(side="right", padx=20, pady=10)

        # --- PAGINACIÓN ---
        self.frame_paginacion = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_paginacion.pack(pady=10)
        self.btn_prev = ctk.CTkButton(self.frame_paginacion, text="Anterior", width=100, command=self.pagina_anterior)
        self.btn_prev.grid(row=0, column=0, padx=10)
        self.label_paginas = ctk.CTkLabel(self.frame_paginacion, text="Página 1 de 1", font=("Arial", 14))
        self.label_paginas.grid(row=0, column=1, padx=20)
        self.btn_next = ctk.CTkButton(self.frame_paginacion, text="Siguiente", width=100, command=self.pagina_siguiente)
        self.btn_next.grid(row=0, column=2, padx=10)

        self.cargar_datos_db()

    def obtener_planes_db(self):
        planes = ["Todos"]
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre_plan FROM planes")
                for fila in cursor.fetchall(): planes.append(fila[0])
        except: pass
        return planes

    def crear_tabla(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=40, font=("Arial", 14))
        style.configure("Treeview.Heading", font=("Arial", 15, "bold"), background="#333", foreground="white")
        
        self.tabla = ttk.Treeview(self.frame_tabla, columns=("Nro", "Fecha", "Nombre", "Apellido", "Plan", "Ingreso"), show="headings")
        
        columnas = [("Nro", 60), ("Fecha", 130), ("Nombre", 180), ("Apellido", 180), ("Plan", 180), ("Ingreso", 130)]
        for col, ancho in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")

        self.tabla.pack(side="left", fill="both", expand=True)
        scrolly = ttk.Scrollbar(self.frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrolly.set)
        scrolly.pack(side="right", fill="y")

    def cargar_datos_db(self):
        """Obtiene clientes con pago realizado y une con el precio del plan"""
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                # Unimos clientes con planes para obtener el precio actual del plan
                query = """
                    SELECT c.fecha_inscripcion, c.nombre, c.apellido, c.plan_seleccionado, p.precio
                    FROM clientes c
                    INNER JOIN planes p ON c.plan_seleccionado = p.nombre_plan
                    WHERE c.pago = 'Realizado'
                """
                cursor.execute(query)
                self.datos_brutos = cursor.fetchall()
            self.aplicar_filtros()
        except Exception as e:
            print(f"Error cargando ingresos: {e}")

    def aplicar_filtros(self):
        texto = self.entry_busqueda.get().lower()
        plan_filtro = self.combo_filtro_plan.get()

        self.datos_filtrados = []
        suma_total = 0.0

        for reg in self.datos_brutos:
            f_ins, nom, ape, plan, precio = reg
            
            match_texto = texto in nom.lower() or texto in ape.lower()
            match_plan = (plan_filtro == "Todos" or plan_filtro == plan)

            if match_texto and match_plan:
                self.datos_filtrados.append(reg)
                suma_total += float(precio)

        self.label_total_dinero.configure(text=f"TOTAL INGRESOS: ${suma_total:,.2f}")
        self.pagina_actual = 1
        self.actualizar_tabla()

    def actualizar_tabla(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)

        inicio = (self.pagina_actual - 1) * self.clientes_por_pagina
        fin = inicio + self.clientes_por_pagina
        datos_pagina = self.datos_filtrados[inicio:fin]

        for i, (f_ins, nom, ape, plan, precio) in enumerate(datos_pagina, start=inicio + 1):
            # Formatear fecha para visualización
            try:
                f_vis = datetime.strptime(f_ins, "%Y-%m-%d").strftime("%d-%m-%Y")
            except:
                f_vis = f_ins

            self.tabla.insert("", "end", values=(i, f_vis, nom, ape, plan, f"${precio:,.2f}"))

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

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Sistema Gym - Control de Ingresos")
    root.geometry("1100x750")
    ctk.set_appearance_mode("dark")
    VentanaIngresos(root).pack(fill="both", expand=True)
    root.mainloop()