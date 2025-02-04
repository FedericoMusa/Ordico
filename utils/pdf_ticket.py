# utils/pdf_ticket.py (versión mejorada)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generar_ticket(datos_venta):
    """Genera PDF con datos de venta."""
    nombre_archivo = f"ticket_{datos_venta['id']}.pdf"
    c = canvas.Canvas(nombre_archivo, pagesize=A4)
    
    # Diseño básico del ticket
    c.drawString(100, 800, f"Ticket #: {datos_venta['id']}")
    c.drawString(100, 780, f"Cliente: {datos_venta['cliente']}")
    c.drawString(100, 760, f"Total: ${datos_venta['total']:.2f}")
    
    c.save()
    return nombre_archivo
