import sqlite3

def crear_tablas():
    conn = sqlite3.connect('ordico.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            total REAL NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta INTEGER,
            id_producto INTEGER,
            cantidad INTEGER NOT NULL,
            FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
            FOREIGN KEY (id_producto) REFERENCES productos(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Ejecutar al inicio para crear tablas
crear_tablas()
import sqlite3

def conectar():
    return sqlite3.connect('ordico.db')

# ---- Funciones para Productos ----
def agregar_producto(nombre, descripcion, precio, stock):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO productos (nombre, descripcion, precio, stock)
        VALUES (?, ?, ?, ?)
    ''', (nombre, descripcion, precio, stock))
    conn.commit()
    conn.close()

def obtener_productos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()
    conn.close()
    return productos

def eliminar_producto(id_producto):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM productos WHERE id = ?', (id_producto,))
    conn.commit()
    conn.close()

# ---- Funciones para Ventas ----
def registrar_venta(fecha, total):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO ventas (fecha, total) VALUES (?, ?)', (fecha, total))
    id_venta = cursor.lastrowid
    conn.commit()
    conn.close()
    return id_venta

def agregar_detalle_venta(id_venta, id_producto, cantidad):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO detalle_ventas (id_venta, id_producto, cantidad)
        VALUES (?, ?, ?)
    ''', (id_venta, id_producto, cantidad))
    conn.commit()
    conn.close()
