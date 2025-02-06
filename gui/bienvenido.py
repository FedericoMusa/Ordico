from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class BienvenidoWindow(QDialog):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Bienvenido a ORDICO")
        self.setFixedSize(300, 200)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        lbl_bienvenida = QLabel(f"Bienvenido a ORDICO, {self.usuario['username']}!")
        lbl_bienvenida.setAlignment(Qt.AlignCenter)
        
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        
        layout.addWidget(lbl_bienvenida)
        layout.addWidget(btn_ok)
        
        self.setLayout(layout)
