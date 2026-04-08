import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3

class GestionGimnasio(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema Gym - Gestión de Planes")
        self.geometry("900x750") # Ventana más grande
        ctk.set_appearance_mode("dark")

        # --- TÍTULO ---
        ctk.CTkLabel(self, text="PLANES DE ENTRENAMIENTO", 
                     font=("Arial", 22, "bold")).pack(pady=20)

        # --- FORMULARIO DE REGISTRO ---
        self.frame_registro = ctk.CTkFrame(self)
        self.frame_registro.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.frame_registro, text="Nombre del Plan:").grid(row=0, column=0, padx=10, pady=20)
        self.entry_nombre_plan = ctk.CTkEntry(self.frame_registro, width=250)
        self.entry_nombre_plan.grid(row=0, column=1, padx=10, pady=20)

        ctk.CTkLabel(self.frame_registro, text="Precio ($):").grid(row=0, column=2, padx=10, pady=20)
        self.entry_precio = ctk.CTkEntry(self.frame_registro, width=120)
        self.entry_precio.grid(row=0, column=3, padx=10, pady=20)

        self.btn_guardar = ctk.CTkButton(self.frame_registro, text="Guardar Plan", 
                                          fg_color="#2ecc71", hover_color="#27ae60", 
                                          font=("Arial", 12, "bold"), command=self.guardar_plan)
        self.btn_guardar.grid(row=0, column=4, padx=15, pady=20)

        # --- TABLA DE PLANES (AGRANDADA) ---
        self.crear_tabla_visual()
        self.cargar_datos_tabla()

        # --- BOTONES DE ACCIÓN (FILA INFERIOR) ---
        self.frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones.pack(pady=20)

        self.btn_editar = ctk.CTkButton(self.frame_acciones, text="Editar Seleccionado", 
                                         fg_color="#3498db", command=self.abrir_modal_edicion)
        self.btn_editar.grid(row=0, column=0, padx=10)

        self.btn_eliminar = ctk.CTkButton(self.frame_acciones, text="Eliminar Seleccionado", 
                                          fg_color="#e74c3c", hover_color="#c0392b", command=self.confirmar_eliminar)
        self.btn_eliminar.grid(row=0, column=1, padx=10)

        self.btn_restablecer = ctk.CTkButton(self.frame_acciones, text="Restablecer Todo", 
                                             fg_color="#777d7e", hover_color="#7f8c8d", command=self.confirmar_restablecer)
        self.btn_restablecer.grid(row=0, column=2, padx=10)

    def crear_tabla_visual(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", 
                        fieldbackground="#2b2b2b", rowheight=35, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#333", foreground="white")
        style.map("Treeview", background=[('selected', '#1f538d')])

        # Definimos las columnas (el ID estará oculto)
        self.tabla = ttk.Treeview(self, columns=("Orden", "Nombre", "Precio", "ID_REAL"), show="headings")
        
        self.tabla.heading("Orden", text="N°")
        self.tabla.heading("Nombre", text="Nombre del Plan de Entrenamiento")
        self.tabla.heading("Precio", text="Precio Sugerido ($)")
        
        self.tabla.column("Orden", width=60, anchor="center")
        self.tabla.column("Nombre", width=450, anchor="w")
        self.tabla.column("Precio", width=150, anchor="center")
        self.tabla.column("ID_REAL", width=0, stretch=False) # Columna invisible para el ID técnico

        self.tabla.pack(pady=10, padx=20, fill="both", expand=True)

    def cargar_datos_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre_plan, precio, id FROM planes")
                for i, (nombre, precio, real_id) in enumerate(cursor.fetchall(), start=1):
                    # Insertamos el número de orden 'i' y al final el id técnico
                    self.tabla.insert("", "end", values=(i, nombre, f"$ {precio:.2f}", real_id))
        except Exception as e:
            print(f"Error al cargar tabla: {e}")

    def guardar_plan(self):
        nombre = self.entry_nombre_plan.get().strip()
        precio = self.entry_precio.get().strip()

        if not nombre or not precio:
            messagebox.showwarning("Atención", "Por favor completa el nombre y el precio")
            return

        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO planes (nombre_plan, precio) VALUES (?, ?)", (nombre, float(precio)))
                conn.commit()
            
            self.entry_nombre_plan.delete(0, 'end')
            self.entry_precio.delete(0, 'end')
            self.cargar_datos_tabla()
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número válido")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def abrir_modal_edicion(self):
        selected = self.tabla.selection()
        if not selected:
            messagebox.showwarning("Atención", "Selecciona un plan de la tabla")
            return

        item_data = self.tabla.item(selected)['values']
        
        modal = ctk.CTkToplevel(self)
        modal.title("Editar Plan")
        modal.geometry("350x300")
        modal.attributes("-topmost", True)

        ctk.CTkLabel(modal, text="Editar Nombre:", font=("Arial", 12, "bold")).pack(pady=(20,0))
        entry_edit_nom = ctk.CTkEntry(modal, width=250)
        entry_edit_nom.insert(0, item_data[1])
        entry_edit_nom.pack(pady=5)

        ctk.CTkLabel(modal, text="Editar Precio:", font=("Arial", 12, "bold")).pack(pady=(10,0))
        entry_edit_pre = ctk.CTkEntry(modal, width=250)
        # Limpiamos el '$' para editar solo el número
        precio_limpio = str(item_data[2]).replace("$ ", "")
        entry_edit_pre.insert(0, precio_limpio)
        entry_edit_pre.pack(pady=5)

        def confirmar():
            try:
                with sqlite3.connect("gimnasio.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE planes SET nombre_plan=?, precio=? WHERE id=?", 
                                   (entry_edit_nom.get(), float(entry_edit_pre.get()), item_data[3]))
                    conn.commit()
                modal.destroy()
                self.cargar_datos_tabla()
            except Exception as e:
                messagebox.showerror("Error", "Datos inválidos")

        ctk.CTkButton(modal, text="Guardar Cambios", fg_color="#2ecc71", command=confirmar).pack(pady=30)

    def confirmar_eliminar(self):
        selected = self.tabla.selection()
        if not selected:
            messagebox.showwarning("Atención", "Selecciona el plan que deseas eliminar")
            return

        item_data = self.tabla.item(selected)['values']
        pregunta = messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar el plan '{item_data[1]}'?")
        
        if pregunta: # Si acepta (True)
            try:
                with sqlite3.connect("gimnasio.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM planes WHERE id=?", (item_data[3],))
                    conn.commit()
                self.cargar_datos_tabla()
                messagebox.showinfo("Eliminado", "El plan ha sido eliminado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def confirmar_restablecer(self):
        pregunta = messagebox.askyesno("Restablecer", "¿Desea eliminar TODOS los planes actuales?\nEsta acción no se puede deshacer.")
        
        if pregunta:
            try:
                with sqlite3.connect("gimnasio.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM planes")
                    # Opcional: Reiniciar el contador de IDs internos de SQLite
                    cursor.execute("DELETE FROM sqlite_sequence WHERE name='planes'")
                    conn.commit()
                self.cargar_datos_tabla()
                messagebox.showinfo("Hecho", "Todos los planes han sido eliminados.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = GestionGimnasio()
    app.mainloop()