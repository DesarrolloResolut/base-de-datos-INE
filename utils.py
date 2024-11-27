from typing import Dict, List
import pandas as pd

def format_nombre_operacion(operacion: Dict) -> str:
    """Formatea el nombre de una operación para mostrar"""
    return f"{operacion.get('nombre', '')} ({operacion.get('id', '')})"

def format_nombre_tabla(tabla: Dict) -> str:
    """Formatea el nombre de una tabla para mostrar"""
    return f"{tabla.get('nombre', '')} - {tabla.get('periodicidad', '')}"

def exportar_a_excel(df: pd.DataFrame, filename: str) -> None:
    """Exporta DataFrame a Excel"""
    df.to_excel(filename, index=False, engine='openpyxl')

def exportar_a_csv(df: pd.DataFrame, filename: str) -> None:
    """Exporta DataFrame a CSV"""
    df.to_csv(filename, index=False, encoding='utf-8-sig')
