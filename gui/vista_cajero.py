from PyQt5.QtWidgets import (
    QMainWindow, QAction, QLabel, QVBoxLayout, QWidget
)

class AdminView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vista de Administrador")
        self.setFixedSize(800, 600)
        self.init_ui()
        
    def init_ui(self):
        # Barra de menú
        menubar = self.menuBar()
        
        # Menú de usuarios
        usuarios_menu = menubar.addMenu("Usuarios")
        add_user_action = QAction("Añadir Usuario", self)
        usuarios_menu.addAction(add_user_action)
        
        # Menú de productos
        productos_menu = menubar.addMenu("Productos")
        add_product_action = QAction("Añadir Producto", self)
        productos_menu.addAction(add_product_action)
        
        # Ventana principal
        layout = QVBoxLayout()
        label = QLabel("Bienvenido, Administrador")
        layout.addWidget(label)
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)