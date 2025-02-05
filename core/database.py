import sqlite3
import bcrypt
from hashlib import sha256
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, filename='app.log',
                    format='%(asctime)s %(levelname)s:%(message)s')

def conectar():
    conn = sqlite3.connect("ordico.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
    return conn

def obtener_todos_los_usuarios():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios')
        return cursor.fetchall()

def actualizar_rol_usuario(usuario_id, nuevo_rol):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE usuarios
            SET rol = ?
            WHERE id = ?
        ''', (nuevo_rol, usuario_id))
        conn.commit()

def crear_tablas():
    with conectar() as conn:
        cursor = conn.cursor()

        # Iniciar transacción
        conn.execute('BEGIN')
        try:
            # Verificar si la tabla 'usuarios' ya existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios';")
            table_exists = cursor.fetchone()

            if table_exists:
                # Obtener las columnas existentes
                cursor.execute("PRAGMA table_info(usuarios);")
                columns_info = cursor.fetchall()
                existing_columns = [column['name'] for column in columns_info]

                # Comprobar si la columna 'email' existe
                if 'email' not in existing_columns:
                    # Renombrar la tabla actual a un nombre temporal
                    cursor.execute('ALTER TABLE usuarios RENAME TO usuarios_old;')

                    # Crear la nueva tabla con la estructura deseada
                    cursor.execute('''
                        CREATE TABLE usuarios (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password_hash BLOB NOT NULL,
                            email TEXT UNIQUE NOT NULL,
                            rol TEXT CHECK(rol IN ('gerente', 'cajero', 'deposito', 'usuario')) NOT NULL
                        );
                    ''')

                    # Migrar los datos de la tabla antigua a la nueva
                    cursor.execute('''
                        SELECT id, username, password_hash, rol FROM usuarios_old;
                    ''')
                    usuarios_antiguos = cursor.fetchall()
                    for usuario in usuarios_antiguos:
                        # Convertir el hash de texto a bytes
                        password_hash_bytes = usuario['password_hash'].encode('utf-8')
                        # Asignar un email temporal
                        email_temporal = usuario['username'] + '@temporal.com'
                        cursor.execute('''
                            INSERT INTO usuarios (id, username, password_hash, email, rol)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (usuario['id'], usuario['username'], password_hash_bytes, email_temporal, usuario['rol']))

                    # Eliminar la tabla antigua
                    cursor.execute('DROP TABLE usuarios_old;')
                    logging.info("Migración de la tabla 'usuarios' completada con éxito.")
                else:
                    logging.info("La columna 'email' ya existe en la tabla 'usuarios'. No es necesaria la migración.")
            else:
                # La tabla no existe; crearla con la estructura completa
                cursor.execute('''
                    CREATE TABLE usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash BLOB NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        rol TEXT CHECK(rol IN ('gerente', 'cajero', 'deposito', 'usuario')) NOT NULL
                    );
                ''')
                logging.info("Tabla 'usuarios' creada con éxito.")

            # Crear tabla 'productos'
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    precio REAL NOT NULL,
                    stock INTEGER NOT NULL,
                    proveedor TEXT,
                    stock_minimo INTEGER DEFAULT 0
                );
            ''')

            # Crear tabla 'ventas'
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ventas (
                    id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    total REAL NOT NULL,
                    cajero_id INTEGER NOT NULL,
                    FOREIGN KEY (cajero_id) REFERENCES usuarios(id)
                );
            ''')

            # Crear tabla 'detalle_ventas'
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detalle_ventas (
                    id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_venta INTEGER,
                    id_producto INTEGER,
                    cantidad INTEGER NOT NULL,
                    precio_unitario REAL NOT NULL,
                    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
                    FOREIGN KEY (id_producto) REFERENCES productos(id)
                );
            ''')

            # Crear índices para mejorar el rendimiento
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_productos_nombre ON productos(nombre);')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha);')

            # Confirmar transacción
            conn.commit()
            logging.info("Las tablas fueron creadas o actualizadas exitosamente.")
        except Exception as e:
            # Revertir transacción en caso de error
            conn.rollback()
            logging.error(f"Error al crear o migrar tablas: {e}")
            raise e

# --------------------------------------------------
# Funciones para Usuarios
# --------------------------------------------------

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
            logging.info(f"Usuario '{username}' creado exitosamente.")
        except sqlite3.IntegrityError:
            raise ValueError("El nombre de usuario o correo electrónico ya existen")
        except Exception as e:
            logging.error(f"Error al crear usuario '{username}': {e}")
            raise e

def obtener_usuario_por_username(username):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE username = ?', (username,))
        return cursor.fetchone()

def obtener_usuario_por_email(email):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
        return cursor.fetchone()

def verificar_login(username, password):
    usuario = obtener_usuario_por_username(username)
    if usuario:
        stored_password_hash = usuario['password_hash']
        try:
            # Intentar verificar con bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash):
                return True
        except ValueError:
            # Si falla, puede ser un hash sha256 en string
            hashed_input = sha256(password.encode()).hexdigest()
            stored_hash_str = stored_password_hash.decode('utf-8')
            if hashed_input == stored_hash_str:
                # Actualizar el password_hash a bcrypt
                nuevo_password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                with conectar() as conn:
                    cursor = conn.cursor()
                    cursor.execute('UPDATE usuarios SET password_hash = ? WHERE id = ?', 
                                   (nuevo_password_hash, usuario['id']))
                    conn.commit()
                logging.info(f"Contraseña de usuario '{username}' actualizada a bcrypt.")
                return True
    return False

def actualizar_email_usuario(usuario_id, nuevo_email):
    with conectar() as conn:
        cursor = conn.cursor()
        try:
            # Verificar si el email ya existe
            cursor.execute('SELECT id FROM usuarios WHERE email = ?', (nuevo_email,))
            if cursor.fetchone():
                raise ValueError("El correo electrónico ya está en uso")

            # Actualizar el email
            cursor.execute('UPDATE usuarios SET email = ? WHERE id = ?', (nuevo_email, usuario_id))
            conn.commit()
            logging.info(f"Email del usuario con ID {usuario_id} actualizado a '{nuevo_email}'.")
        except sqlite3.IntegrityError:
            raise ValueError("El correo electrónico ya está en uso")
        except Exception as e:
            logging.error(f"Error al actualizar email del usuario {usuario_id}: {e}")
            raise e

# --------------------------------------------------
# Funciones para Productos
# --------------------------------------------------

def agregar_producto(nombre, descripcion, precio, stock, proveedor=None, stock_minimo=0):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO productos 
            (nombre, descripcion, precio, stock, proveedor, stock_minimo)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombre, descripcion, precio, stock, proveedor, stock_minimo))
        conn.commit()
        logging.info(f"Producto '{nombre}' agregado exitosamente.")

def obtener_productos():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM productos ORDER BY nombre')
        return cursor.fetchall()

def eliminar_producto(id_producto):
    with conectar() as conn:
        conn.execute('DELETE FROM productos WHERE id = ?', (id_producto,))
        conn.commit()
        logging.info(f"Producto con ID {id_producto} eliminado.")

def actualizar_stock(producto_id, nuevo_stock):
    with conectar() as conn:
        conn.execute('''
            UPDATE productos 
            SET stock = ?
            WHERE id = ?
        ''', (nuevo_stock, producto_id))
        conn.commit()
        logging.info(f"Stock del producto con ID {producto_id} actualizado a {nuevo_stock}.")

def obtener_productos_bajo_stock():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM productos 
            WHERE stock < stock_minimo
            ORDER BY stock ASC
        ''')
        return cursor.fetchall()

