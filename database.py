import sqlite3

def crear_base_de_datos():
    conexion = sqlite3.connect("gimnasio.db")
    cursor = conexion.cursor()
    
    cursor.execute("PRAGMA journal_mode=WAL;")

    # 1. TABLA DE CLIENTES (Actualizada con columna 'pago')
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
            pago TEXT DEFAULT 'Pendiente',
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

    # 2. TABLA DE PLANES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_plan TEXT NOT NULL,
            precio REAL NOT NULL,
            dias INTEGER DEFAULT 30
        )
    ''')

    # 3. TABLA DE EGRESOS
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

    # 4. TABLA DE RUTINAS (Asegúrate que esté así en database.py)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rutinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL, 
            nombre_rutina TEXT NOT NULL,
            ejercicio TEXT NOT NULL,
            series INTEGER NOT NULL,
            repeticiones INTEGER NOT NULL,
            grupo_muscular TEXT NOT NULL,
            dias TEXT NOT NULL,
            imagen_path TEXT,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id)
        )
    ''')

    # --- LÓGICA DE ACTUALIZACIÓN ---
    # Intenta agregar la columna 'pago' a clientes si la tabla ya existía
    try:
        cursor.execute("ALTER TABLE clientes ADD COLUMN pago TEXT DEFAULT 'Pendiente'")
    except sqlite3.OperationalError:
        pass 

    try:
        cursor.execute("ALTER TABLE planes ADD COLUMN dias INTEGER DEFAULT 30")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE rutinas ADD COLUMN id_cliente INTEGER NOT NULL DEFAULT 0")
        print("Columna id_cliente agregada con éxito")
    except sqlite3.OperationalError:
        # Si ya existe, no hará nada
        pass

    conexion.commit()
    conexion.close()
    print("Base de datos actualizada correctamente.")

if __name__ == "__main__":
    crear_base_de_datos()