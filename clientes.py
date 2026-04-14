import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3

from ver_ficha import VerFicha
from ver_membresia import VerMembresia

# CAMBIO: Ahora hereda de ctk.CTkFrame para ser compatible con el dashboard
class VentanaClientes(ctk.CTkFrame):
    def __init__(self, parent):
        # CAMBIO: Inicialización como Frame recibiendo al padre
        super().__init__(parent, fg_color="transparent")

        # Eliminamos title() y geometry() ya que ahora es un panel interno
        
        # Variables de paginación y datos
        self.pagina_actual = 1
        self.clientes_por_pagina = 10
        self.datos_completos_db = [] 
        self.datos_totales = []      

        # --- CABECERA Y BUSCADOR ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(self.frame_top, text="CLIENTES", font=("Arial", 24, "bold")).pack(side="left", padx=10)

        # --- CONTENEDOR DE FILTROS ---
        self.frame_filtros = ctk.CTkFrame(self.frame_top, fg_color="transparent")
        self.frame_filtros.pack(side="right")

        ctk.CTkLabel(self.frame_filtros, text="Plan:", font=("Arial", 14)).pack(side="left", padx=5)
        self.combo_filtro_plan = ctk.CTkOptionMenu(self.frame_filtros, 
                                                   values=self.obtener_planes_db(),
                                                   command=lambda v: self.buscar_cliente(),
                                                   width=160)
        self.combo_filtro_plan.pack(side="left", padx=10)
        self.combo_filtro_plan.set("Todos")

        self.entry_busqueda = ctk.CTkEntry(self.frame_filtros, placeholder_text="Buscar por nombre o apellido...", width=250)
        self.entry_busqueda.pack(side="left", padx=10)
        self.entry_busqueda.bind("<KeyRelease>", self.buscar_cliente)

        # --- CONTENEDOR DE TABLA ---
        self.frame_tabla = ctk.CTkFrame(self)
        self.frame_tabla.pack(pady=10, padx=20, fill="both", expand=True)

        self.crear_tabla_visual()

        # --- PANEL DE ACCIONES ---
        self.frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones.pack(pady=10)

        self.btn_ficha = ctk.CTkButton(self.frame_acciones, text="Ver Ficha", fg_color="#3498db", command=self.ir_a_ficha)
        self.btn_ficha.grid(row=0, column=0, padx=10)

        self.btn_membresia = ctk.CTkButton(self.frame_acciones, text="Ver Membresía", fg_color="#2ecc71", command=self.ir_a_membresia)
        self.btn_membresia.grid(row=0, column=1, padx=10)

        self.btn_rutina = ctk.CTkButton(self.frame_acciones, text="Ver Rutinas", fg_color="#f1c40f", text_color="black", command=self.ir_a_rutinas)
        self.btn_rutina.grid(row=0, column=2, padx=10)

        # --- PAGINACIÓN ---
        self.frame_paginacion = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_paginacion.pack(pady=20)

        self.btn_prev = ctk.CTkButton(self.frame_paginacion, text="Anterior", width=80, command=self.pagina_anterior)
        self.btn_prev.grid(row=0, column=0, padx=10)

        self.label_paginas = ctk.CTkLabel(self.frame_paginacion, text="Página 1 de 1")
        self.label_paginas.grid(row=0, column=1, padx=20)

        self.btn_next = ctk.CTkButton(self.frame_paginacion, text="Siguiente", width=80, command=self.pagina_siguiente)
        self.btn_next.grid(row=0, column=2, padx=10)

        self.cargar_datos_db()

    def obtener_planes_db(self):
        planes = ["Todos"]
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre_plan FROM planes")
                for fila in cursor.fetchall():
                    planes.append(fila[0])
        except:
            pass
        return planes

    def crear_tabla_visual(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b", 
                        rowheight=40, 
                        font=("Arial", 14)) 
        
        style.configure("Treeview.Heading", 
                        font=("Arial", 15, "bold"), 
                        background="#333", 
                        foreground="white")
        
        style.map("Treeview", background=[('selected', '#1f538d')])

        self.tabla = ttk.Treeview(self.frame_tabla, columns=("Numero", "Nombre", "Apellido", "Plan", "ID_REAL"), show="headings")
        
        self.tabla.heading("Numero", text="Nro.")
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("Apellido", text="Apellido")
        self.tabla.heading("Plan", text="Plan Seleccionado")
        
        self.tabla.column("Numero", width=60, anchor="center")
        self.tabla.column("Nombre", width=200, anchor="w")
        self.tabla.column("Apellido", width=200, anchor="w")
        self.tabla.column("Plan", width=250, anchor="center")
        self.tabla.column("ID_REAL", width=0, stretch=False) 

        self.tabla.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def cargar_datos_db(self):
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre, apellido, plan_seleccionado, id FROM clientes")
                self.datos_completos_db = cursor.fetchall()
            self.buscar_cliente()
        except Exception as e:
            print(f"Error cargando datos: {e}")

    def actualizar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        inicio = (self.pagina_actual - 1) * self.clientes_por_pagina
        fin = inicio + self.clientes_por_pagina
        datos_pagina = self.datos_totales[inicio:fin]

        for i, (nombre, apellido, plan, real_id) in enumerate(datos_pagina, start=inicio + 1):
            self.tabla.insert("", "end", values=(i, nombre, apellido, plan, real_id))

        total_paginas = max(1, (len(self.datos_totales) + self.clientes_por_pagina - 1) // self.clientes_por_pagina)
        self.label_paginas.configure(text=f"Página {self.pagina_actual} de {total_paginas}")

    def buscar_cliente(self, event=None):
        termino = self.entry_busqueda.get().lower()
        plan_filtro = self.combo_filtro_plan.get()
        
        self.datos_totales = []
        
        for cli in self.datos_completos_db:
            nombre_completo = f"{cli[0]} {cli[1]}".lower()
            plan_cliente = str(cli[2])
            
            match_texto = termino in nombre_completo
            match_plan = (plan_filtro == "Todos" or plan_filtro == plan_cliente)
            
            if match_texto and match_plan:
                self.datos_totales.append(cli)
                
        self.pagina_actual = 1
        self.actualizar_tabla()

    def pagina_siguiente(self):
        total_paginas = (len(self.datos_totales) + self.clientes_por_pagina - 1) // self.clientes_por_pagina
        if self.pagina_actual < total_paginas:
            self.pagina_actual += 1
            self.actualizar_tabla()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_tabla()

    def obtener_seleccion(self):
        item = self.tabla.selection()
        if not item:
            messagebox.showwarning("Atención", "Por favor, seleccione un cliente de la tabla.")
            return None
        return self.tabla.item(item)['values']

    def ir_a_ficha(self):
        seleccion = self.obtener_seleccion()
        if seleccion:
            id_cliente = seleccion[4]
            # Ocultamos el listado
            self.frame_top.pack_forget()
            self.frame_tabla.pack_forget()
            self.frame_acciones.pack_forget()
            self.frame_paginacion.pack_forget()
                
            self.vista_ficha = VerFicha(self, id_cliente, callback_volver=self.regresar_a_lista)
            self.vista_ficha.pack(fill="both", expand=True)

    def regresar_a_lista(self):
        if hasattr(self, 'vista_ficha'):
            self.vista_ficha.destroy()
        self.mostrar_elementos_lista()
        self.cargar_datos_db() 

    def ir_a_membresia(self):
        seleccion = self.obtener_seleccion()
        if seleccion:
            id_cliente = seleccion[4]
            self.frame_top.pack_forget()
            self.frame_tabla.pack_forget()
            self.frame_acciones.pack_forget()
            self.frame_paginacion.pack_forget()
            
            self.vista_membresia = VerMembresia(self, id_cliente, callback_volver=self.regresar_a_lista_desde_membresia)
            self.vista_membresia.pack(fill="both", expand=True)

    def regresar_a_lista_desde_membresia(self):
        if hasattr(self, 'vista_membresia'):
            self.vista_membresia.destroy()
        self.mostrar_elementos_lista()
        self.cargar_datos_db()

    def ir_a_rutinas(self):
        seleccion = self.obtener_seleccion()
        if seleccion:
            id_cliente_seleccionado = seleccion[4]
            self.frame_top.pack_forget()
            self.frame_tabla.pack_forget()
            self.frame_acciones.pack_forget()
            self.frame_paginacion.pack_forget()
            
            from ver_rutinas import VerRutinas
            
            self.frame_rutinas_container = ctk.CTkFrame(self, fg_color="transparent")
            self.frame_rutinas_container.pack(fill="both", expand=True)
            
            header = ctk.CTkFrame(self.frame_rutinas_container, fg_color="transparent")
            header.pack(fill="x", padx=20, pady=10)
            ctk.CTkButton(header, text="← VOLVER AL LISTADO", width=150, 
                          command=self.regresar_de_rutinas).pack(side="left")

            self.vista_rutinas = VerRutinas(self.frame_rutinas_container, id_cliente=id_cliente_seleccionado)
            self.vista_rutinas.pack(fill="both", expand=True)
        else:
            messagebox.showwarning("Atención", "Por favor, seleccione un cliente de la tabla primero.")
        
    def regresar_de_rutinas(self):
        if hasattr(self, 'frame_rutinas_container'):
            self.frame_rutinas_container.destroy()
        self.mostrar_elementos_lista()
        self.cargar_datos_db()

    def mostrar_elementos_lista(self):
        """Reutilizable para volver a mostrar los componentes de la tabla"""
        self.frame_top.pack(pady=20, padx=20, fill="x")
        self.frame_tabla.pack(pady=10, padx=20, fill="both", expand=True)
        self.frame_acciones.pack(pady=10)
        self.frame_paginacion.pack(pady=20)

if __name__ == "__main__":
    # Para pruebas independientes
    root = ctk.CTk()
    app = VentanaClientes(root)
    app.pack(fill="both", expand=True)
    root.mainloop()