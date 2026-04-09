import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class GestionMembresia(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Variables de paginación
        self.pagina_actual = 1
        self.clientes_por_pagina = 10
        self.datos_totales = []

        # --- CABECERA Y BUSCADOR ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(self.frame_top, text="CONTROL DE MEMBRESÍAS", font=("Arial", 24, "bold")).pack(side="left")

        self.entry_busqueda = ctk.CTkEntry(self.frame_top, placeholder_text="Buscar cliente...", width=300)
        self.entry_busqueda.pack(side="right", padx=10)
        self.entry_busqueda.bind("<KeyRelease>", self.buscar_socio)

        # --- TABLA ---
        self.frame_tabla = ctk.CTkFrame(self)
        self.frame_tabla.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.crear_tabla()

        # --- PAGINACIÓN ---
        self.frame_paginacion = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_paginacion.pack(pady=20)

        self.btn_prev = ctk.CTkButton(self.frame_paginacion, text="Anterior", width=80, command=self.pagina_anterior)
        self.btn_prev.grid(row=0, column=0, padx=10)

        self.label_paginas = ctk.CTkLabel(self.frame_paginacion, text="Página 1 de 1")
        self.label_paginas.grid(row=0, column=1, padx=20)

        self.btn_next = ctk.CTkButton(self.frame_paginacion, text="Siguiente", width=80, command=self.pagina_siguiente)
        self.btn_next.grid(row=0, column=2, padx=10)

        self.cargar_datos()

    def crear_tabla(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=35)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#333", foreground="white")
        
        # Colores para los estados
        style.map("Treeview", background=[('selected', '#1f538d')])
        
        self.tabla = ttk.Treeview(self.frame_tabla, columns=("Nro.", "Nombre", "Apellido", "Inscripcion", "Vencimiento", "Dias restantes", "Estado"), show="headings")
        
        columnas = [("Nro.", 40), ("Nombre", 150), ("Apellido", 150), ("Inscripcion", 120), ("Vencimiento", 120), ("Dias restantes", 100), ("Estado", 180)]
        for col, ancho in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")

        # Configuración de colores de fila (Tags)
        self.tabla.tag_configure("al_dia", foreground="#2ecc71")       # Verde
        self.tabla.tag_configure("por_vencer", foreground="#f1c40f")    # Amarillo
        self.tabla.tag_configure("vencido", foreground="#e74c3c")       # Rojo

        self.tabla.pack(side="left", fill="both", expand=True)
        
        scrolly = ttk.Scrollbar(self.frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrolly.set)
        scrolly.pack(side="right", fill="y")

    def calcular_estado(self, fecha_ven_str):
        if not fecha_ven_str:
            return "Sin Fecha", 0, "vencido"
        
        try:
            # Soportar formatos YYYY-MM-DD y DD-MM-YYYY
            formato = "%Y-%m-%d" if "-" in fecha_ven_str and fecha_ven_str.find("-") == 4 else "%d-%m-%Y"
            fecha_ven = datetime.strptime(fecha_ven_str, formato)
            hoy = datetime.now()
            
            diferencia = (fecha_ven - hoy).days + 1 # +1 para contar el día actual
            
            if diferencia < 0:
                return "Plan Vencido", "", "vencido" # No figura días si ya venció
            elif diferencia <= 2:
                return "Plan se está por vencer", diferencia, "por_vencer"
            else:
                return "Plan al día", diferencia, "al_dia"
        except:
            return "Error Fecha", 0, "vencido"

    def cargar_datos(self):
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre, apellido, fecha_inscripcion, fecha_vencimiento FROM clientes")
                self.datos_totales = cursor.fetchall()
            self.actualizar_tabla()
        except Exception as e:
            print(f"Error: {e}")

    def actualizar_tabla(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)

        inicio = (self.pagina_actual - 1) * self.clientes_por_pagina
        fin = inicio + self.clientes_por_pagina
        datos_pagina = self.datos_totales[inicio:fin]

        for i, (nom, ape, f_ins, f_ven) in enumerate(datos_pagina, start=inicio + 1):
            # Formatear fechas para mostrar en la tabla (DD-MM-YYYY)
            def f_bonita(f):
                try:
                    formato = "%Y-%m-%d" if "-" in f and f.find("-") == 4 else "%d-%m-%Y"
                    return datetime.strptime(f, formato).strftime("%d-%m-%Y")
                except: return f

            estado_txt, dias_rest, tag = self.calcular_estado(f_ven)
            
            self.tabla.insert("", "end", values=(i, nom, ape, f_bonita(f_ins), f_bonita(f_ven), dias_rest, estado_txt), tags=(tag,))

        total_pag = max(1, (len(self.datos_totales) + self.clientes_por_pagina - 1) // self.clientes_por_pagina)
        self.label_paginas.configure(text=f"Página {self.pagina_actual} de {total_pag}")

    def buscar_socio(self, event=None):
        termino = self.entry_busqueda.get().lower()
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre, apellido, fecha_inscripcion, fecha_vencimiento FROM clientes WHERE LOWER(nombre) LIKE ? OR LOWER(apellido) LIKE ?", 
                               (f'%{termino}%', f'%{termino}%'))
                self.datos_totales = cursor.fetchall()
            self.pagina_actual = 1
            self.actualizar_tabla()
        except: pass

    def pagina_siguiente(self):
        total_pag = (len(self.datos_totales) + self.clientes_por_pagina - 1) // self.clientes_por_pagina
        if self.pagina_actual < total_pag:
            self.pagina_actual += 1
            self.actualizar_tabla()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_tabla()

# --- CÓDIGO PARA PROBAR LA VENTANA INDEPENDIENTE ---
if __name__ == "__main__":
    # Creamos una ventana de prueba
    root = ctk.CTk()
    root.title("Prueba de Gestión de Membresías")
    root.geometry("1100x700")
    ctk.set_appearance_mode("dark")

    # Instanciamos el frame dentro de la ventana de prueba
    gestion = GestionMembresia(root)
    gestion.pack(fill="both", expand=True)

    root.mainloop()