import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime
import sqlite3
import reportlab    
from reportlab.lib.pagesizes import letter # type: ignore
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from database import (
    conectar, crear_tablas, agregar_producto,
    obtener_productos, eliminar_producto,
    registrar_venta, agregar_detalle_venta, actualizar_stock
)

class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("ORDICO - Gestión Comercial")
        self.root.geometry("800x600")
        self.carrito = []

        # Crear carpeta para tickets
        if not os.path.exists("tickets"):
            os.makedirs("tickets")

        # Menú principal
        self.menu_frame = ttk.Frame(self.root)
        self.menu_frame.pack(pady=20)

        ttk.Button(self.menu_frame, text="Gestión de Stock",
                   command=self.abrir_gestion_stock).grid(row=0, column=0, padx=10)
        ttk.Button(self.menu_frame, text="Módulo de Ventas",
                   command=self.abrir_modulo_ventas).grid(row=0, column=1, padx=10)
        ttk.Button(self.menu_frame, text="Salir",
                   command=root.quit).grid(row=0, column=2, padx=10)

    # ===== GESTIÓN DE STOCK =====
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
        tree.heading("Precio", text="Precio ($)")
        tree.heading("Stock", text="Stock")
        tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Botones
        ttk.Button(ventana_stock, text="Agregar",
                   command=lambda: self.agregar_producto(
                       entry_nombre.get(),
                       entry_precio.get(),
                       entry_stock.get(),
                       tree)).grid(row=4, column=0, pady=10)

        ttk.Button(ventana_stock, text="Eliminar",
                   command=lambda: self.eliminar_producto(tree)).grid(row=4, column=1, pady=10)

        self.actualizar_tabla_productos(tree)

    def agregar_producto(self, nombre, precio, stock, tree):
        from validaciones import validar_campos_vacios, validar_tipos_datos

        if validar_campos_vacios([nombre, precio, stock]):
            if validar_tipos_datos(precio, stock):
                agregar_producto(nombre, "", float(precio), int(stock))
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

    # ===== MÓDULO DE VENTAS =====
    def abrir_modulo_ventas(self):
        ventana_ventas = tk.Toplevel(self.root)
        ventana_ventas.title("Registrar Venta - ORDICO")
        ventana_ventas.geometry("1200x800")
        ventana_ventas.configure(bg="#F0F0F0")

        # Estilos
        estilo = ttk.Style()
        estilo.configure("Titulo.TLabel", font=("Arial", 16, "bold"),
                         foreground="#2E86C1", background="#F0F0F0")
        estilo.configure("Boton.TButton", font=("Arial", 12),
                         foreground="white", background="#2E86C1")

        # Logo
        try:
            logo = tk.PhotoImage(file="logo.png").subsample(4)
            label_logo = ttk.Label(ventana_ventas, image=logo)
            label_logo.image = logo
            label_logo.grid(row=0, column=0, columnspan=3, pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"No se encontró el logo: {str(e)}")

        # Productos disponibles
        ttk.Label(ventana_ventas, text="Productos Disponibles", style="Titulo.TLabel").grid(row=1, column=0, columnspan=3)
        self.tree_ventas = ttk.Treeview(ventana_ventas, columns=("ID", "Nombre", "Precio", "Stock"), show="headings", height=8)
        self.tree_ventas.heading("ID", text="ID")
        self.tree_ventas.heading("Nombre", text="Nombre")
        self.tree_ventas.heading("Precio", text="Precio ($)")
        self.tree_ventas.heading("Stock", text="Stock")
        self.tree_ventas.grid(row=2, column=0, columnspan=3, padx=20, pady=10)
        self.actualizar_tabla_productos(self.tree_ventas)

        # Cantidad
        ttk.Label(ventana_ventas, text="Cantidad:", font=("Arial", 12), background="#F0F0F0").grid(row=3, column=0, pady=10)
        self.entry_cantidad = ttk.Entry(ventana_ventas, font=("Arial", 12), width=10)
        self.entry_cantidad.grid(row=3, column=1, pady=10)

        # Botones de acción
        ttk.Button(ventana_ventas, text="Agregar al Carrito", style="Boton.TButton",
                   command=self.agregar_al_carrito).grid(row=3, column=2, padx=10, pady=10)

        # Carrito de compras
        ttk.Label(ventana_ventas, text="Carrito de Compra", style="Titulo.TLabel").grid(row=4, column=0, columnspan=3)
        self.tree_carrito = ttk.Treeview(ventana_ventas, columns=("Nombre", "Precio", "Cantidad", "Subtotal"), show="headings", height=6)
        self.tree_carrito.heading("Nombre", text="Nombre")
        self.tree_carrito.heading("Precio", text="Precio ($)")
        self.tree_carrito.heading("Cantidad", text="Cantidad")
        self.tree_carrito.heading("Subtotal", text="Subtotal ($)")
        self.tree_carrito.grid(row=5, column=0, columnspan=3, padx=20, pady=10)

        # Botones finales
        frame_botones = ttk.Frame(ventana_ventas)
        frame_botones.grid(row=6, column=0, columnspan=3, pady=20)

        ttk.Button(frame_botones, text="Finalizar Venta", style="Boton.TButton",
                   command=self.finalizar_venta).grid(row=0, column=0, padx=10)
        ttk.Button(frame_botones, text="Cancelar", style="Boton.TButton",
                   command=ventana_ventas.destroy).grid(row=0, column=1, padx=10)

    def agregar_al_carrito(self):
        seleccionado = self.tree_ventas.selection()
        cantidad = self.entry_cantidad.get()

        if seleccionado and cantidad.isdigit():
            cantidad = int(cantidad)
            id_producto = self.tree_ventas.item(seleccionado[0], 'values')[0]
            nombre = self.tree_ventas.item(seleccionado[0], 'values')[1]
            precio = float(self.tree_ventas.item(seleccionado[0], 'values')[2])
            stock = int(self.tree_ventas.item(seleccionado[0], 'values')[3])

            if cantidad <= stock:
                subtotal = precio * cantidad
                self.carrito.append((id_producto, nombre, precio, cantidad, subtotal))
                self.tree_carrito.insert("", "end", values=(nombre, precio, cantidad, subtotal))
                messagebox.showinfo("Éxito", "Producto agregado al carrito")
            else:
                messagebox.showerror("Error", "Stock insuficiente")
        else:
            messagebox.showerror("Error", "Seleccione un producto y ingrese cantidad válida")

    def finalizar_venta(self):
        if self.carrito:
            total = sum(item[4] for item in self.carrito)
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            id_venta = registrar_venta(fecha, total)

            for item in self.carrito:
                id_producto, nombre, precio, cantidad, subtotal = item
                agregar_detalle_venta(id_venta, id_producto, cantidad)
                actualizar_stock(id_producto, -cantidad)

            self.generar_ticket(id_venta, fecha, total)
            self.carrito.clear()
            self.tree_carrito.delete(*self.tree_carrito.get_children())
            messagebox.showinfo("Éxito", f"Venta registrada!\nTotal: ${total:.2f}")
        else:
            messagebox.showerror("Error", "El carrito está vacío")

    def generar_ticket(self, id_venta, fecha, total):
        try:
            pdf = canvas.Canvas(f"tickets/ticket_{id_venta}.pdf", pagesize=letter)
            pdf.setTitle(f"Ticket de Venta #{id_venta}")

            # Logo
            try:
                logo = ImageReader("logo.png")
                pdf.drawImage(logo, 50, 700, width=100, height=50)
            except FileNotFoundError:
                pdf.drawString(50, 730, "ORDICO - Mayorista")

            # Encabezado
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(180, 730, "ORDICO - Mayorista")
            pdf.setFont("Helvetica", 12)
            pdf.drawString(180, 710, "Av. Principal 123, Maipú")
            pdf.drawString(180, 690, "Tel: +54 261-1234567")

            # Detalles de la venta
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(50, 650, f"Ticket #{id_venta}")
            pdf.setFont("Helvetica", 12)
            pdf.drawString(50, 630, f"Fecha: {fecha}")

            # Productos
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(50, 600, "Productos:")
            y = 580
            for item in self.carrito:
                pdf.setFont("Helvetica", 10)
                pdf.drawString(70, y, f"- {item[1]} x{item[3]}: ${item[4]:.2f}")
                y -= 20

            # Total
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(50, y - 30, f"Total: ${total:.2f}")

            # Pie de página
            pdf.setFont("Helvetica-Oblique", 8)
            pdf.drawString(50, 50, "¡Gracias por su compra! - ORDICO")

            pdf.save()
            messagebox.showinfo("Éxito", f"Ticket generado: tickets/ticket_{id_venta}.pdf")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar ticket: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()