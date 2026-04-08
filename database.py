# 1. Planificación de la Estructura
# Antes de escribir la primera línea de código, debemos entender cómo se conectarán las piezas. 
# La aplicación seguirá una arquitectura básica de Modelo-Vista-Controlador (MVC) de forma 
# simplificada:
# a. Base de Datos (Model): Tablas para Clientes, Membresías, Pagos, Asistencia y Rutinas.
# b.Interfaz Gráfica (View): Ventanas para el Dashboard, el registro y las tablas visuales.
# c. Lógica de Negocio (Controller): Funciones que calculan si un pago está vencido, 
# generan el QR o crean el PDF.
# Requisitos previos
# Para comenzar, necesitarás instalar Python en tu equipo y ejecutar el siguiente 
# comando en tu terminal para instalar las librerías necesarias:
# pip install customtkinter pillow pandas reportlab qrcode opencv-python
#. 2. Paso 1: Diseño de la Base de Datos
# Lo primero es crear el "cerebro" donde guardaremos todo. Usaremos SQLite. 
# Aquí te presento el código para inicializar la base de datos y las tablas principales.
# Código de Inicialización (database.py):
import sqlite3

def crear_base_de_datos():
    conexion = sqlite3.connect("gimnasio.db")
    cursor = conexion.cursor()

    # Tabla de Clientes con Ficha Médica Completa
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
            convulsiones INTEGER DEFAULT 0,
            
            -- Gestión de Gimnasio
            fecha_inscripcion DATE,
            plan_id INTEGER,
            fecha_vencimiento DATE
        )
    ''')

    #Tabla de Pagos
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

    # Tabla de Asistencia
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS asistencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            fecha_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')

    # Tabla de Gestión de Planes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_plan TEXT NOT NULL,
            precio REAL NOT NULL
        )
    ''')

    conexion.commit()
    conexion.close()
    print("Base de datos actualizada con ficha médica completa.")

if __name__ == "__main__":
    crear_base_de_datos()
    