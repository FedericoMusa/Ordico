from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox
)
from core.database import verificar_login, obtener_usuario_por_username
from gui.registro import RegisterWindow

# ----------------------------------------------------------
# Login Window
# ----------------------------------------------------------
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Acceso a ORDICO")
        self.setFixedSize(300, 180)
        self.usuario = None
        self.init_ui()
        
    def init_ui(self):
        layout = QGridLayout()
        
        self.lbl_usuario = QLabel("Usuario:")
        self.txt_usuario = QLineEdit()
        
        self.lbl_password = QLabel("Contraseña:")
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        
        self.btn_login = QPushButton("Ingresar")
        self.btn_login.clicked.connect(self.validar_login)
        
        self.btn_registrar = QPushButton("Registrarse")
        self.btn_registrar.clicked.connect(self.abrir_registro)
        
        layout.addWidget(self.lbl_usuario, 0, 0)
        layout.addWidget(self.txt_usuario, 0, 1)
        layout.addWidget(self.lbl_password, 1, 0)
        layout.addWidget(self.txt_password, 1, 1)
        layout.addWidget(self.btn_login, 2, 0, 1, 2)
        layout.addWidget(self.btn_registrar, 3, 0, 1, 2)
        
        self.setLayout(layout)
    
    def validar_login(self):
        usuario = self.txt_usuario.text()
        password = self.txt_password.text()
        
        if verificar_login(usuario, password):
            self.usuario = obtener_usuario_por_username(usuario)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Credenciales inválidas")
    
    def abrir_registro(self):
        registro = RegisterWindow()
        if registro.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "Registro Exitoso", "Usuario registrado. Por favor, ingresa tus credenciales.")