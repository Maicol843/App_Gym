import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class ControlGastos(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Configuración de variables
        self.pagina_actual = 1
        self.registros_por_pagina = 10
        self.datos_totales = []

        # --- CABECERA ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(pady=20, padx=20, fill="x")
        ctk.CTkLabel(self.frame_top, text="CONTROL DE GASTOS", font=("Arial", 28, "bold")).pack(side="left")

        # --- BUSCADOR Y BOTÓN INGRESAR ---
        self.frame_controles = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_controles.pack(pady=10, padx=20, fill="x")

        self.entry_busqueda = ctk.CTkEntry(self.frame_controles, placeholder_text="Buscar por detalle...", width=300, font=("Arial", 14))
        self.entry_busqueda.pack(side="left", padx=10)
        self.entry_busqueda.bind("<KeyRelease>", lambda e: self.cargar_datos_db())

        self.btn_ingresar = ctk.CTkButton(self.frame_controles, text="+ INGRESAR GASTO", fg_color="#e67e22", 
                                          font=("Arial", 14, "bold"), command=self.abrir_modal_ingreso)
        self.btn_ingresar.pack(side="right", padx=10)

        # --- TABLA ---
        self.frame_tabla = ctk.CTkFrame(self)
        self.frame_tabla.pack(pady=10, padx=20, fill="both", expand=True)
        self.crear_tabla()

        # --- RESUMEN TOTAL ---
        self.frame_total = ctk.CTkFrame(self, fg_color="#1a1a1a", height=50)
        self.frame_total.pack(pady=5, padx=20, fill="x")
        self.label_total_egresos = ctk.CTkLabel(self.frame_total, text="TOTAL EGRESOS: $0.00", font=("Arial", 18, "bold"), text_color="#e74c3c")
        self.label_total_egresos.pack(side="right", padx=20, pady=10)

        # --- BOTONES DE ACCIÓN ---
        self.frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones.pack(pady=10)

        ctk.CTkButton(self.frame_acciones, text="EDITAR", fg_color="#3498db", command=self.editar_gasto).grid(row=0, column=0, padx=10)
        ctk.CTkButton(self.frame_acciones, text="ELIMINAR", fg_color="#e74c3c", command=self.eliminar_gasto).grid(row=0, column=1, padx=10)
        ctk.CTkButton(self.frame_acciones, text="RESTABLECER TODO", fg_color="#555", command=self.restablecer_base_datos).grid(row=0, column=2, padx=10)

        # --- PAGINACIÓN ---
        self.frame_paginacion = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_paginacion.pack(pady=10)
        self.btn_prev = ctk.CTkButton(self.frame_paginacion, text="Anterior", width=80, command=self.pagina_anterior)
        self.btn_prev.grid(row=0, column=0, padx=10)
        self.label_paginas = ctk.CTkLabel(self.frame_paginacion, text="Página 1 de 1", font=("Arial", 14))
        self.label_paginas.grid(row=0, column=1, padx=20)
        self.btn_next = ctk.CTkButton(self.frame_paginacion, text="Siguiente", width=80, command=self.pagina_siguiente)
        self.btn_next.grid(row=0, column=2, padx=10)

        self.cargar_datos_db()

    def crear_tabla(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=40, font=("Arial", 14))
        style.configure("Treeview.Heading", font=("Arial", 15, "bold"), background="#333", foreground="white")
        
        self.tabla = ttk.Treeview(self.frame_tabla, columns=("Nro", "Fecha", "Detalle", "Cant", "P_Unit", "Egreso", "ID"), show="headings")
        
        encabezados = [("Nro", 50), ("Fecha", 120), ("Detalle", 350), ("Cant", 80), ("P_Unit", 120), ("Egreso", 120)]
        for col, ancho in encabezados:
            self.tabla.heading(col, text=col if col != "P_Unit" else "P. Unit")
            self.tabla.column(col, width=ancho, anchor="center")
            
        self.tabla.column("Detalle", anchor="w")
        self.tabla.column("ID", width=0, stretch=False)

        self.tabla.pack(side="left", fill="both", expand=True)
        scrolly = ttk.Scrollbar(self.frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrolly.set)
        scrolly.pack(side="right", fill="y")

    def abrir_modal_ingreso(self, editar_datos=None):
        modal = ctk.CTkToplevel(self)
        modal.title("Registro de Gasto")
        modal.geometry("400x550")
        modal.grab_set()

        ctk.CTkLabel(modal, text="DETALLE DEL GASTO", font=("Arial", 18, "bold")).pack(pady=20)

        entry_fecha = ctk.CTkEntry(modal, placeholder_text="DD-MM-YYYY", width=250)
        entry_fecha.pack(pady=10)
        entry_fecha.insert(0, datetime.now().strftime("%d-%m-%Y"))

        entry_detalle = ctk.CTkEntry(modal, placeholder_text="Descripción", width=250)
        entry_detalle.pack(pady=10)

        entry_cantidad = ctk.CTkEntry(modal, placeholder_text="Cantidad (Entero)", width=250)
        entry_cantidad.pack(pady=10)

        entry_p_unit = ctk.CTkEntry(modal, placeholder_text="Precio Unitario ($)", width=250)
        entry_p_unit.pack(pady=10)

        if editar_datos:
            # Índices de la tabla: 0:Nro, 1:Fecha, 2:Detalle, 3:Cant, 4:P_Unit, 5:Egreso, 6:ID
            entry_fecha.delete(0, 'end')
            entry_fecha.insert(0, editar_datos[1])
            entry_detalle.insert(0, editar_datos[2])
            entry_cantidad.insert(0, editar_datos[3])
            # Limpiar precio para que float() sea posible
            p_limpio = str(editar_datos[4]).replace("$", "").replace(",", "").strip()
            entry_p_unit.insert(0, p_limpio)

        def guardar():
            try:
                fecha_db = datetime.strptime(entry_fecha.get(), "%d-%m-%Y").strftime("%Y-%m-%d")
                detalle = entry_detalle.get()
                cantidad = int(entry_cantidad.get())
                p_unit = float(entry_p_unit.get())
                importe_total = cantidad * p_unit

                if not detalle: raise ValueError

                with sqlite3.connect("gimnasio.db") as conn:
                    cursor = conn.cursor()
                    if editar_datos:
                        # El ID real está en el índice 6
                        cursor.execute("""UPDATE egresos SET fecha=?, detalle=?, cantidad=?, p_unit=?, importe=? 
                                          WHERE id=?""", (fecha_db, detalle, cantidad, p_unit, importe_total, editar_datos[6]))
                    else:
                        cursor.execute("""INSERT INTO egresos (fecha, detalle, cantidad, p_unit, importe) 
                                          VALUES (?,?,?,?,?)""", (fecha_db, detalle, cantidad, p_unit, importe_total))
                    conn.commit()
                modal.destroy()
                self.cargar_datos_db()
            except ValueError:
                messagebox.showerror("Error", "Datos inválidos. Verifique fecha (DD-MM-YYYY), cantidad y precio.")

        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="ACEPTAR", fg_color="#2ecc71", command=guardar).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="CANCELAR", fg_color="#e74c3c", command=modal.destroy).pack(side="left", padx=10)

    def cargar_datos_db(self):
        busqueda = self.entry_busqueda.get().lower()
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                query = "SELECT fecha, detalle, cantidad, p_unit, importe, id FROM egresos WHERE LOWER(detalle) LIKE ? ORDER BY fecha DESC"
                cursor.execute(query, (f'%{busqueda}%',))
                self.datos_totales = cursor.fetchall()
            
            # El importe total está en la posición 4 de la tupla (fecha, detalle, cant, p_unit, importe, id)
            suma = sum(row[4] for row in self.datos_totales)
            self.label_total_egresos.configure(text=f"TOTAL EGRESOS: ${suma:,.2f}")
            self.actualizar_tabla()
        except Exception as e: print(f"Error DB: {e}")

    def actualizar_tabla(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        inicio = (self.pagina_actual - 1) * self.registros_por_pagina
        fin = inicio + self.registros_por_pagina
        
        for i, (fecha, detalle, cant, p_unit, importe, id_real) in enumerate(self.datos_totales[inicio:fin], start=inicio + 1):
            f_vis = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d-%m-%Y")
            self.tabla.insert("", "end", values=(i, f_vis, detalle, cant, f"$ {p_unit:,.2f}", f"$ {importe:,.2f}", id_real))

        total_pag = max(1, (len(self.datos_totales) + self.registros_por_pagina - 1) // self.registros_por_pagina)
        self.label_paginas.configure(text=f"Página {self.pagina_actual} de {total_pag}")

    def editar_gasto(self):
        item = self.tabla.selection()
        if not item: 
            messagebox.showwarning("Atención", "Seleccione un registro para editar.")
            return
        self.abrir_modal_ingreso(editar_datos=self.tabla.item(item)['values'])

    def eliminar_gasto(self):
        item = self.tabla.selection()
        if not item: return
        datos = self.tabla.item(item)['values']
        if messagebox.askyesno("Confirmar", f"¿Eliminar el gasto '{datos[2]}'?"):
            with sqlite3.connect("gimnasio.db") as conn:
                conn.cursor().execute("DELETE FROM egresos WHERE id=?", (datos[6],))
                conn.commit()
            self.cargar_datos_db()

    def restablecer_base_datos(self):
        if messagebox.askyesno("ADVERTENCIA", "¿Desea eliminar TODOS los gastos registrados?"):
            with sqlite3.connect("gimnasio.db") as conn:
                conn.cursor().execute("DELETE FROM egresos")
                conn.commit()
            self.pagina_actual = 1
            self.cargar_datos_db()

    def pagina_siguiente(self):
        total_pag = (len(self.datos_totales) + self.registros_por_pagina - 1) // self.registros_por_pagina
        if self.pagina_actual < total_pag:
            self.pagina_actual += 1
            self.actualizar_tabla()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_tabla()

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Sistema Gym - Control de Gastos")
    root.geometry("1150x750")
    ControlGastos(root).pack(fill="both", expand=True)
    root.mainloop()