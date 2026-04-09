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
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                query = """
                    SELECT c.nombre, c.apellido, c.fecha_inscripcion, c.fecha_vencimiento, 
                           c.plan_seleccionado, c.pago, p.dias, p.precio
                    FROM clientes c
                    LEFT JOIN planes p ON c.plan_seleccionado = p.nombre_plan
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

        # --- LÓGICA DE COLORES PARA EL PAGO ---
        estado_pago = m['pago'] if m['pago'] else "Pendiente"
        
        # Pendiente = Amarillo (#FFCC00)
        # Realizado = Verde (#2ecc71)
        # No Pago = Rojo (#e74c3c)
        if estado_pago == "Realizado":
            color_pago = "#2ecc71"
        elif estado_pago == "Pendiente":
            color_pago = "#FFCC00"
        else: # "No Pago" u otros
            color_pago = "#e74c3c"

        fecha_ins_bonita = self.formatear_fecha_gui(m['fecha_inscripcion'])
        fecha_ven_bonita = self.formatear_fecha_gui(m['fecha_vencimiento'])

        self.crear_item_dato(card, "Plan Actual:", m['plan_seleccionado'])
        self.crear_item_dato(card, "Estado de Pago:", estado_pago, color_personalizado=color_pago)
        self.crear_item_dato(card, "Fecha de Inscripción:", fecha_ins_bonita)
        self.crear_item_dato(card, "Fecha de Vencimiento:", fecha_ven_bonita, destacado=True)
        self.crear_item_dato(card, "Duración del Plan:", f"{m['dias']} días")
        self.crear_item_dato(card, "Precio del Plan:", f"$ {m['precio']}")

        ctk.CTkButton(self.scroll_frame, text="ACTUALIZAR", 
                     fg_color="#2ecc71", hover_color="#27ae60", height=50, 
                     font=("Arial", 16, "bold"),
                     command=lambda: self.abrir_modal_renovacion(m)).pack(pady=40)

    def crear_item_dato(self, parent, label, valor, destacado=False, color_personalizado=None):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=30, pady=10)
        
        if color_personalizado:
            color_val = color_personalizado
        else:
            color_val = "#e74c3c" if destacado else "white" 
            
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
        combo_plan.set(datos_actuales['plan_seleccionado'])
        combo_plan.pack(pady=5)

        # Se agrega "No Pago" a las opciones del menú
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
                    
                    cursor.execute("""
                        UPDATE clientes 
                        SET plan_seleccionado = ?, 
                            fecha_inscripcion = ?, 
                            fecha_vencimiento = ?,
                            pago = ?
                        WHERE id = ?
                    """, (nuevo_plan, fecha_inicio_obj.strftime("%Y-%m-%d"), 
                          nueva_fecha_ven.strftime("%Y-%m-%d"), nuevo_estado_pago, self.id_cliente))
                    conn.commit()

                messagebox.showinfo("Éxito", "Membresía actualizada correctamente.")
                modal.destroy()
                self.cargar_datos_membresia() 
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha incorrecto. Use DD-MM-AAAA")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

        ctk.CTkButton(modal, text="CONFIRMAR ACTUALIZACIÓN", fg_color="#2ecc71", height=40, command=procesar_actualizacion).pack(pady=30)