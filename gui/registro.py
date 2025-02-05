from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from core.database import crear_usuario

class RegisterWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registro de Usuario")
        self.setFixedSize(300, 250)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.lbl_usuario = QLabel("Nombre de Usuario:")
        self.txt_usuario = QLineEdit()

        self.lbl_email = QLabel("Correo Electrónico:")
        self.txt_email = QLineEdit()

        self.lbl_password = QLabel("Contraseña:")
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)

        self.lbl_rol = QLabel("Rol:")
        self.txt_rol = QLineEdit()

        self.btn_registrar = QPushButton("Registrar")
        self.btn_registrar.clicked.connect(self.registrar_usuario)

        layout.addWidget(self.lbl_usuario)
        layout.addWidget(self.txt_usuario)
        layout.addWidget(self.lbl_email)
        layout.addWidget(self.txt_email)
        layout.addWidget(self.lbl_password)
        layout.addWidget(self.txt_password)
        layout.addWidget(self.lbl_rol)
        layout.addWidget(self.btn_registrar)
        
        self.setLayout(layout)

    def registrar_usuario(self):
        username = self.txt_usuario.text()
        email = self.txt_email.text()
        password = self.txt_password.text()
        rol = self.txt_rol.text()

        try:
            crear_usuario(username, password, email, rol)
            QMessageBox.information(self, "Registro Exitoso", "Usuario registrado exitosamente.")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))