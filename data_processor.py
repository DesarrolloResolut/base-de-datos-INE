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
                
                # Extraer sector del nombre
                partes_nombre = nombre.split('.')
                sector = partes_nombre[0].strip()
                
                # Identificar tipo de indicador de forma más precisa
                if "Total" in nombre and "ocupados" in nombre.lower() and "%" not in nombre:
                    tipo = "Total ocupados"
                elif "ocupados" in nombre.lower() and "%" in nombre and "mujeres" not in nombre.lower():
                    tipo = "Porcentaje sector"
                elif "Mujeres" in nombre and "%" not in nombre:
                    tipo = "Mujeres ocupadas"
                elif "Mujeres" in nombre and "%" in nombre:
                    tipo = "Porcentaje mujeres"
                else:
                    continue
                
                # Procesar valores
                for valor in valores:
                    # Validar y procesar el valor
                    valor_numerico = valor.get('Valor', 0)
                    if valor_numerico is None:
                        continue
                        
                    registros.append({
                        'Sector': sector,
                        'Tipo': tipo,
                        'Periodo': valor.get('Anyo', 2024),
                        'Valor': valor_numerico
                    })
            
            if not registros:
                raise ValueError("No se encontraron datos válidos para procesar")
                
            df = pd.DataFrame(registros)
            df['Periodo'] = pd.to_numeric(df['Periodo'], errors='coerce')
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            
            # Ordenar por sector y período
            df = df.sort_values(['Sector', 'Periodo', 'Tipo'])
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
        """Realiza análisis de series temporales con descomposición"""
        try:
            # Importar statsmodels
            from statsmodels.tsa.seasonal import seasonal_decompose
            
            # Ordenar datos por período
            df_sorted = df.sort_values(columna_periodo).copy()
            
            # Crear índice temporal usando date_range con frecuencia anual
            df_sorted.index = pd.date_range(
                start=str(df_sorted[columna_periodo].min()),
                periods=len(df_sorted),
                freq='YE'  # Usar YE en lugar de A para año fiscal
            )
            
            # Realizar descomposición
            series = df_sorted[columna_valor]
            decomposition = seasonal_decompose(series, period=1, model='additive')
            
            # Calcular tendencia lineal para comparación
            X = df_sorted[columna_periodo].values.reshape(-1, 1)
            y = df_sorted[columna_valor].values
            
            # Ajustar regresión lineal
            model = LinearRegression()
            model.fit(X, y)
            
            # Calcular predicciones y R²
            y_pred = model.predict(X)
            r2 = model.score(X, y)
            
            # Realizar prueba de tendencia (Mann-Kendall)
            trend, p_value = stats.kendalltau(X.flatten(), y)
            
            # Calcular tasas de cambio
            tasas_cambio = np.diff(y) / y[:-1]
            
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
                'periodos': df_sorted[columna_periodo].tolist(),
                'descomposicion': {
                    'tendencia': decomposition.trend.fillna(method='bfill').fillna(method='ffill').values.tolist(),
                    'estacional': decomposition.seasonal.fillna(0).values.tolist(),
                    'residual': decomposition.resid.fillna(0).values.tolist()
                }
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
