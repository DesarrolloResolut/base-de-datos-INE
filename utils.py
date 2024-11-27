from typing import Dict, List
import pandas as pd

def format_nombre_operacion(operacion: Dict) -> str:
    """Formatea el nombre de una operación para mostrar"""
    if not isinstance(operacion, dict):
        return "Operación inválida"
    
    try:
        nombre = operacion.get('nombre', 'Sin nombre')
        id_op = operacion.get('id')
        if id_op is None:
            return f"{nombre} (ID no disponible)"
        return f"{nombre} (ID: {id_op})"
    except Exception as e:
        return "Error al formatear operación"

def format_nombre_tabla(tabla: Dict) -> str:
    """Formatea el nombre de una tabla para mostrar"""
    if not isinstance(tabla, dict):
        return "Tabla inválida"
    
    try:    
        nombre = tabla.get('nombre', 'Sin nombre')
        periodicidad = tabla.get('periodicidad', 'Sin periodicidad')
        id_tabla = tabla.get('id')
        if id_tabla is None:
            return f"{nombre} - {periodicidad} (ID no disponible)"
        return f"{nombre} - {periodicidad} (ID: {id_tabla})"
    except Exception as e:
        return "Error al formatear tabla"

def exportar_a_excel(df: pd.DataFrame, filename: str) -> str:
    """Exporta DataFrame a Excel"""
    try:
        df.to_excel(filename, index=False, engine='openpyxl')
        return "Datos exportados exitosamente a Excel"
    except Exception as e:
        return f"Error al exportar a Excel: {str(e)}"

def exportar_a_csv(df: pd.DataFrame, filename: str) -> str:
    """Exporta DataFrame a CSV"""
    try:
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        return "Datos exportados exitosamente a CSV"
    except Exception as e:
        return f"Error al exportar a CSV: {str(e)}"
