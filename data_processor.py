import pandas as pd
from typing import Dict, List
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Procesamiento de datos del INE"""
    
    @staticmethod
    def json_to_dataframe(data: Dict) -> pd.DataFrame:
        try:
            registros = []
            for item in data:
                # Extraer información del nombre
                nombre_completo = item.get('Nombre', '').split('.')
                municipio = nombre_completo[0].strip() if nombre_completo else 'No especificado'
                
                # Determinar género (HOMBRE/MUJER)
                genero = None
                if len(nombre_completo) > 1:
                    nombre_genero = nombre_completo[1].lower().strip()
                    if 'hombres' in nombre_genero:
                        genero = 'HOMBRE'
                    elif 'mujeres' in nombre_genero:
                        genero = 'MUJER'
                    else:
                        genero = 'Total'
                
                # Procesar datos temporales
                for dato in item.get('Data', []):
                    registro = {
                        'Municipio': municipio,
                        'Genero': genero,
                        'Periodo': str(dato.get('Anyo', '')),
                        'Valor': dato.get('Valor', 0)
                    }
                    registros.append(registro)
            
            df = pd.DataFrame(registros)
            print(f"DataFrame creado con {len(df)} registros")
            print("Columnas:", df.columns.tolist())
            print("Primeras filas:", df.head())
            return df
            
        except Exception as e:
            print(f"Error al procesar JSON: {str(e)}")
            print(f"Estructura de datos recibida: {data[0] if data else 'Sin datos'}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error al procesar JSON: {e}")
            print(f"Columnas disponibles: {list(data[0].keys()) if data else []}")
            return pd.DataFrame()

    @staticmethod
    def filtrar_datos(df: pd.DataFrame, filtros: Dict) -> pd.DataFrame:
        """Filtra el DataFrame según los criterios especificados"""
        df_filtrado = df.copy()
        
        for columna, valores in filtros.items():
            if valores and columna in df_filtrado.columns:
                if isinstance(valores, (list, tuple)):
                    df_filtrado = df_filtrado[df_filtrado[columna].isin(valores)]
                else:
                    df_filtrado = df_filtrado[df_filtrado[columna] == valores]
                    
        return df_filtrado

    @staticmethod
    def agrupar_por_municipio_genero(df: pd.DataFrame) -> pd.DataFrame:
        """Agrupa los datos por municipio y género"""
        return df.pivot_table(
            values='Valor',
            index=['Municipio', 'Periodo'],
            columns='Genero',
            aggfunc='first'
        ).reset_index()

    @staticmethod
    def obtener_municipios(df: pd.DataFrame) -> List[str]:
        """Obtiene la lista de municipios disponibles"""
        return sorted(df['Municipio'].unique().tolist())

    @staticmethod
    def obtener_periodos(df: pd.DataFrame) -> List[str]:
        """Obtiene la lista de períodos disponibles"""
        return sorted(df['Periodo'].unique().tolist())

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