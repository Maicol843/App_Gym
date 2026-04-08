import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3

class GestionGimnasio(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema Gym - Gestión de Planes")
        self.geometry("1000x750") # Un poco más ancha para la nueva columna
        ctk.set_appearance_mode("dark")

        ctk.CTkLabel(self, text="CONFIGURACIÓN DE PLANES DE ENTRENAMIENTO", 
                     font=("Arial", 22, "bold")).pack(pady=20)

        # --- FORMULARIO DE REGISTRO ---
        self.frame_registro = ctk.CTkFrame(self)
        self.frame_registro.pack(pady=10, padx=20, fill="x")

        # Configuración de columnas del grid del formulario
        ctk.CTkLabel(self.frame_registro, text="Nombre Plan:").grid(row=0, column=0, padx=5, pady=20)
        self.entry_nombre_plan = ctk.CTkEntry(self.frame_registro, width=200)
        self.entry_nombre_plan.grid(row=0, column=1, padx=5, pady=20)

        ctk.CTkLabel(self.frame_registro, text="Precio ($):").grid(row=0, column=2, padx=5, pady=20)
        self.entry_precio = ctk.CTkEntry(self.frame_registro, width=100)
        self.entry_precio.grid(row=0, column=3, padx=5, pady=20)

        ctk.CTkLabel(self.frame_registro, text="Duración (Días):").grid(row=0, column=4, padx=5, pady=20)
        self.entry_dias = ctk.CTkEntry(self.frame_registro, width=80)
        self.entry_dias.insert(0, "30") # Valor por defecto
        self.entry_dias.grid(row=0, column=5, padx=5, pady=20)

        self.btn_guardar = ctk.CTkButton(self.frame_registro, text="Guardar Plan", 
                                          fg_color="#2ecc71", hover_color="#27ae60", 
                                          font=("Arial", 12, "bold"), command=self.guardar_plan)
        self.btn_guardar.grid(row=0, column=6, padx=15, pady=20)

        # --- TABLA DE PLANES ---
        self.crear_tabla_visual()
        self.cargar_datos_tabla()

        # --- BOTONES DE ACCIÓN ---
        self.frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones.pack(pady=20)

        self.btn_editar = ctk.CTkButton(self.frame_acciones, text="Editar Seleccionado", 
                                         fg_color="#3498db", command=self.abrir_modal_edicion)
        self.btn_editar.grid(row=0, column=0, padx=10)

        self.btn_eliminar = ctk.CTkButton(self.frame_acciones, text="Eliminar Seleccionado", 
                                          fg_color="#e74c3c", command=self.confirmar_eliminar)
        self.btn_eliminar.grid(row=0, column=1, padx=10)

        self.btn_restablecer = ctk.CTkButton(self.frame_acciones, text="Restablecer Todo", 
                                             fg_color="#95a5a6", command=self.confirmar_restablecer)
        self.btn_restablecer.grid(row=0, column=2, padx=10)

    def crear_tabla_visual(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=35)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        # Agregamos la columna 'Dias'
        self.tabla = ttk.Treeview(self, columns=("Orden", "Nombre", "Precio", "Dias", "ID_REAL"), show="headings")
        
        self.tabla.heading("Orden", text="N°")
        self.tabla.heading("Nombre", text="Nombre del Plan")
        self.tabla.heading("Precio", text="Precio ($)")
        self.tabla.heading("Dias", text="Duración (Días)")
        
        self.tabla.column("Orden", width=50, anchor="center")
        self.tabla.column("Nombre", width=350, anchor="w")
        self.tabla.column("Precio", width=120, anchor="center")
        self.tabla.column("Dias", width=120, anchor="center")
        self.tabla.column("ID_REAL", width=0, stretch=False)

        self.tabla.pack(pady=10, padx=20, fill="both", expand=True)

    def cargar_datos_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre_plan, precio, dias, id FROM planes")
                for i, (nombre, precio, dias, real_id) in enumerate(cursor.fetchall(), start=1):
                    self.tabla.insert("", "end", values=(i, nombre, f"$ {precio:.2f}", f"{dias} días", real_id))
        except Exception as e:
            print(f"Error: {e}")

    def guardar_plan(self):
        nombre = self.entry_nombre_plan.get().strip()
        precio = self.entry_precio.get().strip()
        dias = self.entry_dias.get().strip()

        if not nombre or not precio or not dias:
            messagebox.showwarning("Atención", "Completa todos los campos")
            return

        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO planes (nombre_plan, precio, dias) VALUES (?, ?, ?)", 
                               (nombre, float(precio), int(dias)))
                conn.commit()
            self.limpiar_inputs()
            self.cargar_datos_tabla()
        except ValueError:
            messagebox.showerror("Error", "Precio y Días deben ser números")

    def limpiar_inputs(self):
        self.entry_nombre_plan.delete(0, 'end')
        self.entry_precio.delete(0, 'end')
        self.entry_dias.delete(0, 'end')
        self.entry_dias.insert(0, "30")

    def abrir_modal_edicion(self):
        selected = self.tabla.selection()
        if not selected:
            messagebox.showwarning("Atención", "Selecciona un plan")
            return

        item_data = self.tabla.item(selected)['values']
        
        modal = ctk.CTkToplevel(self)
        modal.title("Editar Plan")
        modal.geometry("350x400")
        modal.attributes("-topmost", True)

        ctk.CTkLabel(modal, text="Nombre Plan:").pack(pady=(20,0))
        en = ctk.CTkEntry(modal, width=250); en.insert(0, item_data[1]); en.pack(pady=5)

        ctk.CTkLabel(modal, text="Precio ($):").pack(pady=(10,0))
        ep = ctk.CTkEntry(modal, width=250); ep.insert(0, str(item_data[2]).replace("$ ", "")); ep.pack(pady=5)

        ctk.CTkLabel(modal, text="Duración (Días):").pack(pady=(10,0))
        ed = ctk.CTkEntry(modal, width=250); ed.insert(0, str(item_data[3]).replace(" días", "")); ed.pack(pady=5)

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

if __name__ == "__main__":
    app = GestionGimnasio()
    app.mainloop()