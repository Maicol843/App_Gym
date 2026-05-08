import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3

from ver_ficha import VerFicha
from ver_membresia import VerMembresia

class VentanaClientes(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        # Variables de datos
        self.pagina_actual = 1
        self.clientes_por_pagina = 10
        self.datos_completos_db = [] 
        self.datos_totales = []      

        # Contenedor con scroll solo para la lista
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True)

        self.setup_interfaz_lista()
        self.cargar_datos_db()

    def setup_interfaz_lista(self):
        # --- CABECERA ---
        self.frame_top = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.frame_top.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(self.frame_top, text="CLIENTES", font=("Arial", 24, "bold")).pack(side="left", padx=10)

        self.frame_filtros = ctk.CTkFrame(self.frame_top, fg_color="transparent")
        self.frame_filtros.pack(side="right")

        self.combo_filtro_plan = ctk.CTkOptionMenu(self.frame_filtros, 
                                                   values=self.obtener_planes_db(),
                                                   command=lambda v: self.buscar_cliente())
        self.combo_filtro_plan.pack(side="left", padx=10)
        self.combo_filtro_plan.set("Todos")

        self.entry_busqueda = ctk.CTkEntry(self.frame_filtros, placeholder_text="Buscar por nombre o apellido...", width=250)
        self.entry_busqueda.pack(side="left", padx=10)
        self.entry_busqueda.bind("<KeyRelease>", self.buscar_cliente)

        # --- TABLA ---
        self.frame_tabla = ctk.CTkFrame(self.scroll_container)
        self.frame_tabla.pack(pady=10, padx=20, fill="x")

        self.tabla = ttk.Treeview(self.frame_tabla, columns=("Numero", "Nombre", "Apellido", "Plan", "ID_REAL"), show="headings", height=10)
        
        # Configuración de encabezados
        self.tabla.heading("Numero", text="Nro.", anchor="center") # Centrar encabezado
        self.tabla.heading("Nombre", text="Nombre", anchor="w")
        self.tabla.heading("Apellido", text="Apellido", anchor="w")
        self.tabla.heading("Plan", text="Plan", anchor="center")
        
        # CONFIGURACIÓN DE COLUMNAS (Aquí se centra el contenido)
        self.tabla.column("Numero", width=60, anchor="center") # <--- SOLUCIÓN: Centrado de celdas Nro.
        self.tabla.column("Nombre", width=200, anchor="w")
        self.tabla.column("Apellido", width=200, anchor="w")
        self.tabla.column("Plan", width=250, anchor="center")
        self.tabla.column("ID_REAL", width=0, stretch=False) 

        self.tabla.pack(fill="x")

        # --- PANEL DE ACCIONES ---
        self.frame_acciones = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.frame_acciones.pack(pady=10)

        ctk.CTkButton(self.frame_acciones, text="Ver Ficha", fg_color="#0d6efd", command=self.ir_a_ficha).grid(row=0, column=0, padx=10)
        ctk.CTkButton(self.frame_acciones, text="Ver Membresía", fg_color="#198754", command=self.ir_a_membresia).grid(row=0, column=1, padx=10)
        ctk.CTkButton(self.frame_acciones, text="Ver Rutinas", fg_color="#f1c40f", text_color="black", command=self.ir_a_rutinas).grid(row=0, column=2, padx=10)

        # --- PAGINACIÓN ---
        self.frame_paginacion = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.frame_paginacion.pack(pady=20)

        self.btn_prev = ctk.CTkButton(self.frame_paginacion, text="Anterior", width=80, command=self.pagina_anterior)
        self.btn_prev.grid(row=0, column=0, padx=10)
        self.label_paginas = ctk.CTkLabel(self.frame_paginacion, text="Página 1 de 1")
        self.label_paginas.grid(row=0, column=1, padx=20)
        self.btn_next = ctk.CTkButton(self.frame_paginacion, text="Siguiente", width=80, command=self.pagina_siguiente)
        self.btn_next.grid(row=0, column=2, padx=10)

    def ir_a_ficha(self):
        sel = self.obtener_seleccion()
        if sel:
            self.scroll_container.pack_forget() 
            self.vista_detalle = VerFicha(self, sel[4], callback_volver=self.regresar_a_lista)
            self.vista_detalle.pack(fill="both", expand=True)

    def ir_a_membresia(self):
        sel = self.obtener_seleccion()
        if sel:
            self.scroll_container.pack_forget()
            self.vista_detalle = VerMembresia(self, sel[4], callback_volver=self.regresar_a_lista)
            self.vista_detalle.pack(fill="both", expand=True)

    def ir_a_rutinas(self):
        sel = self.obtener_seleccion()
        if sel:
            from ver_rutinas import VerRutinas
            self.scroll_container.pack_forget()
            self.vista_detalle = ctk.CTkFrame(self, fg_color="transparent")
            self.vista_detalle.pack(fill="both", expand=True)
            ctk.CTkButton(self.vista_detalle, text="← Volver", command=self.regresar_a_lista).pack(pady=10, padx=20, anchor="nw")
            rutinas = VerRutinas(self.vista_detalle, id_cliente=sel[4])
            rutinas.pack(fill="both", expand=True)

    def regresar_a_lista(self):
        if hasattr(self, 'vista_detalle'):
            self.vista_detalle.destroy()
        self.scroll_container.pack(fill="both", expand=True)
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

    def cargar_datos_db(self):
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                query = '''SELECT c.nombre, c.apellido, p.plan_seleccionado, c.id FROM clientes c
                           LEFT JOIN plan_elegido p ON p.id = (SELECT id FROM plan_elegido WHERE id_cliente = c.id ORDER BY id DESC LIMIT 1)'''
                cursor.execute(query)
                self.datos_completos_db = cursor.fetchall()
            self.buscar_cliente()
        except Exception as e: print(e)

    def actualizar_tabla(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        ini = (self.pagina_actual - 1) * self.clientes_por_pagina
        for i, d in enumerate(self.datos_totales[ini:ini+self.clientes_por_pagina], start=ini+1):
            self.tabla.insert("", "end", values=(i, d[0], d[1], d[2] if d[2] else "Sin Plan", d[3]))
        tp = max(1, (len(self.datos_totales) + self.clientes_por_pagina - 1) // self.clientes_por_pagina)
        self.label_paginas.configure(text=f"Página {self.pagina_actual} de {tp}")

    def buscar_cliente(self, event=None):
        t = self.entry_busqueda.get().lower()
        f = self.combo_filtro_plan.get()
        self.datos_totales = [c for c in self.datos_completos_db if t in f"{c[0]} {c[1]}".lower() and (f == "Todos" or f == str(c[2]))]
        self.pagina_actual = 1
        self.actualizar_tabla()

    def pagina_siguiente(self):
        tp = (len(self.datos_totales) + self.clientes_por_pagina - 1) // self.clientes_por_pagina
        if self.pagina_actual < tp:
            self.pagina_actual += 1
            self.actualizar_tabla()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_tabla()

    def obtener_seleccion(self):
        item = self.tabla.selection()
        if not item:
            messagebox.showwarning("Atención", "Seleccione un cliente")
            return None
        return self.tabla.item(item)['values']