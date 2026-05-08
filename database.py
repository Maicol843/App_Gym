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

    # 2. TABLA PLAN ELEGIDO
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plan_elegido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            plan_seleccionado TEXT,
            fecha_inscripcion DATE,
            fecha_vencimiento DATE,
            pago TEXT DEFAULT 'Pendiente',
            FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE CASCADE
        )
    ''')

      # 2. TABLA DE PLANES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_plan TEXT NOT NULL,
            precio REAL NOT NULL,
            dias INTEGER DEFAULT 30
        )
    ''')

   # --- Fragmento modificado de database.py ---

    # 3. TABLA DE INGRESOS 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER,
            plan_seleccionado TEXT, 
            monto REAL NOT NULL,
            fecha DATE NOT NULL,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE CASCADE
        )
    ''')

    # 4. TABLA DE EGRESOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS egresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE NOT NULL,
            detalle TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            p_unit REAL NOT NULL,
            importe REAL NOT NULL
        )
    ''')

    # 5. TABLA DE RUTINAS 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rutinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            nombre_tabla TEXT NOT NULL,
            nombre_rutina TEXT,
            ejercicio TEXT NOT NULL,
            series TEXT,
            repeticiones TEXT,
            grupo_muscular TEXT,
            carga_peso TEXT,
            dias TEXT NOT NULL,
            imagen_path TEXT,
            video_link TEXT,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE CASCADE
        )
    ''')

    conexion.commit()
    conexion.close()
    print("Base de datos actualizada con éxito.")

if __name__ == "__main__":
    crear_base_de_datos()