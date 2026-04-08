import sqlite3

def crear_base_de_datos():
    conexion = sqlite3.connect("gimnasio.db")
    cursor = conexion.cursor()
    
    # Activar modo WAL para evitar bloqueos de base de datos
    cursor.execute("PRAGMA journal_mode=WAL;")

    # 1. TABLA DE CLIENTES (Actualizada con Plan y Fecha de Inscripción)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            -- Datos Personales
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            domicilio TEXT,
            telefono TEXT,
            fecha_nacimiento DATE,
            edad INTEGER,
            
            -- Datos Físicos
            altura REAL,
            peso REAL,
            grupo_sanguineo TEXT,
            
            -- Plan y Gestión
            plan_seleccionado TEXT,
            fecha_inscripcion DATE,
            fecha_vencimiento DATE,
            
            -- Ficha Médica (0 = No, 1 = Si)
            patologia_columna INTEGER DEFAULT 0,
            detalle_columna TEXT,
            enfermedades_cardiacas INTEGER DEFAULT 0,
            detalle_cardiaco TEXT,
            lesiones INTEGER DEFAULT 0,
            detalle_lesion TEXT,
            deportes INTEGER DEFAULT 0,
            detalle_deporte TEXT,
            
            -- Síntomas y Otros
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

    # 2. TABLA DE PLANES (Para la ventana de Gestión de Gimnasio)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_plan TEXT NOT NULL,
            precio REAL NOT NULL
        )
    ''')

    # 3. TABLA DE PAGOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            monto REAL,
            fecha_pago DATE,
            estado TEXT, -- 'Pagado', 'Pendiente'
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')

    # 4. TABLA DE ASISTENCIA
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS asistencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            fecha_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')

    # --- LÓGICA DE ACTUALIZACIÓN ---
    # Si la tabla ya existía, intentamos agregar las columnas nuevas por si acaso
    columnas_nuevas = [
        ("plan_seleccionado", "TEXT"),
        ("fecha_inscripcion", "DATE")
    ]
    
    for columna, tipo in columnas_nuevas:
        try:
            cursor.execute(f"ALTER TABLE clientes ADD COLUMN {columna} {tipo}")
        except sqlite3.OperationalError:
            # Si la columna ya existe, SQLite dará error, simplemente lo ignoramos
            pass

    conexion.commit()
    conexion.close()
    print("Base de datos lista y actualizada.")

if __name__ == "__main__":
    crear_base_de_datos()