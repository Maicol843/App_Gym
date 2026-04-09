import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3

from ver_ficha import VerFicha
from ver_membresia import VerMembresia

class VentanaClientes(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema Gym - Gestión de Clientes")
        self.geometry("1100x700")
        ctk.set_appearance_mode("dark")

        # Variables de paginación y datos
        self.pagina_actual = 1
        self.clientes_por_pagina = 10
        self.datos_totales = []

        # --- CABECERA Y BUSCADOR ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(self.frame_top, text="LISTADO DE CLIENTES", font=("Arial", 24, "bold")).pack(side="left", padx=10)

        self.entry_busqueda = ctk.CTkEntry(self.frame_top, placeholder_text="Buscar por nombre o apellido...", width=300)
        self.entry_busqueda.pack(side="right", padx=10)
        self.entry_busqueda.bind("<KeyRelease>", self.buscar_cliente)

        # --- CONTENEDOR DE TABLA ---
        self.frame_tabla = ctk.CTkFrame(self)
        self.frame_tabla.pack(pady=10, padx=20, fill="both", expand=True)

        self.crear_tabla_visual()

        # --- PANEL DE ACCIONES (Botones debajo de la tabla) ---
        # Nota: En Treeview las acciones se suelen manejar seleccionando la fila y pulsando un botón general
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

    def crear_tabla_visual(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=35, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#333", foreground="white")
        style.map("Treeview", background=[('selected', '#1f538d')])

        self.tabla = ttk.Treeview(self.frame_tabla, columns=("Numero", "Nombre", "Apellido", "Plan", "ID_REAL"), show="headings")
        
        self.tabla.heading("Numero", text="N°")
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("Apellido", text="Apellido")
        self.tabla.heading("Plan", text="Plan Seleccionado")
        
        self.tabla.column("Numero", width=50, anchor="center")
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
                self.datos_totales = cursor.fetchall()
            self.actualizar_tabla()
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
        termino = self.entry_busqueda.get().lower()
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                # Busca por nombre o apellido
                cursor.execute("SELECT nombre, apellido, plan_seleccionado, id FROM clientes WHERE LOWER(nombre) LIKE ? OR LOWER(apellido) LIKE ?", 
                               (f'%{termino}%', f'%{termino}%'))
                self.datos_totales = cursor.fetchall()
            self.pagina_actual = 1
            self.actualizar_tabla()
        except Exception as e:
            print(f"Error en búsqueda: {e}")

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
                widget.pack_forget() # O widget.destroy()
                
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
        datos = self.obtener_seleccion()
        if datos:
            # Aquí abrirás la ventana Rutinas
            print(f"Abriendo rutinas del cliente ID: {datos[4]}")

if __name__ == "__main__":
    app = VentanaClientes()
    app.mainloop()