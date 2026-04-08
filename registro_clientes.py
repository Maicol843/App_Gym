import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime

class RegistroClientes(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema Gym - Registro de Clientes")
        self.geometry("800x850") # Un poco más ancho para las dos columnas
        ctk.set_appearance_mode("dark")

        # --- Contenedor con Scroll ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=750, height=800)
        self.scroll_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.crear_widgets()

    def crear_widgets(self):
        # Título centrado
        ctk.CTkLabel(self.scroll_frame, text="FICHA DE INSCRIPCIÓN", 
                     font=("Arial", 24, "bold")).pack(pady=20)

        # --- SECCIÓN: DATOS PERSONALES ---
        self.seccion_titulo("Datos Personales")
        
        # Creamos un frame para organizar los inputs en cuadrícula
        self.frame_datos = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.frame_datos.pack(pady=10, padx=20)

        self.entry_nombre = self.crear_campo_grid(self.frame_datos, "Nombre:", 0, 0)
        self.entry_apellido = self.crear_campo_grid(self.frame_datos, "Apellido:", 0, 1)
        self.entry_domicilio = self.crear_campo_grid(self.frame_datos, "Domicilio:", 1, 0)
        self.entry_telefono = self.crear_campo_grid(self.frame_datos, "Teléfono:", 1, 1)
        
        # Fecha de Nacimiento y Edad (en una fila propia del grid)
        self.label_nac = ctk.CTkLabel(self.frame_datos, text="Fecha Nac. (DD-MM-AAAA):")
        self.label_nac.grid(row=2, column=0, pady=(10, 0), padx=20, sticky="w")
        self.entry_nacimiento = ctk.CTkEntry(self.frame_datos, width=200, placeholder_text="07-04-1989")
        self.entry_nacimiento.grid(row=3, column=0, pady=5, padx=20, sticky="w")
        self.entry_nacimiento.bind("<FocusOut>", self.calcular_edad)

        self.label_edad = ctk.CTkLabel(self.frame_datos, text="Edad: --", font=("Arial", 12, "bold"), text_color="cyan")
        self.label_edad.grid(row=3, column=1, pady=5, padx=20, sticky="w")

        # --- SECCIÓN: DATOS FÍSICOS ---
        self.seccion_titulo("Datos Físicos")
        self.frame_fisicos = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.frame_fisicos.pack(pady=10, padx=20)

        self.entry_altura = self.crear_campo_grid(self.frame_fisicos, "Altura (cm):", 0, 0)
        self.entry_peso = self.crear_campo_grid(self.frame_fisicos, "Peso (kg):", 0, 1)
        
        ctk.CTkLabel(self.frame_fisicos, text="Grupo Sanguíneo:").grid(row=1, column=0, pady=(10,0), padx=20, sticky="w")
        self.combo_sangre = ctk.CTkOptionMenu(self.frame_fisicos, width=200, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "0+", "0-"])
        self.combo_sangre.grid(row=2, column=0, pady=5, padx=20, sticky="w")

        # --- SECCIÓN: FICHA MÉDICA (Doble Columna) ---
        self.seccion_titulo("Ficha Médica")
        self.frame_medico = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.frame_medico.pack(pady=10, padx=10)
        
        self.var_columna, self.txt_columna = self.crear_pregunta_grid(self.frame_medico, "¿Patología columna?", 0, 0)
        self.var_cardiaco, self.txt_cardiaco = self.crear_pregunta_grid(self.frame_medico, "¿Enf. cardíacas?", 0, 1)
        self.var_lesion, self.txt_lesion = self.crear_pregunta_grid(self.frame_medico, "¿Posee lesiones?", 1, 0)
        self.var_deporte, self.txt_deporte = self.crear_pregunta_grid(self.frame_medico, "¿Practica deportes?", 1, 1)

        # --- SECCIÓN: SÍNTOMAS ---
        self.seccion_titulo("Síntomas y Otros")
        self.frame_switches = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.frame_switches.pack(pady=10)

        # Organizar switches en 2 columnas
        sw_list = [
            ("¿Sufre mareos?", "var_mareos"), ("¿Dolor de cabeza?", "var_cabeza"),
            ("¿Desmayos?", "var_desmayos"), ("¿Hemorragias?", "var_nasal"),
            ("¿Dolores articulares?", "var_articular"), ("¿Otra alteración?", "var_alteracion"),
            ("¿Rodilla/Tobillo?", "var_rodilla"), ("¿Convulsiones?", "var_convulsion")
        ]
        
        for i, (texto, var_name) in enumerate(sw_list):
            var = ctk.IntVar(value=0)
            setattr(self, var_name, var)
            sw = ctk.CTkSwitch(self.frame_switches, text=texto, variable=var)
            sw.grid(row=i//2, column=i%2, padx=30, pady=5, sticky="w")

        # --- BOTÓN REGISTRAR ---
        self.btn_registrar = ctk.CTkButton(self.scroll_frame, text="REGISTRAR CLIENTE", 
                                           width=300, height=50, font=("Arial", 16, "bold"),
                                           fg_color="green", hover_color="darkgreen", command=self.guardar_datos)
        self.btn_registrar.pack(pady=40)

    # --- FUNCIONES AUXILIARES OPTIMIZADAS ---
    def seccion_titulo(self, texto):
        ctk.CTkLabel(self.scroll_frame, text=texto, font=("Arial", 18, "bold"), text_color="#FFCC00").pack(pady=(20, 5))

    def crear_campo_grid(self, parent, label_text, row, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, padx=15, pady=5, sticky="nsew")
        
        ctk.CTkLabel(frame, text=label_text).pack(anchor="w")
        entry = ctk.CTkEntry(frame, width=220)
        entry.pack(pady=2)
        return entry

    def crear_pregunta_grid(self, parent, pregunta, row, col):
        var = ctk.IntVar(value=0)
        frame = ctk.CTkFrame(parent, fg_color="transparent", border_width=1, border_color="#444")
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(frame, text=pregunta, font=("Arial", 12, "bold")).pack(pady=5)
        
        f_radio = ctk.CTkFrame(frame, fg_color="transparent")
        f_radio.pack()
        ctk.CTkRadioButton(f_radio, text="No", variable=var, value=0).pack(side="left", padx=10)
        ctk.CTkRadioButton(f_radio, text="Sí", variable=var, value=1).pack(side="left", padx=10)
        
        txt = ctk.CTkTextbox(frame, width=280, height=60)
        txt.pack(pady=10, padx=10)
        txt.insert("1.0", "Especifique aquí...")
        return var, txt

    # (Las funciones de calcular_edad, guardar_datos y limpiar_formulario se mantienen igual que la versión anterior)
    def calcular_edad(self, event=None):
        try:
            fecha_str = self.entry_nacimiento.get()
            dia_nac, mes_nac, año_nac = map(int, fecha_str.split("-"))
            hoy = datetime.now()
            edad = hoy.year - año_nac
            ya_cumplio = (hoy.month, hoy.day) >= (mes_nac, dia_nac)
            if not ya_cumplio: edad -= 1
            self.label_edad.configure(text=f"Edad: {edad}", text_color="cyan")
            return edad
        except:
            self.label_edad.configure(text="Edad: --", text_color="red")
            return 0

    def guardar_datos(self):
        try:
            def limpiar_texto_ayuda(txt_widget):
                contenido = txt_widget.get("1.0", "end-1c").strip()
                return "" if contenido == "Especifique aquí..." or contenido == "" else contenido

            nombre, apellido = self.entry_nombre.get().strip(), self.entry_apellido.get().strip()
            if not nombre or not apellido: raise ValueError("Nombre y Apellido obligatorios")

            f_nac_raw = self.entry_nacimiento.get().strip()
            fecha_bd = datetime.strptime(f_nac_raw, "%d-%m-%Y").strftime("%Y-%m-%d")
            edad = self.calcular_edad()

            datos = (
                nombre, apellido, self.entry_domicilio.get(), self.entry_telefono.get(), 
                fecha_bd, edad, float(self.entry_altura.get() or 0), float(self.entry_peso.get() or 0),
                self.combo_sangre.get(), self.var_columna.get(), limpiar_texto_ayuda(self.txt_columna),
                self.var_cardiaco.get(), limpiar_texto_ayuda(self.txt_cardiaco),
                self.var_lesion.get(), limpiar_texto_ayuda(self.txt_lesion),
                self.var_deporte.get(), limpiar_texto_ayuda(self.txt_deporte),
                self.var_mareos.get(), self.var_cabeza.get(), self.var_desmayos.get(),
                self.var_nasal.get(), self.var_articular.get(), self.var_alteracion.get(),
                self.var_rodilla.get(), self.var_convulsion.get(), datetime.now().strftime("%Y-%m-%d")
            )

            with sqlite3.connect("gimnasio.db", timeout=20) as conexion:
                cursor = conexion.cursor()
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute('''INSERT INTO clientes (nombre, apellido, domicilio, telefono, fecha_nacimiento, edad, altura, peso, grupo_sanguineo, patologia_columna, detalle_columna, enfermedades_cardiacas, detalle_cardiaco, lesiones, detalle_lesion, deportes, detalle_deporte, mareos, dolor_cabeza, desmayos, hemorragias_nasales, dolores_articulares, alteracion, problemas_rodilla_tobillo, convulsiones, fecha_inscripcion) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', datos)
                conexion.commit()
            
            messagebox.showinfo("Éxito", "Cliente registrado")
            self.limpiar_formulario()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def limpiar_formulario(self):
        for entry in [self.entry_nombre, self.entry_apellido, self.entry_domicilio, self.entry_telefono, self.entry_nacimiento, self.entry_altura, self.entry_peso]:
            entry.delete(0, 'end')
        self.label_edad.configure(text="Edad: --")
        for v in [self.var_columna, self.var_cardiaco, self.var_lesion, self.var_deporte, self.var_mareos, self.var_cabeza, self.var_desmayos, self.var_nasal, self.var_articular, self.var_alteracion, self.var_rodilla, self.var_convulsion]:
            v.set(0)
        for t in [self.txt_columna, self.txt_cardiaco, self.txt_lesion, self.txt_deporte]:
            t.delete("1.0", "end")
            t.insert("1.0", "Especifique aquí...")
        self.scroll_frame._parent_canvas.yview_moveto(0)

if __name__ == "__main__":
    app = RegistroClientes()
    app.mainloop()