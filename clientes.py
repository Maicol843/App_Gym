import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3

from ver_ficha import VerFicha
from ver_membresia import VerMembresia

class VentanaClientes(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema Gym - Gestión de Clientes")
        self.geometry("1200x800") # Aumentado ligeramente para el nuevo filtro
        ctk.set_appearance_mode("dark")

        # Variables de paginación y datos
        self.pagina_actual = 1
        self.clientes_por_pagina = 10
        self.datos_completos_db = [] # Almacena la carga total para filtrar en memoria
        self.datos_totales = []      # Almacena los datos que se muestran (filtrados o no)

        # --- CABECERA Y BUSCADOR ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(self.frame_top, text="LISTADO DE CLIENTES", font=("Arial", 24, "bold")).pack(side="left", padx=10)

        # --- CONTENEDOR DE FILTROS (Lado derecho) ---
        self.frame_filtros = ctk.CTkFrame(self.frame_top, fg_color="transparent")
        self.frame_filtros.pack(side="right")

        # Select para buscar por Plan
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

        # --- PANEL DE ACCIONES (Botones debajo de la tabla) ---
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

        # Carga inicial
        self.cargar_datos_db()

    def obtener_planes_db(self):
        """Busca los nombres de los planes en la base de datos para el OptionMenu"""
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
        
        # --- CAMBIO: FUENTE MÁS GRANDE ---
        # Contenido de la tabla (font size 14) y altura de fila (rowheight 40)
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b", 
                        rowheight=40, 
                        font=("Arial", 14)) 
        
        # Cabeceras de la tabla (font size 15)
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
        self.tabla.column("ID_REAL", width=0, stretch=False) # ID oculto para consultas

        self.tabla.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def cargar_datos_db(self):
        """Obtiene todos los clientes de la base de datos"""
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre, apellido, plan_seleccionado, id FROM clientes")
                self.datos_completos_db = cursor.fetchall()
            self.buscar_cliente() # Llama a buscar_cliente para inicializar la lista con los filtros
        except Exception as e:
            print(f"Error cargando datos: {e}")

    def actualizar_tabla(self):
        """Maneja la paginación y muestra los datos en la tabla"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        # Calcular rangos
        inicio = (self.pagina_actual - 1) * self.clientes_por_pagina
        fin = inicio + self.clientes_por_pagina
        datos_pagina = self.datos_totales[inicio:fin]

        # Insertar datos con número correlativo
        for i, (nombre, apellido, plan, real_id) in enumerate(datos_pagina, start=inicio + 1):
            self.tabla.insert("", "end", values=(i, nombre, apellido, plan, real_id))

        # Actualizar etiquetas de página
        total_paginas = max(1, (len(self.datos_totales) + self.clientes_por_pagina - 1) // self.clientes_por_pagina)
        self.label_paginas.configure(text=f"Página {self.pagina_actual} de {total_paginas}")

    def buscar_cliente(self, event=None):
        """Filtra los datos por nombre/apellido y por plan seleccionado"""
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

    # --- LÓGICA DE NAVEGACIÓN ---
    def pagina_siguiente(self):
        total_paginas = (len(self.datos_totales) + self.clientes_por_pagina - 1) // self.clientes_por_pagina
        if self.pagina_actual < total_paginas:
            self.pagina_actual += 1
            self.actualizar_tabla()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_tabla()

    # --- FUNCIONES PARA LOS BOTONES DE ACCIÓN ---
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
            
            # 1. Limpiamos todo el contenido actual de la ventana
            for widget in self.winfo_children():
                widget.pack_forget() 
                
            # 2. Cargamos el frame de VerFicha en el MISMO lugar
            self.vista_ficha = VerFicha(self, id_cliente, callback_volver=self.regresar_a_lista)
            self.vista_ficha.pack(fill="both", expand=True)

    def regresar_a_lista(self):
        # Destruye la vista de ficha y vuelve a mostrar los widgets de la tabla
        self.vista_ficha.destroy()
        self.frame_top.pack(pady=20, padx=20, fill="x")
        self.frame_tabla.pack(pady=10, padx=20, fill="both", expand=True)
        self.frame_acciones.pack(pady=10)
        self.frame_paginacion.pack(pady=20)
        self.cargar_datos_db() # Refresca por si hubo cambios

    def ir_a_membresia(self):
        seleccion = self.obtener_seleccion()
        if seleccion:
            id_cliente = seleccion[4]
            
            # Ocultamos la tabla y buscador
            self.frame_top.pack_forget()
            self.frame_tabla.pack_forget()
            self.frame_acciones.pack_forget()
            self.frame_paginacion.pack_forget()
            
            # Mostramos la vista de membresía
            self.vista_membresia = VerMembresia(self, id_cliente, callback_volver=self.regresar_a_lista_desde_membresia)
            self.vista_membresia.pack(fill="both", expand=True)

    def regresar_a_lista_desde_membresia(self):
        self.vista_membresia.destroy()
        # Volvemos a mostrar todo lo anterior
        self.frame_top.pack(pady=20, padx=20, fill="x")
        self.frame_tabla.pack(pady=10, padx=20, fill="both", expand=True)
        self.frame_acciones.pack(pady=10)
        self.frame_paginacion.pack(pady=20)
        self.cargar_datos_db()

    def ir_a_rutinas(self):
        # 1. Obtenemos el cliente seleccionado de la tabla
        seleccion = self.obtener_seleccion()
        
        if seleccion:
            # 2. Extraemos el ID (el índice 4 es donde está el ID oculto en tu tabla)
            id_cliente_seleccionado = seleccion[4]
            
            # 3. Ocultamos los componentes del listado
            self.frame_top.pack_forget()
            self.frame_tabla.pack_forget()
            self.frame_acciones.pack_forget()
            self.frame_paginacion.pack_forget()
            
            # Importación local para evitar errores circulares
            from ver_rutinas import VerRutinas
            
            # 4. Creamos el contenedor
            self.frame_rutinas_container = ctk.CTkFrame(self, fg_color="transparent")
            self.frame_rutinas_container.pack(fill="both", expand=True)
            
            header = ctk.CTkFrame(self.frame_rutinas_container, fg_color="transparent")
            header.pack(fill="x", padx=20, pady=10)
            ctk.CTkButton(header, text="← VOLVER AL LISTADO", width=150, 
                          command=self.regresar_de_rutinas).pack(side="left")

            # --- LA SOLUCIÓN ESTÁ AQUÍ ---
            # Ahora le pasamos el ID que extrajimos arriba
            self.vista_rutinas = VerRutinas(self.frame_rutinas_container, id_cliente=id_cliente_seleccionado)
            self.vista_rutinas.pack(fill="both", expand=True)
        else:
            messagebox.showwarning("Atención", "Por favor, seleccione un cliente de la tabla primero.")
        
    def regresar_de_rutinas(self):
        if hasattr(self, 'frame_rutinas_container'):
            self.frame_rutinas_container.destroy()
            
        # Volvemos a mostrar la lista original
        self.frame_top.pack(pady=20, padx=20, fill="x")
        self.frame_tabla.pack(pady=10, padx=20, fill="both", expand=True)
        self.frame_acciones.pack(pady=10)
        self.frame_paginacion.pack(pady=20)
        self.cargar_datos_db()
if __name__ == "__main__":
    app = VentanaClientes()
    app.mainloop()