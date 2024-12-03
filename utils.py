from typing import Dict, List
import pandas as pd
from datetime import datetime

def _format_periodicidad(periodicidad: str) -> str:
    """Formatea la periodicidad a un formato más amigable"""
    if not periodicidad:
        return "Periodicidad no disponible"
        
    periodicidad = periodicidad.lower()
    mapeo = {
        'anual': 'Anual',
        'mensual': 'Mensual',
        'trimestral': 'Trimestral',
        'semestral': 'Semestral',
        'irregular': 'Irregular'
    }
    return mapeo.get(periodicidad, periodicidad.capitalize())

def _format_fecha(fecha_str: str) -> str:
    """Formatea la fecha a un formato más amigable"""
    if not fecha_str:
        return ""
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        return fecha.strftime("%d/%m/%Y")
    except:
        return fecha_str

def format_nombre_operacion(operacion: Dict) -> str:
    """Formatea el nombre de una operación para mostrar"""
    if not isinstance(operacion, dict):
        return "Operación inválida"
    
    try:
        # Validación de campos obligatorios
        nombre = operacion.get('Nombre') or operacion.get('nombre')
        if not nombre:
            return "Error: Nombre de operación no disponible"
        
        # Obtención de campos adicionales
        cod = operacion.get('Codigo') or operacion.get('codigo', '')
        periodicidad = _format_periodicidad(operacion.get('Periodicidad') or operacion.get('periodicidad', ''))
        ultima_actualizacion = _format_fecha(operacion.get('UltimaActualizacion') or operacion.get('ultima_actualizacion', ''))
        
        # Construcción del string formateado
        partes = [
            f"{nombre}",
            f"Código: {cod}" if cod else None,
            f"Periodicidad: {periodicidad}",
            f"Última actualización: {ultima_actualizacion}" if ultima_actualizacion else None
        ]
        
        # Filtrar None y unir con separadores
        return " | ".join(filter(None, partes))
        
    except Exception as e:
        return f"Error al formatear operación: {str(e)}"

def format_nombre_tabla(tabla: Dict) -> str:
    """Formatea el nombre de una tabla para mostrar"""
    if not isinstance(tabla, dict):
        return "Tabla inválida"
    
    try:    
        nombre = tabla.get('nombre')
        if not nombre:
            return "Error: Nombre de tabla no disponible"
            
        periodicidad = _format_periodicidad(tabla.get('periodicidad', ''))
        id_tabla = tabla.get('id')
        
        partes = [
            nombre,
            f"Periodicidad: {periodicidad}",
            f"ID: {id_tabla}" if id_tabla else None
        ]
        
        return " | ".join(filter(None, partes))
    except Exception as e:
        return f"Error al formatear tabla: {str(e)}"

def exportar_a_excel(df: pd.DataFrame, filename: str) -> str:
    """Exporta DataFrame a Excel con manejo robusto de errores"""
    try:
        if df.empty:
            raise ValueError("No hay datos para exportar")
        
        # Crear una copia del DataFrame y limpiar datos
        df_export = df.copy()
        df_export = df_export.fillna('')  # Manejar valores nulos
        
        # Procesar nombres de columnas para mejor visualización
        df_export.columns = [col.replace('_', ' ').title() for col in df_export.columns]
        
        # Exportar a Excel con formato mejorado
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df_export.to_excel(
                writer,
                index=False,
                sheet_name='Datos INE'
            )
            # Ajustar anchos de columna
            worksheet = writer.sheets['Datos INE']
            for idx, col in enumerate(df_export.columns):
                max_length = max(
                    df_export[col].astype(str).apply(len).max(),
                    len(str(col))
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
        
        return "Datos exportados exitosamente a Excel"
    except ValueError as ve:
        return f"Error de validación: {str(ve)}"
    except PermissionError:
        return "Error: No se tiene permiso para escribir el archivo"
    except Exception as e:
        return f"Error inesperado al exportar a Excel: {str(e)}"

def exportar_a_csv(df: pd.DataFrame, filename: str) -> str:
    """Exporta DataFrame a CSV con manejo robusto de errores"""
    try:
        if df.empty:
            raise ValueError("No hay datos para exportar")
        
        # Crear una copia del DataFrame y limpiar datos
        df_export = df.copy()
        df_export = df_export.fillna('')  # Manejar valores nulos
        
        # Procesar nombres de columnas para mejor visualización
        df_export.columns = [col.replace('_', ' ').title() for col in df_export.columns]
        
        # Exportar a CSV con codificación y formato mejorados
        df_export.to_csv(
            filename,
            index=False,
            encoding='utf-8-sig',  # UTF-8 con BOM para mejor compatibilidad
            sep=';',  # Usar punto y coma para mejor compatibilidad con Excel en español
            quoting=1,  # QUOTE_ALL para mejor manejo de campos especiales
            decimal=',',  # Usar coma como separador decimal (formato español)
            date_format='%d/%m/%Y'  # Formato de fecha español
        )
        return "Datos exportados exitosamente a CSV"
    except ValueError as ve:
        return f"Error de validación: {str(ve)}"
    except PermissionError:
        return "Error: No se tiene permiso para escribir el archivo"
    except Exception as e:
        return f"Error inesperado al exportar a CSV: {str(e)}"
