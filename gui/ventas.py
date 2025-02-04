from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QSpinBox, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox
)
from PyQt5.QtCore import Qt
from core.database import agregar_venta, obtener_productos, obtener_detalle_venta
from utils.pdf_ticket import generar_ticket

class VentanaVentas(QMainWindow):
    def __init__(self, cajero_id):
        super().__init__()
        self.cajero_id = cajero_id
        self.carrito = []
        self.setWindowTitle("Sistema de Ventas - Ordico")
        self.resize(800, 600)
        
        # Configurar widgets
        self._crear_widgets()
        self._cargar_productos()

    def _crear_widgets(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Selección de producto
        hbox = QHBoxLayout()
        self.combo_productos = QComboBox()
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setMinimum(1)
        self.btn_agregar = QPushButton("Agregar al Carrito")
        self.btn_agregar.clicked.connect(self.agregar_al_carrito)
        
        hbox.addWidget(QLabel("Producto:"))
        hbox.addWidget(self.combo_productos, stretch=2)
        hbox.addWidget(QLabel("Cantidad:"))
        hbox.addWidget(self.spin_cantidad)
        hbox.addWidget(self.btn_agregar)
        
        # Tabla del carrito
        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(4)
        self.tabla_carrito.setHorizontalHeaderLabels(["Producto", "Precio Unit.", "Cantidad", "Subtotal"])
        
        # Botón finalizar
        self.btn_finalizar = QPushButton("Finalizar Venta")
        self.btn_finalizar.clicked.connect(self.finalizar_venta)
        
        layout.addLayout(hbox)
        layout.addWidget(self.tabla_carrito)
        layout.addWidget(self.btn_finalizar)

    def _cargar_productos(self):
        """Carga productos en el combobox"""
        self.combo_productos.clear()
        for producto in obtener_productos():
            id_producto, nombre, _, precio, *_ = producto
            self.combo_productos.addItem(f"{nombre} (${precio:.2f})", id_producto)

    def agregar_al_carrito(self):
        producto_id = self.combo_productos.currentData()
        cantidad = self.spin_cantidad.value()
        
        # Buscar producto en DB
        producto = next((p for p in obtener_productos() if p[0] == producto_id), None)
        if producto:
            nombre = producto[1]
            precio = producto[3]
            self.carrito.append({
                'id_producto': producto_id,
                'nombre': nombre,
                'cantidad': cantidad,
                'precio_unitario': precio
            })
            self.actualizar_tabla_carrito()

    def actualizar_tabla_carrito(self):
        self.tabla_carrito.setRowCount(len(self.carrito))
        for row, item in enumerate(self.carrito):
            self.tabla_carrito.setItem(row, 0, QTableWidgetItem(item['nombre']))
            self.tabla_carrito.setItem(row, 1, QTableWidgetItem(f"${item['precio_unitario']:.2f}"))
            self.tabla_carrito.setItem(row, 2, QTableWidgetItem(str(item['cantidad'])))
            subtotal = item['cantidad'] * item['precio_unitario']
            self.tabla_carrito.setItem(row, 3, QTableWidgetItem(f"${subtotal:.2f}"))

    def finalizar_venta(self):
        if not self.carrito:
            QMessageBox.warning(self, "Error", "El carrito está vacío")
            return
        
        try:
            # Calcular total y preparar items
            total = sum(item['cantidad'] * item['precio_unitario'] for item in self.carrito)
            items_db = [{
                'id_producto': item['id_producto'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio_unitario']
            } for item in self.carrito]
            
            # Registrar en DB
            venta_id = agregar_venta(
                total=total,
                cajero_id=self.cajero_id,
                items=items_db
            )
            
            # Generar ticket
            generar_ticket({
                'id': venta_id,
                'items': self.carrito,
                'total': total
            })
            
            # Limpiar y actualizar
            self.carrito.clear()
            self.actualizar_tabla_carrito()
            QMessageBox.information(self, "Éxito", f"Venta #{venta_id} registrada\nTicket generado en PDF")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar venta:\n{str(e)}")