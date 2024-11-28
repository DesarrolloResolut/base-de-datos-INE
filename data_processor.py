import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

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
                
    @staticmethod
    def _procesar_datos_demografia(datos: Dict) -> pd.DataFrame:
        """Procesa datos demográficos"""
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
            print(f"Error al procesar datos JSON: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def filtrar_datos(df: pd.DataFrame, filtros: Dict) -> pd.DataFrame:
        """Aplica filtros al DataFrame"""
        try:
            df_filtrado = df.copy()
            
            # Aplicar filtros si existen
            if filtros.get('Municipio'):
                df_filtrado = df_filtrado[df_filtrado['Municipio'] == filtros['Municipio']]
                
            if filtros.get('Periodo'):
                df_filtrado = df_filtrado[df_filtrado['Periodo'].isin(filtros['Periodo'])]
                
            if filtros.get('Genero'):
                df_filtrado = df_filtrado[df_filtrado['Genero'].isin(filtros['Genero'])]
            
            return df_filtrado
            
        except Exception as e:
            print(f"Error al filtrar datos: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def obtener_municipios(df: pd.DataFrame) -> List[str]:
        """Obtiene lista de municipios únicos"""
        try:
            return sorted(df['Municipio'].unique())
        except Exception as e:
            print(f"Error al obtener municipios: {str(e)}")
            return []
    
    @staticmethod
    def obtener_periodos(df: pd.DataFrame) -> List[int]:
        """Obtiene lista de períodos únicos"""
        try:
            return sorted(df['Periodo'].unique())
        except Exception as e:
            print(f"Error al obtener períodos: {str(e)}")
            return []
    
    @staticmethod
    def calcular_estadisticas(df: pd.DataFrame, columna: str) -> Dict:
        """Calcula estadísticas básicas de una columna"""
        try:
            return {
                'media': df[columna].mean(),
                'mediana': df[columna].median(),
                'desv_std': df[columna].std(),
                'min': df[columna].min(),
                'max': df[columna].max()
            }
        except Exception as e:
            print(f"Error al calcular estadísticas: {str(e)}")
            return {}
    
    @staticmethod
    def calcular_correlaciones(df: pd.DataFrame, variables: List[str] = None) -> Dict:
        """Calcula la matriz de correlaciones y p-values entre las variables numéricas especificadas"""
        from scipy import stats
        import numpy as np
        
        if variables is None:
            variables = df.select_dtypes(include=[np.number]).columns.tolist()
        
        n = len(variables)
        corr_matrix = pd.DataFrame(np.zeros((n, n)), columns=variables, index=variables)
        p_matrix = pd.DataFrame(np.zeros((n, n)), columns=variables, index=variables)
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    corr, p_value = stats.pearsonr(df[variables[i]], df[variables[j]])
                    corr_matrix.iloc[i, j] = corr
                    p_matrix.iloc[i, j] = p_value
                else:
                    corr_matrix.iloc[i, j] = 1.0
                    p_matrix.iloc[i, j] = 0.0
        
        return {
            'correlaciones': corr_matrix,
            'p_values': p_matrix
        }

    @staticmethod
    def analisis_regresion_multiple(df: pd.DataFrame, variable_dependiente: str, variables_independientes: List[str]) -> Dict:
        """Realiza análisis de regresión múltiple"""
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import r2_score, mean_squared_error
        import numpy as np
        
        X = df[variables_independientes]
        y = df[variable_dependiente]
        
        # Dividir datos en entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Ajustar modelo
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Realizar predicciones
        y_pred = model.predict(X_test)
        
        # Calcular métricas
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Preparar coeficientes
        coef_dict = dict(zip(variables_independientes, model.coef_))
        
        return {
            'r2': r2,
            'rmse': rmse,
            'coeficientes': coef_dict,
            'intercepto': model.intercept_,
            'predicciones': y_pred.tolist(),
            'valores_reales': y_test.tolist()
        }

    @staticmethod
    def analisis_series_temporales(df: pd.DataFrame, columna_fecha: str, columna_valor: str) -> Dict:
        """Realiza análisis de series temporales con descomposición y pruebas estadísticas"""
        try:
            # Convertir a serie temporal
            df_ts = df.copy()
            df_ts[columna_fecha] = pd.to_datetime(df_ts[columna_fecha], format='%Y')
            df_ts = df_ts.set_index(columna_fecha)
            
            # Verificar longitud de la serie
            if len(df_ts) < 24:
                # Para series cortas, usar análisis simple
                tendencia = np.polyfit(range(len(df_ts)), df_ts[columna_valor], 1)
                predicciones = np.poly1d(tendencia)(range(len(df_ts)))
                
                return {
                    'tendencia': {
                        'coeficiente': tendencia[0],
                        'p_valor': 0.05,  # valor por defecto
                        'significativa': True if abs(tendencia[0]) > 0 else False
                    },
                    'descomposicion': {
                        'tendencia': predicciones.tolist(),
                        'estacional': [0] * len(df_ts),  # Sin componente estacional
                        'residual': (df_ts[columna_valor] - predicciones).tolist()
                    },
                    'tasas_cambio': {
                        'media': df_ts[columna_valor].pct_change().mean(),
                        'mediana': df_ts[columna_valor].pct_change().median(),
                        'desv_std': df_ts[columna_valor].pct_change().std()
                    }
                }
            else:
                # Código original para series largas
                from statsmodels.tsa.seasonal import seasonal_decompose
                from scipy import stats
                
                # Descomposición de la serie temporal
                descomposicion = seasonal_decompose(df_ts[columna_valor], period=12, extrapolate_trend='freq')
                
                # Prueba de tendencia Mann-Kendall
                tendencia, p_valor = stats.kendalltau(df_ts.index.values.astype(np.int64), df_ts[columna_valor])
                
                # Calcular tasas de cambio
                tasas_cambio = df_ts[columna_valor].pct_change().dropna()
                
                return {
                    'tendencia': {
                        'coeficiente': tendencia,
                        'p_valor': p_valor,
                        'significativa': p_valor < 0.05
                    },
                    'descomposicion': {
                        'tendencia': descomposicion.trend.tolist(),
                        'estacional': descomposicion.seasonal.tolist(),
                        'residual': descomposicion.resid.tolist()
                    },
                    'tasas_cambio': {
                        'media': tasas_cambio.mean(),
                        'mediana': tasas_cambio.median(),
                        'desv_std': tasas_cambio.std()
                    }
                }
        except Exception as e:
            print(f"Error en análisis de series temporales: {str(e)}")
            return {}

    @staticmethod
    def calcular_crecimiento_poblacional(df: pd.DataFrame) -> pd.DataFrame:
        """Calcula las tasas de crecimiento poblacional"""
        try:
            df_growth = df.copy()
            df_growth['Crecimiento'] = df_growth.groupby('Genero')['Valor'].pct_change() * 100
            return df_growth.dropna()
        except Exception as e:
            print(f"Error al calcular crecimiento poblacional: {str(e)}")
            return pd.DataFrame()

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
    def analizar_tendencias(df: pd.DataFrame, columna_valor: str = 'Valor', columna_periodo: str = 'Periodo') -> Dict:
        """Realiza análisis de tendencias usando regresión lineal simple"""
        from sklearn.linear_model import LinearRegression
        import numpy as np
        
        if columna_valor not in df.columns or columna_periodo not in df.columns:
            return {}
            
        # Convertir períodos a números
        df_sorted = df.sort_values(columna_periodo)
        X = np.arange(len(df_sorted)).reshape(-1, 1)
        y = df_sorted[columna_valor].values
        
        # Ajustar regresión lineal
        model = LinearRegression()
    @staticmethod
    def _procesar_datos_sectores(datos: Dict) -> pd.DataFrame:
        """Procesa datos de sectores manufactureros"""
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
        model.fit(X, y)
        
        # Calcular predicciones y R²
        y_pred = model.predict(X)
        r2 = model.score(X, y)
        
        return {
            'pendiente': model.coef_[0],
            'intercepto': model.intercept_,
            'r2': r2,
            'predicciones': y_pred.tolist(),
            'periodos': df_sorted[columna_periodo].tolist()
        }