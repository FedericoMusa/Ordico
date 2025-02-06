from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from gui.stock import StockWindow
from gui.ventas import VentanaVentas

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