import customtkinter as ctk
from tkinter import messagebox
import sqlite3

class VerFicha(ctk.CTkFrame):
    def __init__(self, parent, id_cliente, callback_volver):
        super().__init__(parent, fg_color="transparent")
        self.id_cliente = id_cliente
        self.callback_volver = callback_volver 
        
        # Cabecera
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(header, text="← Volver al Listado", width=120, command=self.callback_volver).pack(side="left")
        ctk.CTkLabel(header, text=f"FICHA DEL CLIENTE", font=("Arial", 20, "bold")).pack(side="left", padx=20)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#1a1a1a")
        self.scroll_frame.pack(fill="both", expand=True)

        self.cargar_datos_y_mostrar()

    def obtener_datos_cliente(self):
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM clientes WHERE id = ?", (self.id_cliente,))
                return cursor.fetchone()
        except Exception as e:
            messagebox.showerror("Error", f"Error DB: {e}")
            return None

    def si_no_text(self, valor): 
        return "SÍ" if valor == 1 else "NO"

    def cargar_datos_y_mostrar(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        c = self.obtener_datos_cliente()
        if not c: return

        contenedor_columnas = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        contenedor_columnas.pack(fill="x", padx=10, pady=10)
        contenedor_columnas.columnconfigure((0, 1), weight=1)

        # COLUMNA 1: Personales y Físicos
        col1 = ctk.CTkFrame(contenedor_columnas, fg_color="#2b2b2b")
        col1.grid(row=0, column=0, padx=10, sticky="nsew")
        self.crear_bloque_info(col1, "DATOS PERSONALES", [
            ("Nombre", c['nombre']), ("Apellido", c['apellido']), ("Domicilio", c['domicilio']), 
            ("Teléfono", c['telefono']), ("Fecha de Nacimiento", c['fecha_nacimiento']), ("Edad", f"{c['edad']} años")
        ])
        self.crear_bloque_info(col1, "ESTADO FÍSICO", [
            ("Altura", f"{c['altura']} cm"), ("Peso", f"{c['peso']} kg"), ("Grupo Sanguíneo", c['grupo_sanguineo'])
        ])

        # COLUMNA 2: Médicos y Síntomas
        col2 = ctk.CTkFrame(contenedor_columnas, fg_color="#2b2b2b")
        col2.grid(row=0, column=1, padx=10, sticky="nsew")
        self.crear_bloque_info(col2, "HISTORIAL MÉDICO", [
            ("Patología de Columna", f"{self.si_no_text(c['patologia_columna'])} - {c['detalle_columna']}"),
            ("Enfermedades Cardíacas", f"{self.si_no_text(c['enfermedades_cardiacas'])} - {c['detalle_cardiaco']}"),
            ("Lesiones", f"{self.si_no_text(c['lesiones'])} - {c['detalle_lesion']}"),
            ("Practica otros deportes", f"{self.si_no_text(c['deportes'])} - {c['detalle_deporte']}")
        ])
        self.crear_bloque_info(col2, "OTROS SÍNTOMAS", [
            ("¿Sufre mareos?", self.si_no_text(c['mareos'])), ("¿Ha sufrido desmayos?", self.si_no_text(c['desmayos'])),
            ("¿Tiene dolor de cabeza con frecuencia?", self.si_no_text(c['dolor_cabeza'])), ("¿Sufre hemorragias nasales?", self.si_no_text(c['hemorragias_nasales'])),
            ("¿Tiene dolores en las articulaciones?", self.si_no_text(c['dolores_articulares'])), ("¿Presenta pie plano, cabo o alguna otra alteración?", self.si_no_text(c['alteracion'])),
            ("¿Ha sufrido convulsiones?", self.si_no_text(c['convulsiones'])), ("¿Presenta problemas de tobillo y/o rodilla?", self.si_no_text(c['problemas_rodilla_tobillo']))
        ])

        # BOTONES
        btns = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        btns.pack(pady=30)
        ctk.CTkButton(btns, text="EDITAR DATOS", fg_color="#3498db", command=lambda: self.abrir_modal_edicion(c)).pack(side="left", padx=10)
        ctk.CTkButton(btns, text="ELIMINAR CLIENTE", fg_color="#e74c3c", command=self.eliminar_cliente).pack(side="left", padx=10)

    def crear_bloque_info(self, parent, titulo, items):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(frame, text=titulo, font=("Arial", 14, "bold"), text_color="#3498db").pack(anchor="w")
        ctk.CTkFrame(frame, height=2, fg_color="#444").pack(fill="x", pady=5)
        for label, valor in items:
            f = ctk.CTkFrame(frame, fg_color="transparent")
            f.pack(fill="x")
            ctk.CTkLabel(f, text=f"{label}:", font=("Arial", 12, "bold"), width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(f, text=f"{valor}", font=("Arial", 12), wraplength=200, justify="left").pack(side="left", padx=5)

    # --- MODAL DE EDICIÓN FILTRADO ---
    def abrir_modal_edicion(self, c):
        modal = ctk.CTkToplevel(self)
        modal.title("Editar Ficha Médica y Personal")
        modal.geometry("750x850")
        modal.grab_set()
        modal.attributes("-topmost", True)

        scr = ctk.CTkScrollableFrame(modal, fg_color="#1a1a1a")
        scr.pack(fill="both", expand=True, padx=10, pady=10)

        form = ctk.CTkFrame(scr, fg_color="transparent")
        form.pack(pady=10, padx=20)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        campos_finales = {}
        campos_bool = ['patologia_columna', 'enfermedades_cardiacas', 'lesiones', 'deportes', 
                       'mareos', 'dolor_cabeza', 'desmayos', 'hemorragias_nasales', 
                       'dolores_articulares', 'alteracion', 'problemas_rodilla_tobillo', 'convulsiones']
        
        # LISTA DE EXCLUSIÓN: Campos que NO se deben editar aquí
        excluir = ['id', 'plan_id', 'plan_seleccionado', 'fecha_inscripcion', 'fecha_vencimiento']

        fila_visible = 0
        for col in c.keys():
            if col in excluir: continue # <-- Aquí aplicamos el filtro
            
            txt_label = col.replace('_', ' ').capitalize()
            ctk.CTkLabel(form, text=f"{txt_label}:", font=("Arial", 12, "bold")).grid(row=fila_visible, column=0, padx=10, pady=5, sticky="e")

            if col in campos_bool:
                opt = ctk.CTkOptionMenu(form, values=["No", "Sí"], width=150)
                opt.set("Sí" if c[col] == 1 else "No")
                opt.grid(row=fila_visible, column=1, padx=10, pady=5, sticky="w")
                campos_finales[col] = opt
            else:
                ent = ctk.CTkEntry(form, width=350)
                ent.insert(0, str(c[col]) if c[col] is not None else "")
                ent.grid(row=fila_visible, column=1, padx=10, pady=5, sticky="w")
                campos_finales[col] = ent
            
            fila_visible += 1

        def guardar():
            try:
                set_clause = []
                params = []
                for col, widget in campos_finales.items():
                    set_clause.append(f"{col}=?")
                    val = 1 if (col in campos_bool and widget.get() == "Sí") else (0 if col in campos_bool else widget.get())
                    params.append(val)
                
                params.append(self.id_cliente)
                query = f"UPDATE clientes SET {', '.join(set_clause)} WHERE id=?"
                
                with sqlite3.connect("gimnasio.db") as conn:
                    conn.execute(query, params)
                    conn.commit()
                
                modal.destroy()
                self.cargar_datos_y_mostrar()
                messagebox.showinfo("Éxito", "Ficha actualizada.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(scr, text="GUARDAR CAMBIOS", fg_color="#2ecc71", height=40, command=guardar).pack(pady=20)

    def eliminar_cliente(self):
        if messagebox.askyesno("Eliminar", "¿Seguro que desea eliminar a este cliente?"):
            with sqlite3.connect("gimnasio.db") as conn:
                conn.execute("DELETE FROM clientes WHERE id=?", (self.id_cliente,))
                conn.commit()
            self.callback_volver()