import customtkinter as ctk
import sqlite3
from database import crear_base_de_datos
import os
import sys
# Importación de los módulos (Paneles)
from gestion_gimnasio import GestionGimnasio
from registro_clientes import RegistroClientes
from clientes import VentanaClientes
from gestion_membresia import GestionMembresia
from control_ingresos import VentanaIngresos
from control_gastos import ControlGastos

class AplicacionPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la Ventana Principal
        self.title("SISTEMA DE GESTIÓN DE GIMNASIO")
        self.geometry("1300x850")
        ctk.set_appearance_mode("dark")

        # Ruta dinámica para el icono
        if hasattr(sys, '_MEIPASS'):
            # Si el programa está ejecutándose como .exe
            ruta_icono = os.path.join(sys._MEIPASS, "img/logo.ico")
        else:
            # Si lo corres desde Python normal
            ruta_icono = os.path.join("img", "logo.ico")

        try:
            self.iconbitmap(ruta_icono)
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")

        # Inicializar base de datos
        crear_base_de_datos()

        # --- BARRA DE NAVEGACIÓN SUPERIOR ---
        self.nav_frame = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color="#1a1a1a")
        self.nav_frame.pack(side="top", fill="x")
        
        # Contenedor interno para centrar los botones
        self.menu_container = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
        self.menu_container.pack(expand=True) # Este expand=True es la clave para centrar

        self.crear_menu()

        # --- CONTENEDOR DE PÁGINAS (Área variable) ---
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Cargar la página de inicio por defecto
        self.mostrar_inicio()

    def crear_menu(self):
        # Definición de botones: (Texto, Función, Color)
        menu_items = [
            ("INICIO", self.mostrar_inicio, "#34495e"),
            ("GESTIÓN", self.mostrar_plan, "#34495e"),
            ("REGISTROS", self.mostrar_registro, "#34495e"),
            ("CLIENTES", self.mostrar_clientes, "#34495e"),
            ("MEMBRESÍAS", self.mostrar_membresia, "#34495e"),
            ("INGRESOS", self.mostrar_ingresos, "#2ecc71"),
            ("EGRESOS", self.mostrar_egresos, "#e74c3c")
        ]

        for texto, comando, color in menu_items:
            # Los botones se empaquetan dentro de self.menu_container
            btn = ctk.CTkButton(self.menu_container, text=texto, command=comando, 
                                fg_color=color, hover_color="#5dade2",
                                width=140, height=45, font=("Arial", 12, "bold"))
            btn.pack(side="left", padx=10, pady=12)

    def limpiar_y_mostrar(self, ClaseVista):
        """Borra el contenido actual y carga la nueva vista"""
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Se pasa 'self.container' como padre a las vistas
        nueva_vista = ClaseVista(self.container)
        nueva_vista.pack(fill="both", expand=True)

    def mostrar_inicio(self):
        # Esto limpia el contenedor
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Crea la vista de inicio
        nueva_vista = VistaDashboardInterno(self.container)
        nueva_vista.pack(fill="both", expand=True)
        
        # FORZAR REFRESCO: Llama a refrescar_datos apenas se crea
        nueva_vista.refrescar_datos()

    def mostrar_plan(self):
        self.limpiar_y_mostrar(GestionGimnasio)

    def mostrar_registro(self):
        self.limpiar_y_mostrar(RegistroClientes)

    def mostrar_clientes(self):
        self.limpiar_y_mostrar(VentanaClientes)

    def mostrar_membresia(self):
        self.limpiar_y_mostrar(GestionMembresia)

    def mostrar_ingresos(self):
        self.limpiar_y_mostrar(VentanaIngresos)

    def mostrar_egresos(self):
        self.limpiar_y_mostrar(ControlGastos)

# --- CLASE PARA LA VISTA DE TARJETAS ---
class VistaDashboardInterno(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.label_titulo = ctk.CTkLabel(self, text="💪 SISTEMA GYM", font=("Arial", 30, "bold"))
        self.label_titulo.pack(pady=20)

        self.frame_tarjetas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tarjetas.pack(expand=True, fill="both", padx=50)

        self.crear_interfaz_tarjetas()
        
        # Botón de actualización
        self.btn_actualizar = ctk.CTkButton(self, text="ACTUALIZAR DATOS", 
                                            command=self.refrescar_datos,
                                            fg_color="#34495e", hover_color="#2c3e50",
                                            width=200, height=40, font=("Arial", 13, "bold"))
        self.btn_actualizar.pack(pady=20)

        self.refrescar_datos()

    def crear_interfaz_tarjetas(self):
        self.frame_tarjetas.columnconfigure((0, 1), weight=1)
        self.frame_tarjetas.rowconfigure((0, 1), weight=1)

        self.lbl_clientes = self.crear_tarjeta("CLIENTES ACTIVOS", "#3498db", 0, 0)
        self.lbl_ingresos = self.crear_tarjeta("TOTAL INGRESOS", "#2ecc71", 0, 1)
        self.lbl_egresos = self.crear_tarjeta("TOTAL EGRESOS", "#e74c3c", 1, 0)
        self.lbl_ganancia = self.crear_tarjeta("BALANCE NETO", "#f39c12", 1, 1)

    def crear_tarjeta(self, titulo, color, f, c):
        fr = ctk.CTkFrame(self.frame_tarjetas, fg_color="#2b2b2b", border_color=color, border_width=2)
        fr.grid(row=f, column=c, padx=20, pady=20, sticky="nsew")
        ctk.CTkLabel(fr, text=titulo, font=("Arial", 16, "bold"), text_color="gray").pack(pady=(20, 5))
        valor_label = ctk.CTkLabel(fr, text="...", font=("Arial", 35, "bold"))
        valor_label.pack(pady=(5, 25))
        return valor_label

    def refrescar_datos(self):
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM clientes")
                cant_clientes = cursor.fetchone()[0]
                
                cursor.execute("SELECT SUM(monto) FROM ingresos")
                suma_ingresos = cursor.fetchone()[0] or 0.0
                
                cursor.execute("SELECT SUM(importe) FROM egresos")
                suma_egresos = cursor.fetchone()[0] or 0.0
                
                balance = suma_ingresos - suma_egresos

                self.lbl_clientes.configure(text=str(cant_clientes))
                self.lbl_ingresos.configure(text=f"$ {suma_ingresos:,.2f}")
                self.lbl_egresos.configure(text=f"$ {suma_egresos:,.2f}")
                self.lbl_ganancia.configure(text=f"$ {balance:,.2f}")
                
                color_balance = "#2ecc71" if balance >= 0 else "#e74c3c"
                self.lbl_ganancia.configure(text_color=color_balance)
        except Exception as e:
            print(f"Error al refrescar datos: {e}")

if __name__ == "__main__":
    app = AplicacionPrincipal()
    app.mainloop()