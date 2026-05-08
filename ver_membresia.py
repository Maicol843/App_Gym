import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime, timedelta

class VerMembresia(ctk.CTkFrame):
    def __init__(self, parent, id_cliente, callback_volver):
        super().__init__(parent, fg_color="transparent")
        self.id_cliente = id_cliente
        self.callback_volver = callback_volver
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkButton(header, text="← Volver", width=80, command=self.callback_volver).pack(side="left")
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#1a1a1a")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.cargar_datos_membresia()

    def formatear_fecha_gui(self, fecha_db):
        if not fecha_db: return "S/D"
        try:
            return datetime.strptime(fecha_db, "%Y-%m-%d").strftime("%d-%m-%Y")
        except:
            return fecha_db

    def obtener_datos(self):
        """Obtiene el último plan registrado para el cliente desde plan_elegido."""
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                # La consulta busca el registro con el ID más alto (el último) para este cliente
                query = """
                    SELECT c.nombre, c.apellido, p.fecha_inscripcion, p.fecha_vencimiento, 
                           p.plan_seleccionado, p.pago, pl.dias, pl.precio
                    FROM clientes c
                    LEFT JOIN plan_elegido p ON p.id = (
                        SELECT id FROM plan_elegido 
                        WHERE id_cliente = c.id 
                        ORDER BY id DESC LIMIT 1
                    )
                    LEFT JOIN planes pl ON p.plan_seleccionado = pl.nombre_plan
                    WHERE c.id = ?
                """
                cursor.execute(query, (self.id_cliente,))
                return cursor.fetchone()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar membresía: {e}")
            return None

    def cargar_datos_membresia(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        
        m = self.obtener_datos()
        if not m: return

        ctk.CTkLabel(self.scroll_frame, text=f"{m['nombre']} {m['apellido']}", 
                     font=("Arial", 28, "bold"), text_color="#FFCC00").pack(pady=20)
        
        card = ctk.CTkFrame(self.scroll_frame, fg_color="#2b2b2b", corner_radius=15)
        card.pack(pady=10, padx=50, fill="x")

        # Lógica de colores según el estado
        estado_pago = m['pago'] if m['pago'] else "Pendiente"
        if estado_pago == "Realizado":
            color_pago = "#198754"
        elif estado_pago == "Pendiente":
            color_pago = "#ffc107"
        else: 
            color_pago = "#dc3545"

        fecha_ins_bonita = self.formatear_fecha_gui(m['fecha_inscripcion'])
        fecha_ven_bonita = self.formatear_fecha_gui(m['fecha_vencimiento'])

        self.crear_item_dato(card, "Plan Actual:", m['plan_seleccionado'] if m['plan_seleccionado'] else "Sin Plan")
        self.crear_item_dato(card, "Estado de Pago:", estado_pago, color_personalizado=color_pago)
        self.crear_item_dato(card, "Fecha de Inscripción:", fecha_ins_bonita)
        self.crear_item_dato(card, "Fecha de Vencimiento:", fecha_ven_bonita, destacado=True)
        self.crear_item_dato(card, "Duración del Plan:", f"{m['dias'] if m['dias'] else 0} días")
        self.crear_item_dato(card, "Precio del Plan:", f"$ {m['precio'] if m['precio'] else 0}")

        ctk.CTkButton(self.scroll_frame, text="Renovar", 
                     fg_color="#6610f2", hover_color="#520DC2", height=50, 
                     font=("Arial", 16, "bold"),
                     command=lambda: self.abrir_modal_renovacion(m)).pack(pady=40)

    def crear_item_dato(self, parent, label, valor, destacado=False, color_personalizado=None):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=30, pady=10)
        color_val = color_personalizado if color_personalizado else ("#e74c3c" if destacado else "white")
        ctk.CTkLabel(f, text=label, font=("Arial", 14, "bold"), width=200, anchor="w").pack(side="left")
        ctk.CTkLabel(f, text=str(valor), font=("Arial", 14), text_color=color_val).pack(side="left", padx=10)

    def obtener_lista_planes(self):
        planes = []
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre_plan FROM planes")
                planes = [fila[0] for fila in cursor.fetchall()]
        except: pass
        return planes

    def abrir_modal_renovacion(self, datos_actuales):
        modal = ctk.CTkToplevel(self)
        modal.title("Renovación de Membresía")
        modal.geometry("500x650")
        modal.grab_set()
        modal.attributes("-topmost", True)

        ctk.CTkLabel(modal, text="RENOVAR O CAMBIAR PLAN", font=("Arial", 18, "bold")).pack(pady=20)

        ctk.CTkLabel(modal, text="Seleccionar Plan:").pack(pady=(10,0))
        combo_plan = ctk.CTkOptionMenu(modal, values=self.obtener_lista_planes(), width=250)
        if datos_actuales['plan_seleccionado']:
            combo_plan.set(datos_actuales['plan_seleccionado'])
        combo_plan.pack(pady=5)

        ctk.CTkLabel(modal, text="Estado del Pago:").pack(pady=(10,0))
        combo_pago = ctk.CTkOptionMenu(modal, values=["Pendiente", "Realizado", "No Pago"], width=250)
        combo_pago.set(datos_actuales['pago'] if datos_actuales['pago'] else "Pendiente")
        combo_pago.pack(pady=5)

        ctk.CTkLabel(modal, text="Nueva Fecha de Inscripción (DD-MM-AAAA):").pack(pady=(10,0))
        ent_fecha = ctk.CTkEntry(modal, width=250)
        ent_fecha.insert(0, datetime.now().strftime("%d-%m-%Y"))
        ent_fecha.pack(pady=5)

        def procesar_actualizacion():
            try:
                nuevo_plan = combo_plan.get()
                nuevo_estado_pago = combo_pago.get()
                fecha_inicio_str = ent_fecha.get()
                fecha_inicio_obj = datetime.strptime(fecha_inicio_str, "%d-%m-%Y")

                with sqlite3.connect("gimnasio.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT dias FROM planes WHERE nombre_plan = ?", (nuevo_plan,))
                    resultado = cursor.fetchone()
                    
                    if not resultado:
                        messagebox.showerror("Error", "El plan seleccionado no existe.")
                        return
                    
                    dias = resultado[0]
                    nueva_fecha_ven = fecha_inicio_obj + timedelta(days=dias)
                    
                    # INSERCIÓN EN LUGAR DE UPDATE: 
                    # Se crea un nuevo registro para mantener el historial del cliente
                    cursor.execute("""
                        INSERT INTO plan_elegido (
                            id_cliente, plan_seleccionado, fecha_inscripcion, 
                            fecha_vencimiento, pago
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (self.id_cliente, nuevo_plan, 
                          fecha_inicio_obj.strftime("%Y-%m-%d"), 
                          nueva_fecha_ven.strftime("%Y-%m-%d"), 
                          nuevo_estado_pago))
                    conn.commit()

                messagebox.showinfo("Éxito", "Membresía renovada correctamente.")
                modal.destroy()
                self.cargar_datos_membresia() 
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha incorrecto. Use DD-MM-AAAA")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

        ctk.CTkButton(modal, text="Actualizar", fg_color="#20c997", height=40, command=procesar_actualizacion).pack(pady=30)