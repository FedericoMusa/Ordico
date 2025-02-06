import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from gui.main_window import MainApp
from gui.registro import RegisterWindow
from gui.bienvenido import BienvenidoWindow
from core.database import verificar_login, obtener_usuario_por_username

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

# ----------------------------------------------------------
# Main Application
# ----------------------------------------------------------
class MainApp(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle(f"ORDICO - Bienvenido {usuario['username']}")
        self.setMinimumSize(800, 600)
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Logo del local
        logo = QLabel(self)
        pixmap = QPixmap("assets/logo.png")
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        
        lbl_bienvenida = QLabel(f"Rol: {self.usuario['rol'].capitalize()}")
        lbl_bienvenida.setAlignment(Qt.AlignCenter)
        
        # Botones según rol
        self.btn_stock = QPushButton("Gestión de Stock")
        self.btn_ventas = QPushButton("Sistema de Ventas")
        self.btn_reportes = QPushButton("Reportes Gerenciales")
        btn_salir = QPushButton("Salir")
        
        # Configurar visibilidad por rol
        if self.usuario['rol'] == 'deposito':
            self.btn_ventas.setVisible(False)
            self.btn_reportes.setVisible(False)
        elif self.usuario['rol'] == 'cajero':
            self.btn_stock.setVisible(False)
            self.btn_reportes.setVisible(False)
        elif self.usuario['rol'] == 'usuario':
            self.btn_stock.setVisible(False)
            self.btn_ventas.setVisible(False)
            self.btn_reportes.setVisible(False)
        
        # Conexiones
        self.btn_stock.clicked.connect(self.abrir_stock)
        self.btn_ventas.clicked.connect(self.abrir_ventas)
        self.btn_reportes.clicked.connect(self.abrir_reportes)
        btn_salir.clicked.connect(self.close)
        
        # Estilos
        for btn in [self.btn_stock, self.btn_ventas, self.btn_reportes]:
            btn.setStyleSheet("padding: 15px; font-size: 14px;")
        
        layout.addWidget(logo)
        layout.addWidget(lbl_bienvenida)
        layout.addWidget(self.btn_stock)
        layout.addWidget(self.btn_ventas)
        layout.addWidget(self.btn_reportes)
        layout.addWidget(btn_salir)

    def abrir_stock(self):
        self.stock_window = StockWindow()
        self.stock_window.show()

    def abrir_ventas(self):
        self.ventas_window = VentanaVentas(cajero_id=self.usuario['id'])
        self.ventas_window.show()

    def abrir_reportes(self):
        QMessageBox.information(self, "En Desarrollo", "Módulo de reportes en construcción")

# ----------------------------------------------------------
# Punto de Entrada Principal
# ----------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    login = LoginWindow()
    if login.exec_() == QDialog.Accepted:
        bienvenido_window = BienvenidoWindow(login.usuario)
        if bienvenido_window.exec_() == QDialog.Accepted:
            main_window = MainApp(login.usuario)
            main_window.show()
        sys.exit(app.exec_())
    else:
        sys.exit()