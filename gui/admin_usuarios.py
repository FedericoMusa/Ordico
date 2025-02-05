# Archivo: gui/admin_usuarios.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QComboBox
from core.database import obtener_todos_los_usuarios, actualizar_rol_usuario

class AdminUsuariosWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Administración de Usuarios")
        self.setMinimumSize(600, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.cargar_usuarios()
    
    def cargar_usuarios(self):
        usuarios = obtener_todos_los_usuarios()
        self.table.setRowCount(len(usuarios))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', 'Usuario', 'Email', 'Rol', 'Acciones'])
        
        for row, usuario in enumerate(usuarios):
            self.table.setItem(row, 0, QTableWidgetItem(str(usuario['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(usuario['username']))
            self.table.setItem(row, 2, QTableWidgetItem(usuario['email']))
            
            # ComboBox para cambiar rol
            cmb_rol = QComboBox()
            cmb_rol.addItems(['usuario', 'cajero', 'deposito', 'gerente'])
            cmb_rol.setCurrentText(usuario['rol'])
            self.table.setCellWidget(row, 3, cmb_rol)
            
            # Botón para guardar cambios
            btn_guardar = QPushButton("Guardar")
            btn_guardar.clicked.connect(lambda _, r=row: self.guardar_cambios(r))
            self.table.setCellWidget(row, 4, btn_guardar)
    
    def guardar_cambios(self, row):
        usuario_id = int(self.table.item(row, 0).text())
        nuevo_rol = self.table.cellWidget(row, 3).currentText()
        actualizar_rol_usuario(usuario_id, nuevo_rol)
        QMessageBox.information(self, "Éxito", f"Rol del usuario ID {usuario_id} actualizado a '{nuevo_rol}'")
