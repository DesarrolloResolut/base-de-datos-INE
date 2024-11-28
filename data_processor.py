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

    @staticmethod
    def calcular_crecimiento_poblacional(df: pd.DataFrame, columna_valor: str = 'Valor', columna_periodo: str = 'Periodo') -> pd.DataFrame:
        """Calcula la tasa de crecimiento poblacional entre períodos consecutivos"""
        if columna_valor not in df.columns or columna_periodo not in df.columns:
            return pd.DataFrame()
            
        # Ordenar por período
        df_sorted = df.sort_values(columna_periodo)
        
        # Calcular el crecimiento porcentual
        df_sorted['Crecimiento'] = df_sorted[columna_valor].pct_change() * 100
        
        return df_sorted

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

    @staticmethod
    def calcular_correlaciones(df: pd.DataFrame, variables: List[str] = None) -> Dict:
        """Calcula la matriz de correlaciones y p-values entre las variables numéricas especificadas"""
        from scipy import stats
        import numpy as np
        
        if variables is None:
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
        from statsmodels.tsa.seasonal import seasonal_decompose
        from scipy import stats
        import numpy as np
        
        # Convertir a serie temporal
        df_ts = df.copy()
        df_ts[columna_fecha] = pd.to_datetime(df_ts[columna_fecha])
        df_ts = df_ts.set_index(columna_fecha)
        
        # Descomposición de la serie temporal
        descomposicion = seasonal_decompose(df_ts[columna_valor], period=12, extrapolate_trend='freq')
        
        # Prueba de tendencia Mann-Kendall
        tendencia, p_valor = stats.kendalltau(df_ts.index.values, df_ts[columna_valor])
        
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