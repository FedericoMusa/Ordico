import tkinter as tk
from tkinter import ttk, messagebox
from database import crear_tablas, agregar_producto, obtener_productos, eliminar_producto

class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("ORDICO - Gestión Comercial")
        self.root.geometry("800x600")
        
        # Menú principal
        self.menu_frame = ttk.Frame(self.root)
        self.menu_frame.pack(pady=20)
        
        # Botones
        ttk.Button(self.menu_frame, text="Gestión de Stock", command=self.abrir_gestion_stock).grid(row=0, column=0, padx=10)
        ttk.Button(self.menu_frame, text="Módulo de Ventas", command=self.abrir_modulo_ventas).grid(row=0, column=1, padx=10)
        ttk.Button(self.menu_frame, text="Salir", command=root.quit).grid(row=0, column=2, padx=10)
        
    # ---- Gestión de Stock ----
    def abrir_gestion_stock(self):
        ventana_stock = tk.Toplevel(self.root)
        ventana_stock.title("Gestión de Stock")
        
        # Campos de entrada
        ttk.Label(ventana_stock, text="Nombre:").grid(row=0, column=0, padx=10, pady=5)
        entry_nombre = ttk.Entry(ventana_stock)
        entry_nombre.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(ventana_stock, text="Precio:").grid(row=1, column=0, padx=10, pady=5)
        entry_precio = ttk.Entry(ventana_stock)
        entry_precio.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(ventana_stock, text="Stock:").grid(row=2, column=0, padx=10, pady=5)
        entry_stock = ttk.Entry(ventana_stock)
        entry_stock.grid(row=2, column=1, padx=10, pady=5)
        
        # Tabla de productos
        tree = ttk.Treeview(ventana_stock, columns=("ID", "Nombre", "Precio", "Stock"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Nombre", text="Nombre")
        tree.heading("Precio", text="Precio")
        tree.heading("Stock", text="Stock")
        tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        
        # Botones CRUD
        ttk.Button(ventana_stock, text="Agregar", command=lambda: self.agregar_producto(
            entry_nombre.get(), entry_precio.get(), entry_stock.get(), tree
        )).grid(row=4, column=0, pady=10)
        
        ttk.Button(ventana_stock, text="Eliminar", command=lambda: self.eliminar_producto(tree)).grid(row=4, column=1, pady=10)
        
        # Cargar datos iniciales
        self.actualizar_tabla_productos(tree)

    def agregar_producto(self, nombre, precio, stock, tree):
        from validaciones import validar_campos_vacios, validar_tipos_datos
        if validar_campos_vacios([nombre, precio, stock]):
            if validar_tipos_datos(precio, stock):
                agregar_producto(nombre, "", float(precio), int(stock))  # Descripción vacía por simplicidad
                self.actualizar_tabla_productos(tree)
                messagebox.showinfo("Éxito", "Producto agregado correctamente.")
            else:
                messagebox.showerror("Error", "Precio debe ser numérico y Stock entero.")
        else:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")

    def eliminar_producto(self, tree):
        seleccionado = tree.selection()
        if seleccionado:
            confirmar = messagebox.askyesno("Confirmar", "¿Eliminar este producto?")
            if confirmar:
                id_producto = tree.item(seleccionado[0], 'values')[0]
                eliminar_producto(id_producto)
                self.actualizar_tabla_productos(tree)
                messagebox.showinfo("Éxito", "Producto eliminado.")
        else:
            messagebox.showerror("Error", "Selecciona un producto.")

    def actualizar_tabla_productos(self, tree):
        for item in tree.get_children():
            tree.delete(item)
        productos = obtener_productos()
        for producto in productos:
            tree.insert("", "end", values=(producto[0], producto[1], producto[3], producto[4]))

    # ---- Módulo de Ventas ----
    def abrir_modulo_ventas(self):
        ventana_ventas = tk.Toplevel(self.root)
        ventana_ventas.title("Registrar Venta")
        messagebox.showinfo("Info", "Módulo de ventas en desarrollo.")  # Placeholder

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop() 