import sqlite3

def actualizar_base():
    conexion = sqlite3.connect("gimnasio.db")
    cursor = conexion.cursor()
    
    # Lista de columnas nuevas para la tabla rutinas
    columnas = [
        ("nombre_tabla", "TEXT NOT NULL DEFAULT 'General'"),
        ("nombre_rutina", "TEXT"),
        ("carga_peso", "TEXT"),
        ("imagen_path", "TEXT")
    ]

    for nombre_col, tipo in columnas:
        try:
            cursor.execute(f"ALTER TABLE rutinas ADD COLUMN {nombre_col} {tipo}")
            print(f"Columna {nombre_col} añadida correctamente.")
        except sqlite3.OperationalError:
            print(f"La columna {nombre_col} ya existía.")

    conexion.commit()
    conexion.close()
    print("Actualización completada.")

if __name__ == "__main__":
    actualizar_base()