import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from sklearn.linear_model import LinearRegression
from scipy import stats

class DataProcessor:
    """Procesador de datos del INE"""
    
    @staticmethod
    def json_to_dataframe(datos: Dict, categoria: str = "demografia") -> pd.DataFrame:
        """Convierte datos JSON a DataFrame según la categoría
        Args:
            datos: Datos en formato JSON
            categoria: Categoría de datos ('demografia' o 'sectores_manufactureros')
        """
        try:
            if categoria == "demografia":
                return DataProcessor._procesar_datos_demografia(datos)
            elif categoria == "sectores_manufactureros":
                return DataProcessor._procesar_datos_sectores(datos)
            else:
                raise ValueError(f"Categoría no soportada: {categoria}")
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
                
                # Determinar género
                if 'HOMBRES' in nombre.upper():
                    genero = 'HOMBRE'
                elif 'MUJERES' in nombre.upper():
                    genero = 'MUJER'
                else:
                    genero = 'Total'
                
                # Extraer municipio
                municipio = nombre.split('.')[0].strip()
                    
                # Procesar valores
                for valor in valores:
                    registros.append({
                        'Municipio': municipio,
                        'Genero': genero,
                        'Periodo': valor.get('Anyo', ''),
                        'Valor': valor.get('Valor', 0)
                    })
            
            # Crear DataFrame
            df = pd.DataFrame(registros)
            
            # Convertir tipos de datos
            df['Periodo'] = pd.to_numeric(df['Periodo'], errors='coerce')
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            
            return df
        except Exception as e:
            raise ValueError(f"Error al procesar datos demográficos: {str(e)}")
    
    @staticmethod
    def _procesar_datos_sectores(datos: Dict) -> pd.DataFrame:
        """Procesa datos de sectores manufactureros"""
        try:
            registros = []
            for dato in datos:
                nombre = dato.get('Nombre', '')
                valores = dato.get('Data', [])
                
                # Extraer tipo de indicador
                tipo = 'Total'
                if 'MUJERES' in nombre.upper():
                    tipo = 'Mujeres'
                elif 'PORCENTAJE' in nombre.upper():
                    tipo = 'Porcentaje'
                    
                # Procesar valores
                for valor in valores:
                    registros.append({
                        'Indicador': nombre,
                        'Tipo': tipo,
                        'Periodo': valor.get('Anyo', ''),
                        'Valor': valor.get('Valor', 0)
                    })
            
            # Crear DataFrame
            df = pd.DataFrame(registros)
            
            # Convertir tipos de datos
            df['Periodo'] = pd.to_numeric(df['Periodo'], errors='coerce')
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            
            return df
        except Exception as e:
            raise ValueError(f"Error al procesar datos de sectores: {str(e)}")

    @staticmethod
    def obtener_municipios(df: pd.DataFrame) -> List[str]:
        """Obtiene lista de municipios disponibles"""
        try:
            if 'Municipio' not in df.columns:
                return []
            return sorted(df['Municipio'].unique().tolist())
        except Exception as e:
            raise ValueError(f"Error al obtener municipios: {str(e)}")

    @staticmethod
    def obtener_periodos(df: pd.DataFrame) -> List[int]:
        """Obtiene lista de períodos disponibles"""
        try:
            if 'Periodo' not in df.columns:
                return []
            return sorted(df['Periodo'].unique().tolist())
        except Exception as e:
            raise ValueError(f"Error al obtener períodos: {str(e)}")

    @staticmethod
    def filtrar_datos(df: pd.DataFrame, filtros: Dict) -> pd.DataFrame:
        """Aplica filtros al DataFrame"""
        try:
            df_filtrado = df.copy()
            
            if filtros.get('Municipio'):
                df_filtrado = df_filtrado[df_filtrado['Municipio'] == filtros['Municipio']]
                
            if filtros.get('Periodo'):
                df_filtrado = df_filtrado[df_filtrado['Periodo'].isin(filtros['Periodo'])]
                
            if filtros.get('Genero'):
                df_filtrado = df_filtrado[df_filtrado['Genero'].isin(filtros['Genero'])]
                
            return df_filtrado
            
        except Exception as e:
            raise ValueError(f"Error al aplicar filtros: {str(e)}")

    @staticmethod
    def calcular_estadisticas(df: pd.DataFrame, columna: str) -> Dict:
        """Calcula estadísticas básicas de una columna"""
        try:
            stats = {
                'media': df[columna].mean(),
                'mediana': df[columna].median(),
                'desv_std': df[columna].std(),
                'min': df[columna].min(),
                'max': df[columna].max()
            }
            return stats
        except Exception as e:
            raise ValueError(f"Error al calcular estadísticas: {str(e)}")

    @staticmethod
    def calcular_correlaciones(df: pd.DataFrame, columnas: List[str]) -> Dict:
        """Calcula matriz de correlaciones entre columnas numéricas"""
        try:
            correlaciones = df[columnas].corr()
            p_values = pd.DataFrame(np.zeros_like(correlaciones), 
                                  index=correlaciones.index,
                                  columns=correlaciones.columns)
            
            for i in range(len(columnas)):
                for j in range(i+1, len(columnas)):
                    stat, p_value = stats.pearsonr(df[columnas[i]], df[columnas[j]])
                    p_values.iloc[i,j] = p_value
                    p_values.iloc[j,i] = p_value
                    
            return {
                'correlaciones': correlaciones,
                'p_values': p_values
            }
        except Exception as e:
            raise ValueError(f"Error al calcular correlaciones: {str(e)}")

    @staticmethod
    def analisis_series_temporales(df: pd.DataFrame, columna_periodo: str, columna_valor: str) -> Dict:
        """Realiza análisis de series temporales"""
        try:
            # Ordenar datos por período
            df_sorted = df.sort_values(columna_periodo)
            
            # Calcular tendencia lineal
            X = df_sorted[columna_periodo].values.reshape(-1, 1)
            y = df_sorted[columna_valor].values
            
            # Ajustar regresión lineal
            model = LinearRegression()
            model.fit(X, y)
            
            # Calcular predicciones y R²
            y_pred = model.predict(X)
            r2 = model.score(X, y)
            
            # Calcular tasas de cambio
            tasas_cambio = np.diff(y) / y[:-1]
            
            # Realizar prueba de tendencia (Mann-Kendall)
            trend, p_value = stats.kendalltau(X.flatten(), y)
            
            return {
                'tendencia': {
                    'coeficiente': float(model.coef_[0]),
                    'intercepto': float(model.intercept_),
                    'r2': float(r2),
                    'significativa': p_value < 0.05,
                    'p_valor': float(p_value)
                },
                'tasas_cambio': {
                    'media': float(np.mean(tasas_cambio)),
                    'desv_std': float(np.std(tasas_cambio))
                },
                'predicciones': y_pred.tolist(),
                'periodos': df_sorted[columna_periodo].tolist()
            }
        except Exception as e:
            raise ValueError(f"Error en análisis de series temporales: {str(e)}")

    @staticmethod
    def calcular_crecimiento_poblacional(df: pd.DataFrame) -> pd.DataFrame:
        """Calcula tasas de crecimiento poblacional"""
        try:
            df_growth = df.copy()
            df_growth = df_growth.sort_values('Periodo')
            
            # Calcular cambio porcentual
            df_growth['Crecimiento'] = df_growth.groupby('Genero')['Valor'].pct_change() * 100
            
            return df_growth
        except Exception as e:
            raise ValueError(f"Error al calcular crecimiento poblacional: {str(e)}")