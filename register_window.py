from PyQt5.QtWidgets import QDialog, QMessageBox
from registro import Ui_RegisterDialog
from core.database import registrar_usuario

class RegisterWindow(QDialog, Ui_RegisterDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_register.clicked.connect(self.registrar_usuario)
    
    def registrar_usuario(self):
        username = self.lineEdit_username.text()
        password = self.lineEdit_password.text()

        if registrar_usuario(username, password):
            QMessageBox.information(self, "Registro Exitoso", "Usuario registrado exitosamente.")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "No se pudo registrar el usuario. Intenta nuevamente.")