# main.py
import tkinter as tk
from tkinter import ttk
from gui.stocks import StockWindow
from utils.pdf_ticket import generar_ticket  # ✅ Importación correcta

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ORDICO")
        self.root.geometry("400x200")
        self.crear_menu()
    
    def crear_menu(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=40)
        
        ttk.Button(frame, text="Abrir Stock", 
                 command=lambda: StockWindow(self.root)).grid(row=0, column=0, padx=10)
        
        ttk.Button(frame, text="Generar Ticket", 
                 command=generar_ticket).grid(row=0, column=1, padx=10)  # Nuevo botón
        
        ttk.Button(frame, text="Salir", 
                 command=self.root.quit).grid(row=0, column=2, padx=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
