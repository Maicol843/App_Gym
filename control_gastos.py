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
        ctk.CTkLabel(self.frame_top, text="GESTIÓN DE EGRESOS", font=("Arial", 28, "bold")).pack(side="left")

        # --- PANEL DE CONTROLES ---
        self.frame_controles = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_controles.pack(pady=10, padx=20, fill="x")

        self.entry_busqueda = ctk.CTkEntry(self.frame_controles, placeholder_text="Buscar por detalle...", width=250)
        self.entry_busqueda.pack(side="left", padx=(0, 10))
        self.entry_busqueda.bind("<KeyRelease>", lambda e: self.cargar_datos_db())

        # Botones de Acción
        self.btn_ingresar = ctk.CTkButton(self.frame_controles, text="+ AGREGAR", width=110, fg_color="#2ecc71", command=self.abrir_modal_ingreso)
        self.btn_ingresar.pack(side="left", padx=5)

        self.btn_editar = ctk.CTkButton(self.frame_controles, text="EDITAR", width=100, fg_color="#3498db", command=self.preparar_edicion)
        self.btn_editar.pack(side="left", padx=5)

        self.btn_eliminar = ctk.CTkButton(self.frame_controles, text="ELIMINAR", width=100, fg_color="#e74c3c", command=self.eliminar_gasto)
        self.btn_eliminar.pack(side="left", padx=5)

        self.btn_reset = ctk.CTkButton(self.frame_controles, text="RESTABLECER", width=120, fg_color="#95a5a6", command=self.restablecer_base_datos)
        self.btn_reset.pack(side="left", padx=5)

        # --- TABLA DE DATOS ---
        self.frame_tabla = ctk.CTkFrame(self)
        self.frame_tabla.pack(pady=10, padx=20, fill="both", expand=True)
        self.crear_tabla_visual()

        # --- RESUMEN (TOTAL DE EGRESOS) ---
        self.frame_resumen = ctk.CTkFrame(self, fg_color="#1a1a1a", height=50)
        self.frame_resumen.pack(pady=5, padx=20, fill="x")
        
        self.lbl_total_egresos = ctk.CTkLabel(self.frame_resumen, text="TOTAL EGRESOS: $ 0.00", 
                                               font=("Arial", 18, "bold"), text_color="#e74c3c")
        self.lbl_total_egresos.pack(side="right", padx=20, pady=10)

        # --- PAGINACIÓN ---
        self.frame_paginacion = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_paginacion.pack(pady=15)

        self.btn_prev = ctk.CTkButton(self.frame_paginacion, text="Anterior", width=80, command=self.pagina_anterior)
        self.btn_prev.grid(row=0, column=0, padx=10)

        self.label_paginas = ctk.CTkLabel(self.frame_paginacion, text="Página 1 de 1")
        self.label_paginas.grid(row=0, column=1, padx=20)

        self.btn_next = ctk.CTkButton(self.frame_paginacion, text="Siguiente", width=80, command=self.pagina_siguiente)
        self.btn_next.grid(row=0, column=2, padx=10)

        self.cargar_datos_db()

    def crear_tabla_visual(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=35)
        style.configure("Treeview.Heading", background="#333", foreground="white", font=("Arial", 12, "bold"))
        
        columnas = ("Nro", "Fecha", "Detalle", "Cant.", "P. Unit", "Importe", "ID")
        self.tabla = ttk.Treeview(self.frame_tabla, columns=columnas, show="headings")
        
        anchos = {"Nro": 50, "Fecha": 120, "Detalle": 300, "Cant.": 80, "P. Unit": 120, "Importe": 150, "ID": 0}
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=anchos[col], anchor="center")
        
        self.tabla.column("ID", width=0, stretch=False)
        self.tabla.pack(side="left", fill="both", expand=True)

    def cargar_datos_db(self):
        termino = self.entry_busqueda.get()
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                query = "SELECT fecha, detalle, cantidad, p_unit, importe, id FROM egresos WHERE detalle LIKE ? ORDER BY fecha DESC"
                cursor.execute(query, (f'%{termino}%',))
                self.datos_totales = cursor.fetchall()
            
            # Calcular el total sumando la columna 'importe' (índice 4)
            suma_total = sum(row[4] for row in self.datos_totales)
            self.lbl_total_egresos.configure(text=f"TOTAL EGRESOS: $ {suma_total:,.2f}")
            
            self.actualizar_tabla()
        except Exception as e:
            print(f"Error: {e}")

    def actualizar_tabla(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        inicio = (self.pagina_actual - 1) * self.registros_por_pagina
        datos_pagina = self.datos_totales[inicio:inicio + self.registros_por_pagina]

        for i, row in enumerate(datos_pagina, start=inicio + 1):
            f_vis = datetime.strptime(row[0], "%Y-%m-%d").strftime("%d-%m-%Y")
            self.tabla.insert("", "end", values=(i, f_vis, row[1], row[2], f"${row[3]:,.2f}", f"${row[4]:,.2f}", row[5]))

        total_pag = max(1, (len(self.datos_totales) + self.registros_por_pagina - 1) // self.registros_por_pagina)
        self.label_paginas.configure(text=f"Página {self.pagina_actual} de {total_pag}")

    def eliminar_gasto(self):
        item = self.tabla.selection()
        if not item:
            messagebox.showwarning("Atención", "Seleccione un registro.")
            return
        datos = self.tabla.item(item)['values']
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{datos[2]}'?"):
            with sqlite3.connect("gimnasio.db") as conn:
                conn.cursor().execute("DELETE FROM egresos WHERE id=?", (datos[6],))
                conn.commit()
            self.cargar_datos_db()

    def preparar_edicion(self):
        item = self.tabla.selection()
        if not item:
            messagebox.showwarning("Atención", "Seleccione un registro.")
            return
        self.abrir_modal_ingreso(editar_datos=self.tabla.item(item)['values'])

    def abrir_modal_ingreso(self, editar_datos=None):
        modal = ctk.CTkToplevel(self)
        modal.title("Gasto")
        modal.geometry("400x500")
        modal.grab_set()

        entry_det = ctk.CTkEntry(modal, placeholder_text="Detalle", width=300)
        entry_det.pack(pady=15)
        entry_cant = ctk.CTkEntry(modal, placeholder_text="Cantidad", width=300)
        entry_cant.pack(pady=15)
        entry_punit = ctk.CTkEntry(modal, placeholder_text="Precio Unitario", width=300)
        entry_punit.pack(pady=15)

        if editar_datos:
            entry_det.insert(0, editar_datos[2])
            entry_cant.insert(0, editar_datos[3])
            p_limpio = str(editar_datos[4]).replace("$", "").replace(",", "")
            entry_punit.insert(0, p_limpio)

        def guardar():
            try:
                det = entry_det.get()
                cant = int(entry_cant.get())
                p_u = float(entry_punit.get())
                imp = cant * p_u
                fec = datetime.now().strftime("%Y-%m-%d")

                with sqlite3.connect("gimnasio.db") as conn:
                    cursor = conn.cursor()
                    if editar_datos:
                        cursor.execute("UPDATE egresos SET detalle=?, cantidad=?, p_unit=?, importe=? WHERE id=?",
                                       (det, cant, p_u, imp, editar_datos[6]))
                    else:
                        cursor.execute("INSERT INTO egresos (fecha, detalle, cantidad, p_unit, importe) VALUES (?,?,?,?,?)",
                                       (fec, det, cant, p_u, imp))
                    conn.commit()
                self.cargar_datos_db()
                modal.destroy()
            except:
                messagebox.showerror("Error", "Datos inválidos.")

        ctk.CTkButton(modal, text="GUARDAR", command=guardar).pack(pady=20)

    def restablecer_base_datos(self):
        if messagebox.askyesno("ADVERTENCIA", "¿Borrar TODOS los egresos?"):
            with sqlite3.connect("gimnasio.db") as conn:
                conn.cursor().execute("DELETE FROM egresos")
                conn.commit()
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