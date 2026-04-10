import customtkinter as ctk
from tkinter import messagebox, filedialog
import sqlite3
import os
import shutil
from PIL import Image
from datetime import datetime

class VerRutinas(ctk.CTkFrame):
    def __init__(self, parent, id_cliente):
        super().__init__(parent, fg_color="transparent")
        self.id_cliente = id_cliente
        self.ruta_imagen_temp = None
        self.carpeta_imagenes = "img_rutinas"
        
        # Diccionario para mantener las imágenes en memoria (evita que desaparezcan visualmente)
        self.imagenes_dict = {}

        if not os.path.exists(self.carpeta_imagenes):
            os.makedirs(self.carpeta_imagenes)
        
        # --- CABECERA ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(pady=20, padx=20, fill="x")
        ctk.CTkLabel(self.frame_top, text="RUTINAS PERSONALIZADAS", font=("Arial", 28, "bold")).pack(side="left")
        
        ctk.CTkButton(self.frame_top, text="RESTABLECER", fg_color="#555", 
                       width=100, command=self.restablecer_rutinas_cliente).pack(side="right", padx=10)

        ctk.CTkButton(self.frame_top, text="+ CREAR RUTINA", fg_color="#27ae60", 
                        font=("Arial", 14, "bold"), command=self.abrir_modal_rutina).pack(side="right", padx=10)
        
        # --- CONTENEDOR PRINCIPAL ---
        self.container_rutinas = ctk.CTkScrollableFrame(self, fg_color="#1a1a1a")
        self.container_rutinas.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Configurar columnas para que se expandan uniformemente (2 filas x 3 columnas)
        for i in range(3):
            self.container_rutinas.grid_columnconfigure(i, weight=1)

        self.cargar_rutinas_grid()

    def cargar_rutinas_grid(self):
        for widget in self.container_rutinas.winfo_children():
            widget.destroy()

        dias_semana = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]
        for i, dia in enumerate(dias_semana):
            frame_dia = ctk.CTkFrame(self.container_rutinas, fg_color="#2b2b2b", corner_radius=10)
            frame_dia.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
            
            ctk.CTkLabel(frame_dia, text=dia.upper(), font=("Arial", 14, "bold"), 
                         fg_color="#333", corner_radius=5).pack(fill="x", pady=5, padx=5)
            self.dibujar_ejercicios_dia(frame_dia, dia)

    def dibujar_ejercicios_dia(self, frame, dia):
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, ejercicio FROM rutinas WHERE id_cliente = ? AND dias LIKE ?", 
                               (self.id_cliente, f'%{dia}%'))
                for id_rut, nombre_ej in cursor.fetchall():
                    btn_ej = ctk.CTkButton(frame, text=f"• {nombre_ej}", fg_color="transparent", 
                                           text_color="#3498db", hover_color="#3d3d3d", 
                                           anchor="w", font=("Arial", 13, "underline"),
                                           command=lambda r=id_rut: self.ver_detalle_rutina(r))
                    btn_ej.pack(fill="x", padx=10, pady=2)
        except Exception as e:
            print(f"Error cargando ejercicios: {e}")

    def abrir_modal_rutina(self, editar_id=None):
        modal = ctk.CTkToplevel(self)
        modal.title("Configuración de Rutina")
        modal.geometry("500x750")
        
        # --- VENTANA SIEMPRE ADELANTE ---
        modal.attributes('-topmost', True)
        modal.lift()
        modal.grab_set()
        modal.after(100, lambda: modal.focus_force())

        ctk.CTkLabel(modal, text="DATOS DEL EJERCICIO", font=("Arial", 20, "bold")).pack(pady=15)

        entry_rutina = ctk.CTkEntry(modal, placeholder_text="Nombre de la Rutina (Ej: Rutina Volumen)", width=350)
        entry_rutina.pack(pady=5)
        entry_ejercicio = ctk.CTkEntry(modal, placeholder_text="Nombre del Ejercicio", width=350)
        entry_ejercicio.pack(pady=5)

        f_nums = ctk.CTkFrame(modal, fg_color="transparent")
        f_nums.pack(pady=5)
        entry_series = ctk.CTkEntry(f_nums, placeholder_text="Series", width=170)
        entry_series.pack(side="left", padx=5)
        entry_reps = ctk.CTkEntry(f_nums, placeholder_text="Repeticiones", width=170)
        entry_reps.pack(side="left", padx=5)

        entry_grupo = ctk.CTkEntry(modal, placeholder_text="Grupo Muscular (Ej: Espalda)", width=350)
        entry_grupo.pack(pady=5)

        frame_dias = ctk.CTkFrame(modal); frame_dias.pack(pady=10, padx=20)
        dias_vars = {}
        dias_nombres = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]
        for i, d in enumerate(dias_nombres):
            var = ctk.StringVar(value="off")
            cb = ctk.CTkCheckBox(frame_dias, text=d, variable=var, onvalue=d, offvalue="off")
            cb.grid(row=i//3, column=i%3, padx=10, pady=10)
            dias_vars[d] = var

        self.ruta_imagen_temp = None
        label_status_img = ctk.CTkLabel(modal, text="Sin imagen seleccionada", font=("Arial", 10))
        
        def seleccionar():
            # FILTRO SOLO JPG Y PNG
            path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.png *.jpeg")])
            if path:
                self.ruta_imagen_temp = path
                label_status_img.configure(text=f"Nueva: {os.path.basename(path)}", text_color="#2ecc71")

        ctk.CTkButton(modal, text="📂 Seleccionar Imagen", command=seleccionar).pack(pady=5)
        label_status_img.pack()

        img_previa = None
        if editar_id:
            with sqlite3.connect("gimnasio.db") as conn:
                r = conn.cursor().execute("SELECT * FROM rutinas WHERE id=?", (editar_id,)).fetchone()
                if r:
                    entry_rutina.insert(0, str(r[1]))
                    entry_ejercicio.insert(0, str(r[2]))
                    entry_series.insert(0, str(r[3]))
                    entry_reps.insert(0, str(r[4]))
                    entry_grupo.insert(0, str(r[5]))
                    img_previa = r[6] # Guardamos la ruta existente
                    if img_previa and isinstance(img_previa, str) and os.path.exists(img_previa):
                        label_status_img.configure(text=f"Actual: {os.path.basename(img_previa)}")
                    for d in (r[7].split(",") if r[7] else []):
                        if d in dias_vars: dias_vars[d].set(d)

        def guardar():
            dias_sel = [v.get() for v in dias_vars.values() if v.get() != "off"]
            if not dias_sel or not entry_ejercicio.get(): 
                messagebox.showwarning("Atención", "Nombre del ejercicio y al menos un día son obligatorios.")
                return
            
            # --- LÓGICA DE IMAGEN MEJORADA ---
            ruta_final = img_previa # Por defecto, mantenemos la anterior si es edición
            if self.ruta_imagen_temp:
                try:
                    ext = os.path.splitext(self.ruta_imagen_temp)[1]
                    nombre_unico = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                    ruta_destino = os.path.join(self.carpeta_imagenes, nombre_unico)
                    
                    # Copiamos la nueva imagen al directorio local
                    shutil.copy2(self.ruta_imagen_temp, ruta_destino)
                    ruta_final = ruta_destino # Guardamos la nueva ruta
                    
                    # Opcional: Podrías borrar la imagen física anterior si quieres ahorrar espacio
                except Exception as e: print(f"Error copia: {e}")

            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                if editar_id:
                    cursor.execute("""UPDATE rutinas SET nombre_rutina=?, ejercicio=?, series=?, 
                                      repeticiones=?, grupo_muscular=?, dias=?, imagen_path=? 
                                      WHERE id=?""",
                                   (entry_rutina.get(), entry_ejercicio.get(), entry_series.get(),
                                    entry_reps.get(), entry_grupo.get(), ",".join(dias_sel), ruta_final, editar_id))
                else:
                    cursor.execute("""INSERT INTO rutinas (id_cliente, nombre_rutina, ejercicio, series, 
                                      repeticiones, grupo_muscular, dias, imagen_path) 
                                      VALUES (?,?,?,?,?,?,?,?)""",
                                   (self.id_cliente, entry_rutina.get(), entry_ejercicio.get(), 
                                    entry_series.get(), entry_reps.get(), entry_grupo.get(), ",".join(dias_sel), ruta_final))
            modal.destroy()
            self.cargar_rutinas_grid()

        btn_f = ctk.CTkFrame(modal, fg_color="transparent"); btn_f.pack(pady=20)
        ctk.CTkButton(btn_f, text="GUARDAR", fg_color="#2ecc71", width=120, command=guardar).pack(side="left", padx=10)
        ctk.CTkButton(btn_f, text="CANCELAR", fg_color="#e74c3c", width=120, command=modal.destroy).pack(side="left", padx=10)

    def ver_detalle_rutina(self, id_rutina):
        with sqlite3.connect("gimnasio.db") as conn:
            # --- DESORDEN DATOS: SELECCIÓN EXPLICITA ---
            # Seleccionamos las columnas en orden fijo para asegurar los índices
            r = conn.cursor().execute("SELECT id, id_cliente, nombre_rutina, ejercicio, series, repeticiones, grupo_muscular, dias, imagen_path FROM rutinas WHERE id=?", (id_rutina,)).fetchone()

        if not r: return

        modal = ctk.CTkToplevel(self)
        modal.title("Detalle del Ejercicio")
        modal.geometry("500x700")
        
        # Mantener ventana al frente
        modal.lift()
        modal.attributes('-topmost', True)
        modal.grab_set()
        modal.after(100, lambda: modal.focus_force())

        # Asignación de índices CORREGIDA basada en la consulta de arriba
        # r[2] es nombre_rutina, r[3] ejercicio, r[4] series, r[5] reps, r[6] grupo, r[8] imagen
        ctk.CTkLabel(modal, text=(r[2] or "RUTINA").upper(), font=("Arial", 22, "bold"), text_color="#e67e22").pack(pady=15)
        
        info_frame = ctk.CTkFrame(modal, fg_color="#222", corner_radius=10)
        info_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(info_frame, text=f"Ejercicio: {r[3]}", font=("Arial", 18, "bold")).pack(pady=5)
        ctk.CTkLabel(info_frame, text=f"Músculo: {r[6]}", font=("Arial", 14)).pack()
        ctk.CTkLabel(info_frame, text=f"{r[4]} Series x {r[5]} Repeticiones", font=("Arial", 18, "bold"), text_color="#2ecc71").pack(pady=10)

        # MOSTRAR IMAGEN DESDE LA CARPETA
        ruta_img = r[8]
        if ruta_img and isinstance(ruta_img, str) and os.path.exists(ruta_img):
            try:
                img_raw = Image.open(ruta_img)
                # Convertimos RGB para compatibilidad total con el modo oscuro
                if img_raw.mode in ("RGBA", "P"): img_raw = img_raw.convert("RGB")
                
                # Crear imagen CTk
                img_ctk = ctk.CTkImage(light_image=img_raw, dark_image=img_raw, size=(380, 260))
                
                label_img = ctk.CTkLabel(modal, image=img_ctk, text="")
                # CRITICO: Guardar referencia en el widget para evitar Garbage Collection
                label_img._image = img_ctk 
                label_img.pack(pady=10)
            except Exception as e:
                ctk.CTkLabel(modal, text=f"Error al abrir la imagen").pack()
                print(f"Error de Pillow: {e}")
        else:
            ctk.CTkLabel(modal, text="(Sin imagen o archivo no encontrado)", text_color="gray").pack(pady=20)

        btn_f = ctk.CTkFrame(modal, fg_color="transparent"); btn_f.pack(pady=20)
        
        def eliminar():
            if messagebox.askyesno("Confirmar", "¿Eliminar ejercicio?"):
                with sqlite3.connect("gimnasio.db") as conn:
                    conn.cursor().execute("DELETE FROM rutinas WHERE id=?", (id_rutina,))
                modal.destroy(); self.cargar_rutinas_grid()

        # Botón EDITAR abre modal y cierra este de detalle
        ctk.CTkButton(btn_f, text="EDITAR", fg_color="#3498db", command=lambda: [modal.destroy(), self.abrir_modal_rutina(id_rutina)]).pack(side="left", padx=10)
        ctk.CTkButton(btn_f, text="ELIMINAR", fg_color="#e74c3c", command=eliminar).pack(side="left", padx=10)

    def restablecer_rutinas_cliente(self):
        if messagebox.askyesno("Atención", "¿Borrar todas las rutinas de este cliente?"):
            with sqlite3.connect("gimnasio.db") as conn:
                conn.cursor().execute("DELETE FROM rutinas WHERE id_cliente = ?", (self.id_cliente,))
            self.cargar_rutinas_grid()