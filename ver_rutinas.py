import customtkinter as ctk
from tkinter import messagebox, filedialog
import sqlite3
import os
import shutil
import webbrowser  # Importado para abrir enlaces en el navegador
from PIL import Image
from datetime import datetime

class VerRutinas(ctk.CTkFrame):
    def __init__(self, parent, id_cliente):
        super().__init__(parent, fg_color="transparent")
        self.id_cliente = id_cliente
        self.carpeta_imagenes = "img_rutinas"
        
        self.tablas_vacias_memoria = []
        
        if not os.path.exists(self.carpeta_imagenes):
            os.makedirs(self.carpeta_imagenes)
        
        # --- BARRA DE ACCIONES PRINCIPAL ---
        self.frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones.pack(pady=15, padx=20, fill="x")

        self.container_botones = ctk.CTkFrame(self.frame_acciones, fg_color="transparent")
        self.container_botones.pack(expand=True)    

        ctk.CTkButton(self.container_botones, text="Crear tabla", fg_color="#0d6efd", 
                      command=self.modal_crear_tabla).pack(side="left", padx=5)
        
        ctk.CTkButton(self.container_botones, text="Eliminar tabla", fg_color="#dc3545", 
                      command=self.modal_eliminar_tabla).pack(side="left", padx=5)
        
        ctk.CTkButton(self.container_botones, text="Restablecer", fg_color="#0AA2C0", 
                      command=self.restablecer_todo).pack(side="left", padx=5)
        
        ctk.CTkButton(self.container_botones, text="Agregar Rutina", fg_color="#fd7e14", 
                      command=lambda: self.modal_configurar_rutina()).pack(side="left", padx=5)

        # --- ÁREA DE TABLAS ---
        self.area_tablas = ctk.CTkScrollableFrame(self, fg_color="#1a1a1a")
        self.area_tablas.pack(pady=10, padx=20, fill="both", expand=True)

        self.cargar_tablas_visuales()

    def abrir_enlace(self, url):
        """Valida y abre el enlace del video en el navegador."""
        if url and (url.startswith("http://") or url.startswith("https://")):
            webbrowser.open(url)
        else:
            messagebox.showwarning("Enlace no válido", "El enlace no es una URL válida o está vacío.")

    def obtener_todos_los_nombres_tablas(self):
        nombres_completos = set(self.tablas_vacias_memoria)
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT nombre_tabla FROM rutinas WHERE id_cliente = ?", (self.id_cliente,))
                for row in cursor.fetchall():
                    nombres_completos.add(row[0])
        except: pass
        return sorted(list(nombres_completos)) if nombres_completos else ["Mi Primera Tabla"]

    def cargar_tablas_visuales(self):
        for widget in self.area_tablas.winfo_children():
            widget.destroy()
        
        todos_los_nombres = self.obtener_todos_los_nombres_tablas()
        
        check_db_vacia = True
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                res = conn.cursor().execute("SELECT id FROM rutinas WHERE id_cliente=?", (self.id_cliente,)).fetchone()
                if res: check_db_vacia = False
        except: pass

        if check_db_vacia and not self.tablas_vacias_memoria:
            return

        for nombre in todos_los_nombres:
            self.crear_diseno_tabla(nombre)

    def crear_diseno_tabla(self, nombre):
        frame_t = ctk.CTkFrame(self.area_tablas, fg_color="#2b2b2b", border_width=2, border_color="#0d6efd", corner_radius=8)
        frame_t.pack(pady=15, padx=10, fill="x")
        ctk.CTkLabel(frame_t, text=nombre.upper(), font=("Arial", 18, "bold"), text_color="#0d6efd").pack(pady=(10, 5))
        
        dias_frame = ctk.CTkFrame(frame_t, fg_color="transparent")
        dias_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        dias_semana = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]
        for i, dia in enumerate(dias_semana):
            col = ctk.CTkFrame(dias_frame, fg_color="#1a1a1a", corner_radius=5)
            col.grid(row=0, column=i, padx=3, sticky="nsew")
            dias_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(col, text=dia, font=("Arial", 12, "bold"), text_color="white").pack(pady=4)
            self.cargar_enlaces_ejercicios(col, nombre, dia)

    def cargar_enlaces_ejercicios(self, parent, tabla, dia):
        try:
            with sqlite3.connect("gimnasio.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, ejercicio FROM rutinas WHERE id_cliente=? AND nombre_tabla=? AND dias LIKE ?", 
                               (self.id_cliente, tabla, f'%{dia}%'))
                for id_reg, nombre_ej in cursor.fetchall():
                    btn = ctk.CTkButton(parent, text=nombre_ej, fg_color="transparent", 
                                        text_color="#0d6efd", hover_color="#2b2b2b", 
                                        height=22, anchor="w", font=("Arial", 11, "underline"),
                                        command=lambda idx=id_reg: self.ver_detalle_ejercicio(idx))
                    btn.pack(fill="x", padx=5, pady=1)
        except: pass

    def modal_configurar_rutina(self, editar_id=None):
        modal = ctk.CTkToplevel(self)
        modal.title("Configurar Rutina")
        modal.geometry("500x820")
        modal.grab_set()
        modal.attributes("-topmost", True)

        scr = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        scr.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(scr, text="DATOS DEL EJERCICIO", font=("Arial", 20, "bold"), text_color="#0d6efd").pack(pady=(10, 15))

        opciones_tablas = self.obtener_todos_los_nombres_tablas()
        combo_tabla = ctk.CTkOptionMenu(scr, values=opciones_tablas, width=350)
        combo_tabla.pack(pady=(5, 15))

        ent_rutina = ctk.CTkEntry(scr, placeholder_text="Nombre de la Rutina", width=350)
        ent_rutina.pack(pady=5)
        ent_ejercicio = ctk.CTkEntry(scr, placeholder_text="Nombre del Ejercicio", width=350)
        ent_ejercicio.pack(pady=5)
        ent_grupo = ctk.CTkEntry(scr, placeholder_text="Grupo Muscular", width=350)
        ent_grupo.pack(pady=5)

        f_info = ctk.CTkFrame(scr, fg_color="transparent")
        f_info.pack(pady=10)
        ent_series = ctk.CTkEntry(f_info, placeholder_text="Series", width=95); ent_series.pack(side="left", padx=3)
        ent_reps = ctk.CTkEntry(f_info, placeholder_text="Reps", width=95); ent_reps.pack(side="left", padx=3)
        ent_peso = ctk.CTkEntry(f_info, placeholder_text="Carga/Peso", width=95); ent_peso.pack(side="left", padx=3)

        vars_dias = {d: ctk.StringVar(value="off") for d in ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]}
        dias_frame = ctk.CTkFrame(scr, fg_color="#1a1a1a", corner_radius=8)
        dias_frame.pack(pady=5, padx=20, fill="x")
        for i, (d, v) in enumerate(vars_dias.items()):
            cb = ctk.CTkCheckBox(dias_frame, text=d, variable=v, onvalue=d, offvalue="off")
            cb.grid(row=i//3, column=i%3, padx=15, pady=10, sticky="w")

        ent_video = ctk.CTkEntry(scr, placeholder_text="Enlace del Video (YouTube/Drive)", width=350)
        ent_video.pack(pady=(15, 5))

        self.ruta_img_temp = None
        img_actual_path = None
        lbl_status_img = ctk.CTkLabel(scr, text="Ninguna imagen seleccionada", font=("Arial", 10), text_color="gray")
        
        def subir_img():
            modal.attributes("-topmost", False)
            p = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.png *.jpeg")])
            modal.attributes("-topmost", True)
            if p:
                self.ruta_img_temp = p
                lbl_status_img.configure(text=f"Nueva imagen: {os.path.basename(p)}", text_color="#0d6efd")

        ctk.CTkButton(scr, text="Subir Imagen (.png, .jpg)", command=subir_img).pack(pady=(20, 5))
        lbl_status_img.pack()

        if editar_id:
            try:
                with sqlite3.connect("gimnasio.db") as conn:
                    conn.row_factory = sqlite3.Row
                    r = conn.cursor().execute("SELECT * FROM rutinas WHERE id=?", (editar_id,)).fetchone()
                    if r:
                        combo_tabla.set(r['nombre_tabla'])
                        ent_rutina.insert(0, r['nombre_rutina'] or "")
                        ent_ejercicio.insert(0, r['ejercicio'])
                        ent_grupo.insert(0, r['grupo_muscular'] or "")
                        ent_series.insert(0, r['series'] or "")
                        ent_reps.insert(0, r['repeticiones'] or "")
                        ent_peso.insert(0, r['carga_peso'] or "")
                        ent_video.insert(0, r['video_link'] or "")
                        img_actual_path = r['imagen_path']
                        dias_db = (r['dias'] or "").split(",")
                        for d in dias_db:
                            if d in vars_dias: vars_dias[d].set(d)
            except: pass

        def guardar():
            tabla_sel = combo_tabla.get()
            ejercicio_nom = ent_ejercicio.get().strip()
            sel_dias = [v.get() for v in vars_dias.values() if v.get() != "off"]
            video_url = ent_video.get().strip()

            if not ejercicio_nom or not sel_dias:
                messagebox.showwarning("Atención", "Nombre del ejercicio y días son obligatorios.", parent=modal)
                return
            
            path_final_imagen = img_actual_path
            if self.ruta_img_temp:
                nombre_unico = f"cli_{self.id_cliente}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{os.path.splitext(self.ruta_img_temp)[1]}"
                path_final_imagen = os.path.join(self.carpeta_imagenes, nombre_unico)
                shutil.copy2(self.ruta_img_temp, path_final_imagen)

            try:
                with sqlite3.connect("gimnasio.db") as conn:
                    cursor = conn.cursor()
                    if editar_id:
                        cursor.execute("""UPDATE rutinas SET nombre_tabla=?, nombre_rutina=?, ejercicio=?, series=?, 
                                          repeticiones=?, grupo_muscular=?, carga_peso=?, dias=?, imagen_path=?, video_link=? WHERE id=?""",
                                       (tabla_sel, ent_rutina.get(), ejercicio_nom, ent_series.get(), ent_reps.get(), 
                                        ent_grupo.get(), ent_peso.get(), ",".join(sel_dias), path_final_imagen, video_url, editar_id))
                    else:
                        cursor.execute("""INSERT INTO rutinas (id_cliente, nombre_tabla, nombre_rutina, ejercicio, 
                                          series, repeticiones, grupo_muscular, carga_peso, dias, imagen_path, video_link) 
                                          VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                                       (self.id_cliente, tabla_sel, ent_rutina.get(), ejercicio_nom,
                                        ent_series.get(), ent_reps.get(), ent_grupo.get(), ent_peso.get(), 
                                        ",".join(sel_dias), path_final_imagen, video_url))
                    conn.commit()
                modal.destroy()
                self.cargar_tablas_visuales()
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al guardar: {e}", parent=modal)

        f_btns = ctk.CTkFrame(scr, fg_color="transparent")
        f_btns.pack(pady=30)
        ctk.CTkButton(f_btns, text="Guardar", fg_color="#198754", command=guardar).pack(side="left", padx=10)
        ctk.CTkButton(f_btns, text="Cancelar", fg_color="#555", command=modal.destroy).pack(side="left", padx=10)

    def ver_detalle_ejercicio(self, id_reg):
        modal = ctk.CTkToplevel(self)
        modal.title("Detalle del Ejercicio")
        modal.geometry("550x750")
        modal.grab_set()
        modal.attributes("-topmost", True)

        try:
            with sqlite3.connect("gimnasio.db") as conn:
                conn.row_factory = sqlite3.Row
                r = conn.cursor().execute("SELECT * FROM rutinas WHERE id=?", (id_reg,)).fetchone()
        except: return

        scr = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        scr.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scr, text=r['ejercicio'], font=("Arial", 26, "bold"), text_color="#0d6efd").pack(pady=(0, 15))
        
        info_frame = ctk.CTkFrame(scr, fg_color="#1a1a1a", corner_radius=8)
        info_frame.pack(fill="x", pady=10)
        
        # Datos a mostrar
        datos = [
            ("Rutina", r['nombre_rutina']), 
            ("Grupo Muscular", r['grupo_muscular']), 
            ("Series", r['series']), 
            ("Repeticiones", r['repeticiones']), 
            ("Carga / Peso", r['carga_peso'])
        ]
        
        for tit, val in datos:
            f = ctk.CTkFrame(info_frame, fg_color="transparent")
            f.pack(fill="x", padx=15, pady=5)
            ctk.CTkLabel(f, text=f"{tit}:", font=("Arial", 12, "bold"), width=120, anchor="w", text_color="#aaa").pack(side="left")
            ctk.CTkLabel(f, text=str(val) if val else "-", font=("Arial", 13)).pack(side="left", padx=5)

        # SECCIÓN DE VIDEO: Botón con apariencia de enlace
        if r['video_link'] and r['video_link'].strip():
            f_video = ctk.CTkFrame(info_frame, fg_color="transparent")
            f_video.pack(fill="x", padx=15, pady=5)
            ctk.CTkLabel(f_video, text="Video:", font=("Arial", 12, "bold"), width=120, anchor="w", text_color="#aaa").pack(side="left")
            
            btn_video = ctk.CTkButton(f_video, text="Ver video tutorial", 
                                      fg_color="transparent", 
                                      text_color="#0d6efd", 
                                      hover_color="#2b2b2b",
                                      font=("Arial", 13, "underline"),
                                      anchor="w",
                                      command=lambda: self.abrir_enlace(r['video_link']))
            btn_video.pack(side="left", padx=5)

        if r['imagen_path'] and os.path.exists(r['imagen_path']):
            try:
                img_p = Image.open(r['imagen_path'])
                img_ctk = ctk.CTkImage(img_p, size=(400, 300))
                ctk.CTkLabel(scr, image=img_ctk, text="").pack(pady=25)
            except: pass

        f_acc = ctk.CTkFrame(scr, fg_color="transparent")
        f_acc.pack(pady=20)
        
        def ir_a_editar():
            modal.destroy()
            self.modal_configurar_rutina(editar_id=id_reg)

        ctk.CTkButton(f_acc, text="Editar", fg_color="#0d6efd", command=ir_a_editar).pack(side="left", padx=10)
        ctk.CTkButton(f_acc, text="Eliminar", fg_color="#dc3545", command=lambda: self.eliminar_ejercicio(id_reg, modal)).pack(side="left", padx=10)

    def eliminar_ejercicio(self, idx, modal_detalle):
        if messagebox.askyesno("Confirmar", "¿Eliminar este ejercicio?", parent=modal_detalle):
            try:
                with sqlite3.connect("gimnasio.db") as conn:
                    conn.cursor().execute("DELETE FROM rutinas WHERE id=?", (idx,))
                    conn.commit()
                modal_detalle.destroy()
                self.cargar_tablas_visuales()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def modal_crear_tabla(self):
        dialog = ctk.CTkInputDialog(text="Nombre de la tabla:", title="Nueva Tabla")
        dialog.attributes("-topmost", True)
        nombre = dialog.get_input()
        if nombre:
            nombre = nombre.strip()
            if nombre not in self.tablas_vacias_memoria:
                self.tablas_vacias_memoria.append(nombre)
                self.cargar_tablas_visuales()

    def modal_eliminar_tabla(self):
        opciones = self.obtener_todos_los_nombres_tablas()
        if not opciones: return
        pop = ctk.CTkToplevel(self)
        pop.geometry("350x200")
        pop.attributes("-topmost", True)
        combo = ctk.CTkOptionMenu(pop, values=opciones)
        combo.pack(pady=20)
        def confirmar():
            target = combo.get()
            with sqlite3.connect("gimnasio.db") as conn:
                conn.cursor().execute("DELETE FROM rutinas WHERE id_cliente=? AND nombre_tabla=?", (self.id_cliente, target))
            if target in self.tablas_vacias_memoria: self.tablas_vacias_memoria.remove(target)
            pop.destroy()
            self.cargar_tablas_visuales()
        ctk.CTkButton(pop, text="ELIMINAR", fg_color="#e74c3c", command=confirmar).pack()

    def restablecer_todo(self):
        if messagebox.askyesno("Atención", "¿Borrar todas las tablas y rutinas de este cliente?"):
            with sqlite3.connect("gimnasio.db") as conn:
                conn.cursor().execute("DELETE FROM rutinas WHERE id_cliente=?", (self.id_cliente,))
            self.tablas_vacias_memoria = []
            self.cargar_tablas_visuales()