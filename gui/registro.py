# Archivo: gui/registro.py
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox
)
import re
from core.database import crear_usuario

class RegisterWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registro de Nuevo Usuario")
        self.setFixedSize(350, 250)
        self.init_ui()
        
    def init_ui(self):
        layout = QGridLayout()
        
        # Etiquetas y campos de entrada
        self.lbl_usuario = QLabel("Usuario:")
        self.txt_usuario = QLineEdit()
        
        self.lbl_password = QLabel("Contraseña:")
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        
        self.lbl_confirmar = QLabel("Confirmar Contraseña:")
        self.txt_confirmar = QLineEdit()
        self.txt_confirmar.setEchoMode(QLineEdit.Password)
        
        self.lbl_email = QLabel("Correo Electrónico:")
        self.txt_email = QLineEdit()
        
        # Botón de registro
        self.btn_registrar = QPushButton("Registrar")
        self.btn_registrar.clicked.connect(self.registrar_usuario)
        
        # Añadir widgets al layout
        layout.addWidget(self.lbl_usuario, 0, 0)
        layout.addWidget(self.txt_usuario, 0, 1)
        layout.addWidget(self.lbl_password, 1, 0)
        layout.addWidget(self.txt_password, 1, 1)
        layout.addWidget(self.lbl_confirmar, 2, 0)
        layout.addWidget(self.txt_confirmar, 2, 1)
        layout.addWidget(self.lbl_email, 3, 0)
        layout.addWidget(self.txt_email, 3, 1)
        layout.addWidget(self.btn_registrar, 4, 0, 1, 2)
        
        self.setLayout(layout)
        
    def registrar_usuario(self):
        usuario = self.txt_usuario.text().strip()
        password = self.txt_password.text()
        confirmar = self.txt_confirmar.text()
        email = self.txt_email.text().strip()
        
        # Validaciones básicas
        if not usuario or not password or not confirmar or not email:
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos")
            return
        if password != confirmar:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
            return
        if not self.validar_email(email):
            QMessageBox.warning(self, "Error", "Correo electrónico inválido")
            return
        
        # No hasheamos la contraseña aquí; eso se hace en crear_usuario
        try:
            # Intentar crear el usuario en la base de datos
            crear_usuario(usuario, password, email)
            QMessageBox.information(self, "Éxito", "Usuario registrado correctamente")
            self.accept()
        except ValueError as ve:
            QMessageBox.warning(self, "Error", str(ve))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Ocurrió un error al registrar el usuario: {e}")

    def validar_email(self, email):
        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(patron, email)
