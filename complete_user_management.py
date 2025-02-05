import sqlite3
import bcrypt

def conectar():
    return sqlite3.connect("ordico.db")

def crear_tablas():
    with conectar() as conn:
        cursor = conn.cursor()
        try:
            # Eliminar y recrear las tablas
            cursor.executescript('''
                -- Eliminar la tabla detalle_ventas si existe
                DROP TABLE IF EXISTS detalle_ventas;

                -- Eliminar la tabla ventas si existe
                DROP TABLE IF EXISTS ventas;

                -- Eliminar la tabla usuarios si existe
                DROP TABLE IF EXISTS usuarios;

                -- Eliminar la tabla productos si existe
                DROP TABLE IF EXISTS productos;

                -- Crear la tabla usuarios
                CREATE TABLE usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash BLOB NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    rol TEXT CHECK(rol IN ('gerente', 'cajero', 'deposito', 'usuario')) NOT NULL
                );

                -- Crear la tabla productos
                CREATE TABLE productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    precio REAL NOT NULL,
                    stock INTEGER NOT NULL,
                    proveedor TEXT,
                    stock_minimo INTEGER DEFAULT 0
                );

                -- Crear la tabla ventas
                CREATE TABLE ventas (
                    id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    total REAL NOT NULL,
                    cajero_id INTEGER NOT NULL,
                    FOREIGN KEY (cajero_id) REFERENCES usuarios(id)
                );

                -- Crear la tabla detalle_ventas
                CREATE TABLE detalle_ventas (
                    id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_venta INTEGER,
                    id_producto INTEGER,
                    cantidad INTEGER NOT NULL,
                    precio_unitario REAL NOT NULL,
                    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
                    FOREIGN KEY (id_producto) REFERENCES productos(id)
                );

                -- Crear índices para mejorar el rendimiento
                CREATE INDEX idx_productos_nombre ON productos(nombre);
                CREATE INDEX idx_ventas_fecha ON ventas(fecha);
            ''')
            conn.commit()
            print("Tablas recreadas exitosamente.")
        except Exception as e:
            conn.rollback()
            print(f"Error al recrear tablas: {e}")

def verificar_tablas_vacias():
    with conectar() as conn:
        cursor = conn.cursor()
        try:
            # Verificar la tabla usuarios
            cursor.execute('SELECT COUNT(*) FROM usuarios')
            usuarios_count = cursor.fetchone()[0]
            print(f"Usuarios: {usuarios_count}")

            # Verificar la tabla productos
            cursor.execute('SELECT COUNT(*) FROM productos')
            productos_count = cursor.fetchone()[0]
            print(f"Productos: {productos_count}")

            if usuarios_count == 0 and productos_count == 0:
                print("Las tablas están vacías y listas para usar.")
            else:
                print("Las tablas no están vacías.")
        except Exception as e:
            print(f"Error al verificar tablas: {e}")

def crear_usuario(username, password, email, rol='usuario'):
    """Crea un usuario con contraseña hasheada usando bcrypt y correo electrónico"""
    with conectar() as conn:
        cursor = conn.cursor()
        try:
            # Verificar si el usuario o el email ya existen
            cursor.execute('SELECT id FROM usuarios WHERE username = ? OR email = ?', (username, email))
            if cursor.fetchone():
                raise ValueError("El nombre de usuario o correo electrónico ya existen")

            # Hashear contraseña con bcrypt
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            cursor.execute('''
                INSERT INTO usuarios (username, password_hash, rol, email)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, rol, email))
            conn.commit()
            print(f"Usuario '{username}' creado exitosamente.")
        except sqlite3.IntegrityError:
            raise ValueError("El nombre de usuario o correo electrónico ya existen")
        except Exception as e:
            print(f"Error al crear usuario '{username}': {e}")

def autenticar_usuario(username, password):
    """Autentica un usuario verificando su nombre de usuario y contraseña"""
    with conectar() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT password_hash FROM usuarios WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row is None:
                return False
            password_hash = row[0]
            return bcrypt.checkpw(password.encode('utf-8'), password_hash)
        except Exception as e:
            print(f"Error al autenticar usuario '{username}': {e}")
            return False

def ver_usuarios():
    with conectar() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM usuarios')
            usuarios = cursor.fetchall()
            for usuario in usuarios:
                print(f"ID: {usuario[0]}, Username: {usuario[1]}, Email: {usuario[3]}, Rol: {usuario[4]}")
        except Exception as e:
            print(f"Error al obtener usuarios: {e}")

if __name__ == "__main__":
    crear_tablas()
    verificar_tablas_vacias()
    crear_usuario('admin', 'admin123', 'admin@example.com', 'gerente')
    ver_usuarios()
    
    # Autenticar usuario
    if autenticar_usuario('admin', 'admin123'):
        print("Autenticación exitosa para el usuario 'admin'.")
    else:
        print("Fallo en la autenticación para el usuario 'admin'.")
