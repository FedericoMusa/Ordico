def validar_campos_vacios(campos):
    return all(str(campo).strip() != "" for campo in campos)

def validar_tipos_producto(precio, stock):
    try:
        float(precio)
        int(stock)
        return True
    except ValueError:
        return False