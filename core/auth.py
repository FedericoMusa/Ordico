# Ejemplo de estructura de usuarios en DB
USUARIOS = [
    {
        "id": 1,
        "username": "jefe",
        "password_hash": "hash_secure",
        "rol": "gerente"
    },
    # ... más usuarios
]

def login(username, password):
    # Verifica credenciales y devuelve el rol del usuario
