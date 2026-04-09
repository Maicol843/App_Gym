import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class GestionMembresia(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Variables de control
        self.pagina_actual = 1
        self.clientes_por_pagina = 10
        self.datos_completos_db = [] # Datos brutos de la base de datos
        self.datos_totales = []      # Datos después de aplicar filtros

        # --- CABECERA ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(pady=(20, 10), padx=20, fill="x")
        ctk.CTkLabel(self.frame_top, text="CONTROL DE MEMBRESÍAS", font=("Arial", 28, "bold")).pack(side="left")

        # --- PANEL DE FILTROS ---
        self.frame_filtros = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_filtros.pack(pady=10, padx=20, fill="x")

        # Buscador por texto (Nombre/Apellido)
        self.entry_busqueda = ctk.CTkEntry(self.frame_filtros, placeholder_text="Buscar cliente...", width=250, font=("Arial", 14))
        self.entry_busqueda.pack(side="left", padx=(0, 10))
        self.entry_busqueda.bind("<KeyRelease>", lambda e: self.buscar_socio())

        # Select para Estado de Membresía
        ctk.CTkLabel(self.frame_filtros, text="Estado:", font=("Arial", 14)).pack(side="left", padx=5)
        self.combo_filtro_estado = ctk.CTkOptionMenu(self.frame_filtros, 
                                                    values=["Todos", "Al día", "Por vencer", "Vencido"],
                                                    command=lambda v: self.buscar_socio(),
                                                    width=140)
        self.combo_filtro_estado.pack(side="left", padx=10)
        self.combo_filtro_estado.set("Todos")

        # Select para Estado de Pago
        ctk.CTkLabel(self.frame_filtros, text="Pago:", font=("Arial", 14)).pack(side="left", padx=5)
        self.combo_filtro_pago = ctk.CTkOptionMenu(self.frame_filtros, 
                                                  values=["Todos", "Realizado", "Pendiente", "No Pago"],
                                                  command=lambda v: self.buscar_socio(),
                                                  width=140)
        self.combo_filtro_pago.pack(side="left", padx=10)
        self.combo_filtro_pago.set("Todos")

        # --- TABLA ---
        self.frame_tabla = ctk.CTkFrame(self)
        self.frame_tabla.pack(pady=10, padx=20, fill="both", expand=True)
        self.crear_tabla()

        # --- PAGINACIÓN ---
        self.frame_paginacion = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_paginacion.pack(pady=20)
        self.btn_prev = ctk.CTkButton(self.frame_paginacion, text="Anterior", width=100, command=self.pagina_anterior)
        self.btn_prev.grid(row=0, column=0, padx=10)
        self.label_paginas = ctk.CTkLabel(self.frame_paginacion, text="Página 1 de 1", font=("Arial", 14))
        self.label_paginas.grid(row=0, column=1, padx=20)
        self.btn_next = ctk.CTkButton(self.frame_paginacion, text="Siguiente", width=100, command=self.pagina_siguiente)
        self.btn_next.grid(row=0, column=2, padx=10)

        self.cargar_datos()

    def crear_tabla(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=40, font=("Arial", 14))
        style.configure("Treeview.Heading", font=("Arial", 15, "bold"), background="#333", foreground="white")
        
        self.tabla = ttk.Treeview(self.frame_tabla, columns=("Nro.", "Nombre", "Apellido", "Vencimiento", "Dias", "Estado", "Pago"), show="headings")
        columnas = [("Nro.", 50), ("Nombre", 150), ("Apellido", 150), ("Vencimiento", 130), ("Dias", 80), ("Estado", 200), ("Pago", 130)]
        
        for col, ancho in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")

        self.tabla.tag_configure("al_dia", foreground="#2ecc71")
        self.tabla.tag_configure("por_vencer", foreground="#f1c40f")
        self.tabla.tag_configure("vencido", foreground="#e74c3c")
        self.tabla.pack(side="left", fill="both", expand=True)
        
        scrolly = ttk.Scrollbar(self.frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrolly.set)
        scrolly.pack(side="right", fill="y")

    def calcular_estados(self, fecha_ven_str, pago_db):
        """Devuelve el estado de membresía, días restantes, estado de pago y tag de color"""
        if not fecha_ven_str: return "Sin Fecha", "", "No Pago", "vencido"
        try:
            formato = "%Y-%m-%d" if "-" in fecha_ven_str and fecha_ven_str.find("-") == 4 else "%d-%m-%Y"
            fecha_ven = datetime.strptime(fecha_ven_str, formato)
            hoy = datetime.now()
            diferencia = (fecha_ven - hoy).days + 1
            
            if diferencia < 0:
                return "Vencido", "", "No Pago", "vencido"
            
            pago_final = pago_db if pago_db else "Pendiente"
            
            if diferencia <= 2:
                return "Por vencer", diferencia, pago_final, "por_vencer"
            else:
                return "Al día", diferencia, pago_final, "al_dia"
        except:
            return "Error", 0, "Error", "vencido"

    def cargar_datos(self):
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre, apellido, fecha_vencimiento, pago FROM clientes")
                self.datos_completos_db = cursor.fetchall()
            self.buscar_socio() 
        except Exception as e:
            print(f"Error: {e}")

    def buscar_socio(self, event=None):
        """Filtra los datos cargados en memoria según texto, estado de membresía y estado de pago"""
        texto = self.entry_busqueda.get().lower()
        filtro_estado = self.combo_filtro_estado.get()
        filtro_pago = self.combo_filtro_pago.get()

        self.datos_totales = []

        for cli in self.datos_completos_db:
            nom, ape, f_ven, pago_db = cli
            est_mem, dias, est_pag, tag = self.calcular_estados(f_ven, pago_db)

            # Lógica de coincidencia para filtros
            match_texto = texto in nom.lower() or texto in ape.lower()
            match_estado = filtro_estado == "Todos" or filtro_estado == est_mem
            match_pago = filtro_pago == "Todos" or filtro_pago == est_pag

            if match_texto and match_estado and match_pago:
                self.datos_totales.append(cli)

        self.pagina_actual = 1
        self.actualizar_tabla()

    def actualizar_tabla(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)

        inicio = (self.pagina_actual - 1) * self.clientes_por_pagina
        fin = inicio + self.clientes_por_pagina
        datos_pagina = self.datos_totales[inicio:fin]

        for i, (nom, ape, f_ven, pago_db) in enumerate(datos_pagina, start=inicio + 1):
            def f_bonita(f):
                try:
                    formato = "%Y-%m-%d" if "-" in f and f.find("-") == 4 else "%d-%m-%Y"
                    return datetime.strptime(f, formato).strftime("%d-%m-%Y")
                except: return f

            est_mem, dias, est_pag, tag = self.calcular_estados(f_ven, pago_db)
            self.tabla.insert("", "end", values=(i, nom, ape, f_bonita(f_ven), dias, est_mem, est_pag), tags=(tag,))

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

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Gestión de Membresías")
    root.geometry("1200x750")
    ctk.set_appearance_mode("dark")
    GestionMembresia(root).pack(fill="both", expand=True)
    root.mainloop()