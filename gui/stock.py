from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QHeaderView, QGridLayout
)
from PyQt5.QtCore import Qt
from core.database import agregar_producto, obtener_productos, eliminar_producto
from core.validaciones import validar_campos_vacios, validar_tipos_producto

class StockWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Stock - ORDICO")
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.cargar_productos()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Campos de entrada
        grid = QGridLayout()
        self.entries = {
            'nombre': QLineEdit(),
            'precio': QLineEdit(),
            'stock': QLineEdit()
        }
        
        grid.addWidget(QLabel("Nombre:"), 0, 0)
        grid.addWidget(self.entries['nombre'], 0, 1)
        grid.addWidget(QLabel("Precio:"), 1, 0)
        grid.addWidget(self.entries['precio'], 1, 1)
        grid.addWidget(QLabel("Stock:"), 2, 0)
        grid.addWidget(self.entries['stock'], 2, 1)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar Producto")
        self.btn_eliminar = QPushButton("Eliminar Seleccionado")
        
        self.btn_agregar.clicked.connect(self.agregar_producto)
        self.btn_eliminar.clicked.connect(self.eliminar_producto)
        
        btn_layout.addWidget(self.btn_agregar)
        btn_layout.addWidget(self.btn_eliminar)
        
        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Precio", "Stock"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Ensamblar layout
        layout.addLayout(grid)
        layout.addLayout(btn_layout)
        layout.addWidget(self.tabla)
        self.setLayout(layout)

    def cargar_productos(self):
        self.tabla.setRowCount(0)
        productos = obtener_productos()
        for row, producto in enumerate(productos):
            self.tabla.insertRow(row)
            for col, value in enumerate(producto[:4]):  # ID, Nombre, Descripción, Precio, Stock
                item = QTableWidgetItem(str(value))
                if col in [0, 3]:  # ID y Stock son de solo lectura
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.tabla.setItem(row, col, item)

    def agregar_producto(self):
        nombre = self.entries['nombre'].text()
        precio = self.entries['precio'].text()
        stock = self.entries['stock'].text()
        
        if not validar_campos_vacios([nombre, precio, stock]):
            QMessageBox.critical(self, "Error", "Complete todos los campos")
            return
            
        if not validar_tipos_producto(precio, stock):
            QMessageBox.critical(self, "Error", "Tipos de datos inválidos:\n- Precio debe ser número\n- Stock debe ser entero")
            return
            
        try:
            agregar_producto(
                nombre=nombre,
                descripcion="",  # Campo modificable si se agrega en la UI
                precio=float(precio),
                stock=int(stock)
            )
            self.cargar_productos()
            QMessageBox.information(self, "Éxito", "Producto agregado exitosamente")
            self.limpiar_campos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar producto:\n{str(e)}")

    def eliminar_producto(self):
        selected = self.tabla.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return
            
        row = selected[0].row()
        producto_id = int(self.tabla.item(row, 0).text())
        
        confirm = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Está seguro de eliminar este producto?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                eliminar_producto(producto_id)
                self.cargar_productos()
                QMessageBox.information(self, "Éxito", "Producto eliminado exitosamente")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar producto:\n{str(e)}")

    def limpiar_campos(self):
        for entry in self.entries.values():
            entry.clear()