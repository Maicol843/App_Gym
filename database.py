import sqlite3

def crear_base_de_datos():
    conexion = sqlite3.connect("gimnasio.db")
    cursor = conexion.cursor()
    
    cursor.execute("PRAGMA journal_mode=WAL;")

    # 1. TABLA DE CLIENTES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            domicilio TEXT,
            telefono TEXT,
            fecha_nacimiento DATE,
            edad INTEGER,
            altura REAL,
            peso REAL,
            grupo_sanguineo TEXT,
            plan_seleccionado TEXT,
            fecha_inscripcion DATE,
            fecha_vencimiento DATE,
            patologia_columna INTEGER DEFAULT 0,
            detalle_columna TEXT,
            enfermedades_cardiacas INTEGER DEFAULT 0,
            detalle_cardiaco TEXT,
            lesiones INTEGER DEFAULT 0,
            detalle_lesion TEXT,
            deportes INTEGER DEFAULT 0,
            detalle_deporte TEXT,
            mareos INTEGER DEFAULT 0,
            dolor_cabeza INTEGER DEFAULT 0,
            desmayos INTEGER DEFAULT 0,
            hemorragias_nasales INTEGER DEFAULT 0,
            dolores_articulares INTEGER DEFAULT 0,
            alteracion INTEGER DEFAULT 0,
            problemas_rodilla_tobillo INTEGER DEFAULT 0,
            convulsiones INTEGER DEFAULT 0
        )
    ''')

    # 2. TABLA DE PLANES (Actualizada con columna 'dias')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_plan TEXT NOT NULL,
            precio REAL NOT NULL,
            dias INTEGER DEFAULT 30
        )
    ''')

    # --- LÓGICA DE ACTUALIZACIÓN ---
    # Intentamos agregar la columna 'dias' por si la tabla ya existe sin ella
    try:
        cursor.execute("ALTER TABLE planes ADD COLUMN dias INTEGER DEFAULT 30")
    except sqlite3.OperationalError:
        pass # La columna ya existe

    conexion.commit()
    conexion.close()
    print("Base de datos actualizada correctamente.")

if __name__ == "__main__":
    crear_base_de_datos()