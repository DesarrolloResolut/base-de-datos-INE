import pandas as pd
import numpy as np
from typing import Dict, List

class DataProcessor:
    """Procesamiento de datos del INE"""
    
    @staticmethod
    def json_to_dataframe(datos: Dict) -> pd.DataFrame:
        """Convierte datos JSON del INE a DataFrame"""
        if not datos:
            return pd.DataFrame()
            
        # Extraer datos principales
        if 'Data' in datos:
            df = pd.DataFrame(datos['Data'])
        else:
            return pd.DataFrame()
            
        # Procesar metadatos si están disponibles
        if 'Metadata' in datos:
            metadata = datos['Metadata']
            # Añadir información de variables como columnas
            for var in metadata.get('Variables', []):
                nombre = var.get('Nombre', '')
                valores = var.get('Valores', [])
                if valores:
                    # Crear mapeo de códigos a nombres
                    mapping = {str(v['Codigo']): v['Nombre'] for v in valores}
                    # Aplicar mapeo si la columna existe
                    if nombre in df.columns:
                        df[f"{nombre}_desc"] = df[nombre].map(mapping)
        
        return df
    
    @staticmethod
    def filtrar_datos(df: pd.DataFrame, filtros: Dict) -> pd.DataFrame:
        """Aplica filtros al DataFrame"""
        df_filtered = df.copy()
        
        for columna, valor in filtros.items():
            if columna in df_filtered.columns and valor:
                if isinstance(valor, list):
                    df_filtered = df_filtered[df_filtered[columna].isin(valor)]
                else:
                    df_filtered = df_filtered[df_filtered[columna] == valor]
        
        return df_filtered
    
    @staticmethod
    def calcular_estadisticas(df: pd.DataFrame, columna_valores: str) -> Dict:
        """Calcula estadísticas básicas de una columna"""
        if columna_valores not in df.columns:
            return {}
            
        stats = {
            'media': df[columna_valores].mean(),
            'mediana': df[columna_valores].median(),
            'desv_std': df[columna_valores].std(),
            'min': df[columna_valores].min(),
            'max': df[columna_valores].max()
        }
        return stats
