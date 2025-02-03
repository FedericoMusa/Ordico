import tkinter as tk
from tkinter import ttk, messagebox
from core.database import agregar_producto, obtener_productos, eliminar_producto
from core.validaciones import validar_campos_vacios, validar_tipos_producto

class StockWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Gestión de Stock")
        self.geometry("800x600")
        self.resizable(False, False)
        self.crear_interfaz()

    def crear_interfaz(self):
        # Campos de entrada
        ttk.Label(self, text="Nombre:").grid(row=0, column=0, padx=10, pady=5)
        self.entry_nombre = ttk.Entry(self)
        self.entry_nombre.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(self, text="Precio:").grid(row=1, column=0, padx=10, pady=5)
        self.entry_precio = ttk.Entry(self)
        self.entry_precio.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(self, text="Stock:").grid(row=2, column=0, padx=10, pady=5)
        self.entry_stock = ttk.Entry(self)
        self.entry_stock.grid(row=2, column=1, padx=10, pady=5)
        
        # Tabla
        self.tree = ttk.Treeview(self, columns=("ID", "Nombre", "Precio", "Stock"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Precio", text="Precio")
        self.tree.heading("Stock", text="Stock")
        self.tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        
        # Botones
        ttk.Button(self, text="Agregar", command=self.agregar_producto).grid(row=4, column=0, pady=10)
        ttk.Button(self, text="Eliminar", command=self.eliminar_producto).grid(row=4, column=1, pady=10)
        
        self.actualizar_tabla()

    def actualizar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for producto in obtener_productos():
            self.tree.insert("", "end", values=producto)

    def agregar_producto(self):
        nombre = self.entry_nombre.get()
        precio = self.entry_precio.get()
        stock = self.entry_stock.get()
        
        if validar_campos_vacios([nombre, precio, stock]):
            if validar_tipos_producto(precio, stock):
                agregar_producto(nombre, "", float(precio), int(stock))
                self.actualizar_tabla()
                messagebox.showinfo("Éxito", "Producto agregado!")
            else:
                messagebox.showerror("Error", "Precio debe ser número y Stock entero")
        else:
            messagebox.showerror("Error", "Complete todos los campos")

    def eliminar_producto(self):
        seleccion = self.tree.selection()
        if seleccion:
            id_producto = self.tree.item(seleccion[0])['values'][0]
            eliminar_producto(id_producto)
            self.actualizar_tabla()
            messagebox.showinfo("Éxito", "Producto eliminado!")
        else:
            messagebox.showerror("Error", "Seleccione un producto")