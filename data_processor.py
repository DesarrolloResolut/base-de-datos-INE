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
            
        try:
            # Extraer datos principales
            if isinstance(datos, list):
                # Manejar el caso cuando la respuesta es una lista de objetos
                all_data = []
                for item in datos:
                    if 'Data' in item:
                        all_data.extend(item['Data'])
                    elif isinstance(item, dict):
                        all_data.append(item)
                df = pd.DataFrame(all_data)
            elif isinstance(datos, dict) and 'Data' in datos:
                df = pd.DataFrame(datos['Data'])
            else:
                print("Formato de datos no reconocido:", type(datos))
                return pd.DataFrame()
            
            # Debug logging
            print("Columnas disponibles:", df.columns.tolist())
            print("Primeras filas:", df.head())

            # Mapear nombres de columnas
            if 'T3_Periodo' in df.columns:
                df['Periodo'] = df['T3_Periodo']

            # Convertir columnas numéricas
            if 'Valor' in df.columns:
                df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            
            # Convertir fechas
            if 'Fecha' in df.columns:
                df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')

            # Asegurar que tenemos las columnas necesarias
            columnas_requeridas = ['Fecha', 'Periodo', 'Valor']
            for col in columnas_requeridas:
                if col not in df.columns:
                    print(f"Columna {col} no encontrada en los datos")
                    return pd.DataFrame()
                
            return df
            
        except Exception as e:
            print(f"Error al procesar los datos: {str(e)}")
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
        
    @staticmethod
    def calcular_tasa_natalidad(df: pd.DataFrame, col_nacimientos: str, col_poblacion: str) -> float:
        """Calcula la tasa de natalidad por cada 1000 habitantes"""
        if col_nacimientos not in df.columns or col_poblacion not in df.columns:
            return 0.0
        return (df[col_nacimientos].sum() / df[col_poblacion].sum()) * 1000
        
    @staticmethod
    def calcular_tasa_mortalidad(df: pd.DataFrame, col_defunciones: str, col_poblacion: str) -> float:
        """Calcula la tasa de mortalidad por cada 1000 habitantes"""
        if col_defunciones not in df.columns or col_poblacion not in df.columns:
            return 0.0
        return (df[col_defunciones].sum() / df[col_poblacion].sum()) * 1000
