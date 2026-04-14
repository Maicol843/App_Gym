import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from database import crear_base_de_datos 

class VentanaIngresos(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        crear_base_de_datos()
        
        self.pagina_actual = 1
        self.clientes_por_pagina = 10
        self.datos_brutos = [] 
        self.datos_filtrados = [] 

        # --- CABECERA (Botón eliminado) ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(pady=(20, 10), padx=20, fill="x")
        ctk.CTkLabel(self.frame_top, text="REPORTE DE INGRESOS", font=("Arial", 28, "bold")).pack(side="left")

        # --- PANEL DE FILTROS ---
        self.frame_filtros = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_filtros.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.frame_filtros, text="Plan:", font=("Arial", 14)).pack(side="left", padx=5)
        self.combo_filtro_plan = ctk.CTkOptionMenu(self.frame_filtros, 
                                                   values=self.obtener_planes_db(),
                                                   command=lambda v: self.aplicar_filtros(),
                                                   width=160)
        self.combo_filtro_plan.pack(side="left", padx=10)
        self.combo_filtro_plan.set("Todos")

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

        # Ejecutamos la carga y el procesado automático
        self.cargar_y_procesar_ingresos()

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
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=40, font=("Arial", 12))
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background="#333", foreground="white")
        
        self.tabla = ttk.Treeview(self.frame_tabla, columns=("Nro", "Fecha", "Nombre", "Apellido", "Plan", "Ingreso"), show="headings")
        
        columnas = [("Nro", 50), ("Fecha", 110), ("Nombre", 150), ("Apellido", 150), ("Plan", 150), ("Ingreso", 110)]
        for col, ancho in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")

        self.tabla.pack(side="left", fill="both", expand=True)
        scrolly = ttk.Scrollbar(self.frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrolly.set)
        scrolly.pack(side="right", fill="y")

    def cargar_y_procesar_ingresos(self):
        """
        Busca clientes con pago 'Realizado' que NO estén aún en la tabla de ingresos
        y los registra automáticamente.
        """
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                
                # 1. Buscar clientes marcados como 'Realizado'
                query_pendientes = """
                    SELECT c.id, c.nombre, c.apellido, c.plan_seleccionado, p.precio, c.fecha_inscripcion
                    FROM clientes c
                    INNER JOIN planes p ON c.plan_seleccionado = p.nombre_plan
                    WHERE c.pago = 'Realizado'
                """
                cursor.execute(query_pendientes)
                pendientes = cursor.fetchall()

                fecha_hoy = datetime.now().strftime("%Y-%m-%d")

                for cli in pendientes:
                    id_db, nom, ape, plan, precio, f_ins = cli
                    
                    # Verificamos si ya existe ese registro en ingresos para este cliente hoy
                    # (Esto evita duplicados si abres la ventana varias veces al día)
                    cursor.execute("SELECT id FROM ingresos WHERE id_cliente = ? AND fecha = ?", (id_db, fecha_hoy))
                    existe = cursor.fetchone()

                    if not existe:
                        # Insertar en ingresos
                        cursor.execute("""
                            INSERT INTO ingresos (id_cliente, monto, fecha, detalle) 
                            VALUES (?, ?, ?, ?)
                        """, (id_db, precio, fecha_hoy, f"Mensualidad: {plan}"))
                        
                        # Actualizamos el estado a 'SÍ' para saber que ya fue procesado por el sistema
                        cursor.execute("UPDATE clientes SET pago = 'SÍ' WHERE id = ?", (id_db,))
                
                conn.commit()

                # 2. Ahora cargamos los datos brutos para la visualización de la tabla (Histórico)
                query_historico = """
                    SELECT i.fecha, c.nombre, c.apellido, c.plan_seleccionado, i.monto
                    FROM ingresos i
                    INNER JOIN clientes c ON i.id_cliente = c.id
                """
                cursor.execute(query_historico)
                self.datos_brutos = cursor.fetchall()

            self.aplicar_filtros()
        except Exception as e:
            print(f"Error en procesado automático: {e}")

    def aplicar_filtros(self):
        texto = self.entry_busqueda.get().lower()
        plan_filtro = self.combo_filtro_plan.get()

        self.datos_filtrados = []
        suma_total = 0.0

        for reg in self.datos_brutos:
            fecha, nom, ape, plan, monto = reg
            
            match_texto = texto in nom.lower() or texto in ape.lower()
            match_plan = (plan_filtro == "Todos" or plan_filtro == plan)

            if match_texto and match_plan:
                self.datos_filtrados.append(reg)
                suma_total += float(monto)

        self.label_total_dinero.configure(text=f"TOTAL INGRESOS: ${suma_total:,.2f}")
        self.pagina_actual = 1
        self.actualizar_tabla()

    def actualizar_tabla(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)

        inicio = (self.pagina_actual - 1) * self.clientes_por_pagina
        fin = inicio + self.clientes_por_pagina
        datos_pagina = self.datos_filtrados[inicio:fin]

        for i, (fecha, nom, ape, plan, monto) in enumerate(datos_pagina, start=inicio + 1):
            try:
                f_vis = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d-%m-%Y")
            except:
                f_vis = fecha

            self.tabla.insert("", "end", values=(i, f_vis, nom, ape, plan, f"${monto:,.2f}"))

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
    root.title("Sistema Gym - Control de Ingresos Automático")
    root.geometry("1100x750")
    ctk.set_appearance_mode("dark")
    VentanaIngresos(root).pack(fill="both", expand=True)
    root.mainloop()