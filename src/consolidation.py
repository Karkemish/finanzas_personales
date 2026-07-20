import pandas as pd

def consolidate_to_dataframe(result_dict: dict) -> pd.DataFrame:
    """Convierte el resultado del cleaner en un DataFrame plano listo para Excel."""
    info_general = result_dict.get("info_general", {})
    transactions = result_dict.get("transactions", [])
    
    # 1. Creamos el DataFrame base con las transacciones
    df = pd.DataFrame(transactions)
    
    # Si no hay transacciones, devolvemos un DataFrame vacío con las columnas correctas
    if df.empty:
        return pd.DataFrame(columns=["fecha_compra", "descripcion", "tipo", "monto", "moneda", "categoria"])
    
    # 2. Inyectamos la información general como columnas al principio de la tabla
    for key, value in info_general.items():
        # insert(posición, nombre_columna, valor) -> 0 significa ponerlo al inicio
        df.insert(0, key, value)
        
    return df