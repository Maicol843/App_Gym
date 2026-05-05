import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from database import crear_base_de_datos 

# Librerías para la generación y renderizado de la gráfica
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class VentanaIngresos(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        crear_base_de_datos()
        
        self.pagina_actual = 1
        self.clientes_por_pagina = 10
        self.datos_brutos = [] 
        self.datos_filtrados = [] 
        self.canvas_grafica = None 

        # --- Interfaz de Usuario ---
        self.configurar_interfaz()
        self.cargar_y_procesar_ingresos()

    def configurar_interfaz(self):
        """Configura los elementos visuales de la ventana."""
        # Cabecera
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(pady=(20, 10), padx=20, fill="x")
        ctk.CTkLabel(self.frame_top, text="INGRESOS", font=("Arial", 28, "bold")).pack(side="left")

        # Filtros
        self.frame_filtros = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_filtros.pack(pady=10, padx=20, fill="x")

        self.combo_filtro_plan = ctk.CTkOptionMenu(self.frame_filtros, values=self.obtener_planes_db(),
                                                   command=lambda v: self.aplicar_filtros())
        self.combo_filtro_plan.pack(side="left", padx=5)
        self.combo_filtro_plan.set("Todos")

        self.entry_busqueda = ctk.CTkEntry(self.frame_filtros, placeholder_text="Buscar por nombre...", width=200)
        self.entry_busqueda.pack(side="left", padx=5)
        self.entry_busqueda.bind("<KeyRelease>", lambda e: self.aplicar_filtros())

        self.btn_grafica = ctk.CTkButton(self.frame_filtros, text="Ver gráfica", command=self.alternar_vista_grafica)
        self.btn_grafica.pack(side="left", padx=10)

        # Contenedor para Tabla/Gráfica
        self.contenedor_principal = ctk.CTkFrame(self)
        self.contenedor_principal.pack(pady=10, padx=20, fill="both", expand=True)
        self.crear_tabla()

        # Resumen y Paginación
        self.frame_total = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.frame_total.pack(pady=5, padx=20, fill="x")
        self.label_total_dinero = ctk.CTkLabel(self.frame_total, text="Total Ingresos: $0.00", font=("Arial", 18, "bold"), text_color="#2ecc71")
        self.label_total_dinero.pack(side="right", padx=20, pady=10)

    def cargar_y_procesar_ingresos(self):
        """
        Paso 1: Detecta clientes con pago 'Realizado'.
        Paso 2: Inserta en 'ingresos' usando la 'fecha_inscripcion' del cliente.[cite: 13, 14]
        """
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                # Obtenemos la fecha_inscripcion directamente del cliente
                cursor.execute("""
                    SELECT c.id, c.nombre, c.apellido, c.plan_seleccionado, p.precio, c.fecha_inscripcion
                    FROM clientes c
                    INNER JOIN planes p ON c.plan_seleccionado = p.nombre_plan
                    WHERE c.pago = 'Realizado'
                """)
                pendientes = cursor.fetchall()

                for cli in pendientes:
                    id_db, nom, ape, plan, precio, f_ins = cli
                    
                    # Verificamos si ya existe el registro para evitar duplicados
                    cursor.execute("SELECT id FROM ingresos WHERE id_cliente = ? AND fecha = ?", (id_db, f_ins))
                    
                    if not cursor.fetchone():
                        # Usamos f_ins para que la fecha en ingresos sea la de inscripción
                        cursor.execute("""
                            INSERT INTO ingresos (id_cliente, monto, fecha, detalle) 
                            VALUES (?, ?, ?, ?)
                        """, (id_db, precio, f_ins, f"Pago: {plan}"))
                        
                        # Marcamos como procesado
                        cursor.execute("UPDATE clientes SET pago = 'SÍ' WHERE id = ?", (id_db,))
                
                conn.commit()

                # Consultamos para mostrar en la tabla
                cursor.execute("""
                    SELECT i.fecha, c.nombre, c.apellido, c.plan_seleccionado, i.monto
                    FROM ingresos i
                    INNER JOIN clientes c ON i.id_cliente = c.id
                    ORDER BY i.fecha DESC
                """)
                self.datos_brutos = cursor.fetchall()
                
            self.aplicar_filtros()
        except Exception as e:
            print(f"Error al procesar ingresos: {e}")

    def dibujar_grafica(self):
        """
        Genera la gráfica de barras mostrando los 12 meses (Ene-Dic) y la suma total.[cite: 13]
        """
        meses_labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        totales_por_mes = {i: 0.0 for i in range(1, 13)} # Diccionario para rellenar meses sin datos

        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                # Extraemos el mes de la fecha y sumamos los montos[cite: 13]
                cursor.execute("""
                    SELECT CAST(strftime('%m', fecha) AS INTEGER) as mes, SUM(monto) 
                    FROM ingresos 
                    GROUP BY mes
                """)
                for mes, suma in cursor.fetchall():
                    totales_por_mes[mes] = suma

        except Exception as e:
            messagebox.showerror("Error", f"Error en gráfica: {e}")
            return

        valores = [totales_por_mes[i] for i in range(1, 13)]

        # Configuración de Matplotlib
        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')

        barras = ax.bar(meses_labels, valores, color='#2ecc71')

        # Añadir etiquetas de texto sobre las barras[cite: 13]
        for barra in barras:
            yval = barra.get_height()
            if yval > 0:
                ax.text(barra.get_x() + barra.get_width()/2, yval + 500, f'${yval:,.0f}', 
                        ha='center', va='bottom', color='white', fontweight='bold', fontsize=9)

        ax.set_title("Ingresos Totales por Mes", color='white', fontsize=16)
        ax.tick_params(axis='both', colors='white')

        self.canvas_grafica = FigureCanvasTkAgg(fig, master=self.contenedor_principal)
        self.canvas_grafica.draw()
        self.canvas_grafica.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # --- Métodos de utilidad (Tabla, Filtros, Paginación) ---
    def crear_tabla(self):
        self.frame_tabla = ctk.CTkFrame(self.contenedor_principal, fg_color="transparent")
        self.frame_tabla.pack(fill="both", expand=True)
        self.tabla = ttk.Treeview(self.frame_tabla, columns=("Nro", "Fecha", "Nombre", "Apellido", "Plan", "Ingreso"), show="headings")
        for col in ("Nro", "Fecha", "Nombre", "Apellido", "Plan", "Ingreso"):
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=120)
        self.tabla.pack(side="left", fill="both", expand=True)

    def aplicar_filtros(self):
        self.datos_filtrados = []
        suma = 0.0
        for reg in self.datos_brutos:
            self.datos_filtrados.append(reg)
            suma += reg[4]
        self.label_total_dinero.configure(text=f"TOTAL INGRESOS: ${suma:,.2f}")
        self.actualizar_tabla()

    def actualizar_tabla(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        for i, (fecha, nom, ape, plan, monto) in enumerate(self.datos_filtrados, 1):
            # Formateamos la fecha de inscripción para que se vea bien en la tabla[cite: 13]
            try: f_fmt = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d-%m-%Y")
            except: f_fmt = fecha
            self.tabla.insert("", "end", values=(i, f_fmt, nom, ape, plan, f"${monto:,.2f}"))

    def alternar_vista_grafica(self):
        if self.canvas_grafica:
            self.canvas_grafica.get_tk_widget().destroy()
            self.canvas_grafica = None
            self.frame_tabla.pack(fill="both", expand=True)
            self.btn_grafica.configure(text="Ver gráfica")
        else:
            self.frame_tabla.pack_forget()
            self.btn_grafica.configure(text="Ver tabla")
            self.dibujar_grafica()

    def obtener_planes_db(self):
        return ["Todos"] # Simplificado para el ejemplo

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1100x750")
    VentanaIngresos(root).pack(fill="both", expand=True)
    root.mainloop()