# --------------------------------------------------
# Funciones para Ventas
# --------------------------------------------------

def agregar_venta(total, cajero_id, items):
    """Registra una venta y actualiza el stock en transacción"""
    with conectar() as conn:
        try:
            cursor = conn.cursor()
            
            # Validar stock primero
            for item in items:
                cursor.execute('SELECT stock FROM productos WHERE id = ?', (item['id_producto'],))
                stock_actual = cursor.fetchone()['stock']
                if stock_actual < item['cantidad']:
                    raise ValueError(f"Stock insuficiente para producto ID {item['id_producto']}")
            
            # Insertar venta principal
            cursor.execute('''
                INSERT INTO ventas (total, cajero_id)
                VALUES (?, ?)
            ''', (total, cajero_id))
            venta_id = cursor.lastrowid
            
            # Insertar detalles y actualizar stock
            for item in items:
                cursor.execute('''
                    INSERT INTO detalle_ventas 
                    (id_venta, id_producto, cantidad, precio_unitario)
                    VALUES (?, ?, ?, ?)
                ''', (venta_id, item['id_producto'], item['cantidad'], item['precio_unitario']))
                
                cursor.execute('''
                    UPDATE productos 
                    SET stock = stock - ?
                    WHERE id = ?
                ''', (item['cantidad'], item['id_producto']))
            
            conn.commit()
            logging.info(f"Venta ID {venta_id} registrada exitosamente por cajero ID {cajero_id}.")
            return venta_id
        except sqlite3.Error as e:
            conn.rollback()
            logging.error(f"Error al registrar venta: {e}")
            raise e

def obtener_ventas_por_cajero(cajero_id):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.id_venta, v.fecha, v.total, u.username 
            FROM ventas v
            JOIN usuarios u ON v.cajero_id = u.id
            WHERE v.cajero_id = ?
            ORDER BY v.fecha DESC
        ''', (cajero_id,))
        return cursor.fetchall()

def obtener_detalle_venta(id_venta):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.nombre, dv.cantidad, dv.precio_unitario 
            FROM detalle_ventas dv
            JOIN productos p ON dv.id_producto = p.id
            WHERE dv.id_venta = ?
        ''', (id_venta,))
        return cursor.fetchall()

# --------------------------------------------------
# Inicializar la base de datos al importar
# --------------------------------------------------

crear_tablas()

# Crear usuarios predeterminados (solo si no existen)
usuarios_predeterminados = [
    ("admin", "admin123", "admin@example.com", "gerente"),
    ("cajero", "cajero123", "cajero@example.com", "cajero"),
    ("operador", "operador123", "operador@example.com", "deposito")
]

for username, password, email, rol in usuarios_predeterminados:
    try:
        crear_usuario(username, password, email, rol)
        logging.info(f"Usuario predeterminado '{username}' creado exitosamente.")
    except ValueError:
        logging.info(f"El usuario predeterminado '{username}' ya existe.")