import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class GestionMembresia(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Variables de control originales
        self.pagina_actual = 1
        self.clientes_por_pagina = 10
        self.datos_completos_db = [] 
        self.datos_totales = []      

        # Agregamos el contenedor con scroll para que se vea la paginación
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True)

        self.setup_interfaz()
        self.cargar_datos_membresia()

    def setup_interfaz(self):
        # Todo se empaqueta en self.scroll_container
        # --- CABECERA ---
        self.frame_top = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.frame_top.pack(pady=(20, 10), padx=20, fill="x")
        ctk.CTkLabel(self.frame_top, text="MEMBRESÍAS", font=("Arial", 28, "bold")).pack(side="left")

        # --- PANEL DE FILTROS ---
        self.frame_filtros = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.frame_filtros.pack(pady=10, padx=20, fill="x")

        self.entry_busqueda = ctk.CTkEntry(self.frame_filtros, placeholder_text="Buscar por nombre o apellido...", width=300, font=("Arial", 14))
        self.entry_busqueda.pack(side="left", padx=(0, 10))
        self.entry_busqueda.bind("<KeyRelease>", self.filtrar_datos)

        self.combo_estado = ctk.CTkOptionMenu(self.frame_filtros, values=["Todos", "Activos", "Vencidos", "Por Vencer"], command=lambda v: self.filtrar_datos())
        self.combo_estado.pack(side="left")
        self.combo_estado.set("Todos")

        # --- TABLA ---
        self.frame_tabla = ctk.CTkFrame(self.scroll_container)
        self.frame_tabla.pack(pady=10, padx=20, fill="x")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0, font=("Arial", 11), rowheight=30)
        style.map("Treeview", background=[('selected', '#3b8ed0')])
        style.configure("Treeview.Heading", background="#1f1f1f", foreground="white", font=("Arial", 12, "bold"))

        self.tabla = ttk.Treeview(self.frame_tabla, columns=("Nro", "Nombre", "Apellido", "Plan", "Vencimiento", "Estado", "Pago"), show="headings", height=10)
        
        self.tabla.heading("Nro", text="Nro.", anchor="center")
        self.tabla.heading("Nombre", text="Nombre", anchor="w")
        self.tabla.heading("Apellido", text="Apellido", anchor="w")
        self.tabla.heading("Plan", text="Plan", anchor="center")
        self.tabla.heading("Vencimiento", text="Vencimiento", anchor="center")
        self.tabla.heading("Estado", text="Estado", anchor="center")
        self.tabla.heading("Pago", text="Pago", anchor="center")

        self.tabla.column("Nro", width=50, anchor="center")
        self.tabla.column("Nombre", width=150, anchor="w")
        self.tabla.column("Apellido", width=150, anchor="w")
        self.tabla.column("Plan", width=150, anchor="center")
        self.tabla.column("Vencimiento", width=120, anchor="center")
        self.tabla.column("Estado", width=120, anchor="center")
        self.tabla.column("Pago", width=100, anchor="center")

        self.tabla.pack(fill="x")

        self.tabla.tag_configure('activo', foreground='#2ecc71')
        self.tabla.tag_configure('vencido', foreground='#e74c3c')
        self.tabla.tag_configure('por_vencer', foreground='#f1c40f')

        # --- PAGINACIÓN ---
        self.frame_paginacion = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.frame_paginacion.pack(pady=20)

        self.btn_prev = ctk.CTkButton(self.frame_paginacion, text="Anterior", width=100, command=self.pagina_anterior)
        self.btn_prev.grid(row=0, column=0, padx=10)

        self.label_paginas = ctk.CTkLabel(self.frame_paginacion, text="Página 1 de 1", font=("Arial", 14))
        self.label_paginas.grid(row=0, column=1, padx=20)

        self.btn_next = ctk.CTkButton(self.frame_paginacion, text="Siguiente", width=100, command=self.pagina_siguiente)
        self.btn_next.grid(row=0, column=2, padx=10)

    def cargar_datos_membresia(self):
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                query = """
                    SELECT c.nombre, c.apellido, p.plan_seleccionado, p.fecha_vencimiento, p.pago
                    FROM clientes c
                    LEFT JOIN plan_elegido p ON p.id = (
                        SELECT id FROM plan_elegido 
                        WHERE id_cliente = c.id 
                        ORDER BY id DESC LIMIT 1
                    )
                """
                cursor.execute(query)
                self.datos_completos_db = cursor.fetchall()
            self.filtrar_datos()
        except Exception as e:
            print(f"Error: {e}")

    def calcular_estados(self, fecha_ven_str):
        if not fecha_ven_str: return "Sin Plan", "vencido"
        try:
            formato = "%Y-%m-%d" if "-" in fecha_ven_str and fecha_ven_str.find("-") == 4 else "%d-%m-%Y"
            fecha_ven = datetime.strptime(fecha_ven_str, formato)
            hoy = datetime.now()
            dias_restantes = (fecha_ven - hoy).days
            if dias_restantes < 0: return "Vencido", "vencido"
            if dias_restantes <= 5: return "Por Vencer", "por_vencer"
            return "Activo", "activo"
        except: return "Error", "vencido"

    def filtrar_datos(self, event=None):
        busqueda = self.entry_busqueda.get().lower()
        filtro_estado = self.combo_estado.get() # "Activos", "Vencidos", etc.
        
        self.datos_totales = []
        for reg in self.datos_completos_db:
            nom, ape, plan, f_ven, pago = reg
            nombre_completo = f"{nom} {ape}".lower()
            est_mem, _ = self.calcular_estados(f_ven) # "Activo", "Vencido", etc.
            
            # Ajustamos la comparación para que coincida con los valores del selector
            match_estado = False
            if filtro_estado == "Todos":
                match_estado = True
            elif filtro_estado == "Activos" and est_mem == "Activo":
                match_estado = True
            elif filtro_estado == "Vencidos" and est_mem == "Vencido":
                match_estado = True
            elif filtro_estado == "Por Vencer" and est_mem == "Por Vencer":
                match_estado = True

            if busqueda in nombre_completo and match_estado:
                self.datos_totales.append(reg)
        
        self.pagina_actual = 1
        self.actualizar_tabla()

    def actualizar_tabla(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        inicio = (self.pagina_actual - 1) * self.clientes_por_pagina
        fin = inicio + self.clientes_por_pagina
        for i, reg in enumerate(self.datos_totales[inicio:fin], start=inicio + 1):
            nom, ape, plan, f_ven, pago_db = reg
            try:
                formato_orig = "%Y-%m-%d" if "-" in f_ven and f_ven.find("-") == 4 else "%d-%m-%Y"
                f_bonita = datetime.strptime(f_ven, formato_orig).strftime("%d-%m-%Y")
            except: f_bonita = f_ven
            est_mem, tag = self.calcular_estados(f_ven)
            self.tabla.insert("", "end", values=(i, nom, ape, plan, f_bonita, est_mem, pago_db), tags=(tag,))
        total_pag = max(1, (len(self.datos_totales) + self.clientes_por_pagina - 1) // self.clientes_por_pagina)
        self.label_paginas.configure(text=f"Página {self.pagina_actual} de {total_pag}")

    def pagina_siguiente(self):
        total_pag = (len(self.datos_totales) + self.clientes_por_pagina - 1) // self.clientes_por_pagina
        if self.pagina_actual < total_pag:
            self.pagina_actual += 1
            self.actualizar_tabla()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_tabla()