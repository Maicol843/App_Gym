import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3

class GestionGimnasio(ctk.CTkFrame): # Modificado para ser un Frame
    def __init__(self, parent):      # Recibe el contenedor padre
        super().__init__(parent, fg_color="transparent")

        # Título de la sección
        ctk.CTkLabel(self, text="PLANES DE ENTRENAMIENTO", 
                     font=("Arial", 22, "bold")).pack(pady=20)

        # --- FORMULARIO DE REGISTRO ---
        self.frame_registro = ctk.CTkFrame(self)
        self.frame_registro.pack(pady=10, padx=20, fill="x")

        # Configuración de columnas del grid del formulario
        ctk.CTkLabel(self.frame_registro, text="Nombre del plan:").grid(row=0, column=0, padx=5, pady=20)
        self.entry_nombre_plan = ctk.CTkEntry(self.frame_registro, width=200)
        self.entry_nombre_plan.grid(row=0, column=1, padx=5, pady=20)

        ctk.CTkLabel(self.frame_registro, text="Precio ($):").grid(row=0, column=2, padx=5, pady=20)
        self.entry_precio = ctk.CTkEntry(self.frame_registro, width=100)
        self.entry_precio.grid(row=0, column=3, padx=5, pady=20)

        ctk.CTkLabel(self.frame_registro, text="Días:").grid(row=0, column=4, padx=5, pady=20)
        self.entry_dias = ctk.CTkEntry(self.frame_registro, width=80)
        self.entry_dias.grid(row=0, column=5, padx=5, pady=20)

        self.btn_guardar = ctk.CTkButton(self.frame_registro, text="Guardar", 
                                          command=self.guardar_plan, fg_color="#2ecc71")
        self.btn_guardar.grid(row=0, column=6, padx=15, pady=20)

        # --- TABLA DE PLANES ---
        self.crear_tabla()
        self.cargar_datos_tabla()

        # --- BOTONES DE ACCIÓN (Debajo de la tabla) ---
        self.frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones.pack(pady=20)

        ctk.CTkButton(self.frame_acciones, text="Editar Seleccionado", 
                       command=self.abrir_modal_edicion, fg_color="#3498db").pack(side="left", padx=10)
        ctk.CTkButton(self.frame_acciones, text="Eliminar Plan", 
                       command=self.confirmar_eliminar, fg_color="#e74c3c").pack(side="left", padx=10)
        ctk.CTkButton(self.frame_acciones, text="Restablecer Todo", 
                       command=self.confirmar_restablecer, fg_color="gray").pack(side="left", padx=10)

    def crear_tabla(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", 
                        fieldbackground="#2b2b2b", rowheight=35, font=("Arial", 11))
        style.map("Treeview", background=[('selected', '#3498db')])

        self.tabla = ttk.Treeview(self, columns=("N°", "Nombre", "Precio", "Días"), show="headings")
        self.tabla.heading("N°", text="Nro.")
        self.tabla.heading("Nombre", text="Plan")
        self.tabla.heading("Precio", text="Precio")
        self.tabla.heading("Días", text="Días de duración")

        self.tabla.column("N°", width=50, anchor="center")
        self.tabla.column("Nombre", width=300, anchor="center")
        self.tabla.column("Precio", width=150, anchor="center")
        self.tabla.column("Días", width=150, anchor="center")

        self.tabla.pack(pady=10, padx=20, fill="both", expand=True)

    def guardar_plan(self):
        n = self.entry_nombre_plan.get()
        p = self.entry_precio.get()
        d = self.entry_dias.get()

        if not n or not p or not d:
            messagebox.showwarning("Atención", "Complete todos los campos")
            return

        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS planes (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre_plan TEXT, precio REAL, dias INTEGER)")
                cursor.execute("INSERT INTO planes (nombre_plan, precio, dias) VALUES (?,?,?)", (n, float(p), int(d)))
                conn.commit()
            
            self.entry_nombre_plan.delete(0, 'end')
            self.entry_precio.delete(0, 'end')
            self.entry_dias.delete(0, 'end')
            self.cargar_datos_tabla()
            messagebox.showinfo("Éxito", "Plan guardado correctamente")
        except ValueError:
            messagebox.showerror("Error", "Precio y Días deben ser números")

    def cargar_datos_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS planes (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre_plan TEXT, precio REAL, dias INTEGER)")
                cursor.execute("SELECT nombre_plan, precio, dias, id FROM planes")
                for i, fila in enumerate(cursor.fetchall(), start=1):
                    # El ID real de la DB se guarda oculto en los valores para poder editar/eliminar
                    self.tabla.insert("", "end", values=(i, fila[0], f"$ {fila[1]:.2f}", fila[2], fila[3]))
        except Exception as e:
            print(f"Error cargando tabla: {e}")

    def abrir_modal_edicion(self):
        selected = self.tabla.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un plan para editar")
            return
        
        item_data = self.tabla.item(selected)['values']
        
        # Ventana modal (Toplevel sigue siendo necesario para diálogos emergentes)
        modal = ctk.CTkToplevel(self)
        modal.title("Editar Plan")
        modal.geometry("400x400")
        modal.attributes("-topmost", True)

        ctk.CTkLabel(modal, text="Editar Plan", font=("Arial", 18, "bold")).pack(pady=20)
        
        en = ctk.CTkEntry(modal, width=250, placeholder_text="Nombre")
        en.insert(0, item_data[1])
        en.pack(pady=10)
        
        ep = ctk.CTkEntry(modal, width=250, placeholder_text="Precio")
        ep.insert(0, item_data[2].replace("$ ", ""))
        ep.pack(pady=10)
        
        ed = ctk.CTkEntry(modal, width=250, placeholder_text="Días")
        ed.insert(0, item_data[3])
        ed.pack(pady=10)

        def confirmar():
            try:
                with sqlite3.connect("gimnasio.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE planes SET nombre_plan=?, precio=?, dias=? WHERE id=?", 
                                   (en.get(), float(ep.get()), int(ed.get()), item_data[4]))
                    conn.commit()
                modal.destroy()
                self.cargar_datos_tabla()
            except:
                messagebox.showerror("Error", "Datos inválidos")

        ctk.CTkButton(modal, text="Actualizar", fg_color="#2ecc71", command=confirmar).pack(pady=30)

    def confirmar_eliminar(self):
        selected = self.tabla.selection()
        if not selected: return
        item_data = self.tabla.item(selected)['values']
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{item_data[1]}'?"):
            with sqlite3.connect("gimnasio.db") as conn:
                conn.cursor().execute("DELETE FROM planes WHERE id=?", (item_data[4],))
            self.cargar_datos_tabla()

    def confirmar_restablecer(self):
        if messagebox.askyesno("Restablecer", "¿Eliminar TODOS los planes?"):
            with sqlite3.connect("gimnasio.db") as conn:
                conn.cursor().execute("DELETE FROM planes")
                conn.cursor().execute("DELETE FROM sqlite_sequence WHERE name='planes'")
            self.cargar_datos_tabla()