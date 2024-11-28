import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose

class DataProcessor:
    """Procesador de datos del INE"""
    
    @staticmethod
    def json_to_dataframe(datos: Dict, categoria: str = "provincias") -> pd.DataFrame:
        """Convierte datos JSON a DataFrame según la categoría
        Args:
            datos: Datos en formato JSON
            categoria: Categoría de datos ('provincias' o 'municipios_habitantes')
        """
        try:
            if categoria == "provincias":
                return DataProcessor._procesar_datos_demografia(datos)
            elif categoria == "municipios_habitantes":
                return DataProcessor._procesar_datos_municipios(datos)
            else:
                raise ValueError(f"Categoría no válida: {categoria}")
        except Exception as e:
            raise ValueError(f"Error al procesar datos: {str(e)}")

    @staticmethod
    def _procesar_datos_demografia(datos: Dict) -> pd.DataFrame:
        """Procesa datos demográficos"""
        try:
            registros = []
            for dato in datos:
                nombre = dato.get('Nombre', '')
                valores = dato.get('Data', [])
                cod = dato.get('COD', '')
                
                # Procesar datos según el código
                if cod == 'DPOP160':  # Total
                    genero = 'Total'
                    municipio = 'Total'
                elif cod == 'DPOP161':  # Hombres
                    genero = 'HOMBRE'
                    municipio = 'Total'
                elif cod == 'DPOP162':  # Mujeres
                    genero = 'MUJER'
                    municipio = 'Total'
                else:
                    # Procesar otros datos municipales
                    partes = nombre.split('.')
                    municipio = partes[0].strip() if len(partes) > 1 else nombre.split(',')[0].strip()
                    if 'Hombres' in nombre:
                        genero = 'HOMBRE'
                    elif 'Mujeres' in nombre:
                        genero = 'MUJER'
                    else:
                        genero = 'Total'
                
                # Procesar valores
                for valor in valores:
                    registros.append({
                        'Municipio': municipio,
                        'Periodo': valor.get('NombrePeriodo', ''),
                        'Valor': valor.get('Valor', 0),
                        'Genero': genero
                    })
            
            if not registros:
                raise ValueError("No se encontraron datos demográficos")
                
            # Crear DataFrame
            df = pd.DataFrame(registros)
            
            # Convertir tipos de datos
            df['Periodo'] = pd.to_numeric(df['Periodo'], errors='coerce')
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error al procesar datos demográficos: {str(e)}")

    @staticmethod
    def _procesar_datos_municipios(datos: Dict) -> pd.DataFrame:
        """Procesa datos de municipios por rango de habitantes"""
        try:
            registros = []
            for dato in datos:
                nombre = dato.get('Nombre', '')
                valores = dato.get('Data', [])
                
                # Ignorar datos nacionales
                if nombre.startswith('Total Nacional'):
                    continue
                    
                # Extraer provincia y rango
                partes = nombre.split(',')
                if len(partes) < 2:
                    continue
                    
                codigo_provincia = partes[0].strip().split()[0]
                nombre_provincia = ' '.join(partes[0].strip().split()[1:])
                rango = partes[1].strip()
                
                # Procesar valores usando NombrePeriodo como año
                for valor in valores:
                    registros.append({
                        'Provincia': nombre_provincia,
                        'Codigo': codigo_provincia,
                        'Rango': rango,
                        'Periodo': valor.get('NombrePeriodo', ''),
                        'Valor': valor.get('Valor', 0)
                    })
            
            if not registros:
                raise ValueError("No se encontraron datos de municipios")
                
            # Crear DataFrame
            df = pd.DataFrame(registros)
            
            # Convertir tipos de datos
            df['Periodo'] = pd.to_numeric(df['Periodo'], errors='coerce')
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error al procesar datos de municipios: {str(e)}")

    @staticmethod
    def obtener_municipios(df: pd.DataFrame) -> List[str]:
        """Obtiene lista de municipios disponibles"""
        if 'Municipio' in df.columns:
            return sorted(df['Municipio'].unique().tolist())
        return []

    @staticmethod
    def obtener_periodos(df: pd.DataFrame) -> List[int]:
        """Obtiene lista de períodos disponibles"""
        return sorted(df['Periodo'].unique().tolist())

    @staticmethod
    def filtrar_datos(df: pd.DataFrame, filtros: Dict) -> pd.DataFrame:
        """Filtra DataFrame según criterios especificados"""
        try:
            df_filtrado = df.copy()
            
            for campo, valores in filtros.items():
                if valores and campo in df_filtrado.columns:
                    if isinstance(valores, list):
                        df_filtrado = df_filtrado[df_filtrado[campo].isin(valores)]
                    else:
                        df_filtrado = df_filtrado[df_filtrado[campo] == valores]
            
            return df_filtrado
            
        except Exception as e:
            raise ValueError(f"Error al filtrar datos: {str(e)}")

    @staticmethod
    def calcular_estadisticas(df: pd.DataFrame, columna: str) -> Dict:
        """Calcula estadísticas básicas para una columna"""
        try:
            if columna not in df.columns:
                raise ValueError(f"Columna {columna} no encontrada en el DataFrame")
                
            return {
                'media': df[columna].mean(),
                'mediana': df[columna].median(),
                'desv_std': df[columna].std(),
                'min': df[columna].min(),
                'max': df[columna].max()
            }
        except Exception as e:
            raise ValueError(f"Error al calcular estadísticas: {str(e)}")

    @staticmethod
    def calcular_correlaciones(df: pd.DataFrame, columnas: List[str]) -> pd.DataFrame:
        """Calcula matriz de correlaciones entre columnas numéricas"""
        try:
            return df[columnas].corr()
        except Exception as e:
            raise ValueError(f"Error al calcular correlaciones: {str(e)}")

    @staticmethod
    def analisis_series_temporales(df: pd.DataFrame, columna_tiempo: str, columna_valor: str) -> Dict:
        """Realiza análisis de series temporales"""
        try:
            # Preparar serie temporal
            serie = df.sort_values(columna_tiempo).set_index(columna_tiempo)[columna_valor]
            
            # Descomposición de la serie
            descomposicion = seasonal_decompose(serie, period=1)
            
            # Análisis de tendencia
            x = np.arange(len(serie))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, serie)
            
            # Calcular tasas de cambio
            tasas_cambio = serie.pct_change().dropna()
            
            return {
                'descomposicion': {
                    'tendencia': descomposicion.trend,
                    'estacional': descomposicion.seasonal,
                    'residual': descomposicion.resid
                },
                'tendencia': {
                    'coeficiente': slope,
                    'intercepto': intercept,
                    'r_cuadrado': r_value**2,
                    'p_valor': p_value,
                    'error_std': std_err
                },
                'tasas_cambio': {
                    'media': tasas_cambio.mean(),
                    'desv_std': tasas_cambio.std()
                }
            }
        except Exception as e:
            raise ValueError(f"Error en análisis de series temporales: {str(e)}")

    @staticmethod
    def calcular_crecimiento_poblacional(df: pd.DataFrame) -> pd.DataFrame:
        """Calcula tasas de crecimiento poblacional"""
        try:
            # Filtrar datos totales y ordenar por período
            df_total = df[df['Genero'] == 'Total'].copy()
            df_total = df_total.sort_values('Periodo')
            
            # Calcular crecimiento anual por municipio
            df_total['Crecimiento'] = df_total.groupby('Municipio')['Valor'].pct_change() * 100
            
            return df_total
        except Exception as e:
            raise ValueError(f"Error al calcular crecimiento poblacional: {str(e)}")
