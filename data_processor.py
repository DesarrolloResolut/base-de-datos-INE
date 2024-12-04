import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging
import json
from sklearn.preprocessing import MinMaxScaler

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Procesador de datos del INE"""
    
    @staticmethod
    def procesar_datos(datos: List[Dict], categoria: str, filtros: Optional[Dict] = None) -> pd.DataFrame:
        """Convierte datos JSON a DataFrame según la categoría
        Args:
            datos: Datos en formato JSON
            categoria: Categoría de datos ('provincias', 'municipios_habitantes', 'censo_agrario', 'tasa_empleo', 'tasa_nacimientos', 'tasa_defunciones')
            filtros: Diccionario de filtros a aplicar (opcional)
        """
        try:
            # Mapeo de categorías a funciones de procesamiento
            categorias_validas = {
                "provincias": DataProcessor._procesar_datos_provincia,
                "municipios_habitantes": DataProcessor._procesar_datos_municipios,
                "censo_agrario": DataProcessor._procesar_datos_censo_agrario,
                "tasa_empleo": DataProcessor._procesar_datos_empleo,
                "tasa_nacimientos": DataProcessor._procesar_datos_nacimientos,
                "tasa_defunciones": DataProcessor._procesar_datos_defunciones
            }
            
            if categoria not in categorias_validas:
                raise ValueError(f"Categoría no válida: {categoria}")
                
            # Procesar datos según la categoría
            df = categorias_validas[categoria](datos)
            
            # Aplicar filtros si existen
            if filtros:
                df = DataProcessor._aplicar_filtros(df, filtros)
                
            return df
            
        except Exception as e:
            error_msg = f"Error al procesar datos: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    @staticmethod
    def _procesar_datos_provincia(datos: Dict) -> pd.DataFrame:
        """Procesa datos demográficos por provincia"""
        try:
            registros = []
            for dato in datos:
                nombre = dato.get('Nombre', '').strip()
                valores = dato.get('Data', [])
                
                if not nombre or not valores:
                    continue
                
                # Extraer provincia y tipo de dato
                partes = [p.strip() for p in nombre.split('.')]
                if len(partes) < 2:
                    continue
                
                provincia = partes[0]
                tipo_dato = partes[-1]
                
                # Procesar valores históricos
                for valor in valores:
                    periodo = valor.get('NombrePeriodo', '')
                    valor_numerico = valor.get('Valor')
                    
                    if not periodo or valor_numerico is None:
                        continue
                    
                    registros.append({
                        'Provincia': provincia,
                        'Tipo': tipo_dato,
                        'Periodo': str(periodo),
                        'Valor': float(valor_numerico)
                    })
            
            if not registros:
                raise ValueError("No se encontraron datos demográficos válidos")
            
            df = pd.DataFrame(registros)
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            df['Periodo'] = pd.to_numeric(df['Periodo'], errors='coerce')
            
            return df.sort_values('Periodo', ascending=False)
            
        except Exception as e:
            raise ValueError(f"Error al procesar datos demográficos: {str(e)}")

    @staticmethod
    def _procesar_datos_municipios(datos: Dict) -> pd.DataFrame:
        """Procesa datos por municipio"""
        try:
            registros = []
            for dato in datos:
                nombre = dato.get('Nombre', '').strip()
                valores = dato.get('Data', [])
                
                if not nombre or not valores:
                    continue
                
                # Extraer municipio y provincia
                partes = nombre.split('.')
                if len(partes) < 2:
                    continue
                    
                municipio = partes[0].strip()
                provincia = partes[1].strip() if len(partes) > 1 else "No especificada"
                
                # Procesar valores históricos
                for valor in valores:
                    periodo = valor.get('Anyo', '')
                    valor_numerico = valor.get('Valor')
                    
                    if not periodo or valor_numerico is None:
                        continue
                        
                    registros.append({
                        'Municipio': municipio,
                        'Provincia': provincia,
                        'Periodo': periodo,
                        'Habitantes': float(valor_numerico)
                    })
                    
            if not registros:
                raise ValueError("No se encontraron datos de municipios válidos")
                
            # Crear DataFrame
            df = pd.DataFrame(registros)
            
            # Convertir tipos de datos
            df['Habitantes'] = pd.to_numeric(df['Habitantes'], errors='coerce')
            df['Periodo'] = pd.to_numeric(df['Periodo'], errors='coerce')
            
            # Ordenar por período y habitantes
            df = df.sort_values(['Periodo', 'Habitantes'], ascending=[False, False])
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error al procesar datos de municipios: {str(e)}")

    @staticmethod
    def _procesar_datos_censo_agrario(datos: Dict) -> pd.DataFrame:
        """Procesa datos del censo agrario"""
        try:
            registros = []
            for dato in datos:
                nombre = dato.get('Nombre', '').strip()
                valores = dato.get('Data', [])
                
                if not nombre or not valores:
                    continue
                    
                # Extraer componentes del nombre
                partes = nombre.split('.')
                if len(partes) < 3:
                    continue
                    
                provincia = partes[0].strip()
                comarca = partes[1].strip()
                tipo_dato = partes[2].strip()
                
                # Procesar valores
                for valor in valores:
                    periodo = valor.get('Anyo', '')
                    valor_numerico = valor.get('Valor')
                    
                    if not periodo or valor_numerico is None:
                        continue
                        
                    registros.append({
                        'Provincia': provincia,
                        'Comarca': comarca,
                        'Tipo_Dato': tipo_dato,
                        'Periodo': periodo,
                        'Valor': float(valor_numerico)
                    })
                    
            if not registros:
                raise ValueError("No se encontraron datos del censo agrario válidos")
                
            # Crear DataFrame
            df = pd.DataFrame(registros)
            
            # Convertir tipos de datos
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            df['Periodo'] = pd.to_numeric(df['Periodo'], errors='coerce')
            
            # Ordenar por período
            df = df.sort_values(['Periodo', 'Provincia', 'Comarca'], ascending=[False, True, True])
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error al procesar datos del censo agrario: {str(e)}")

    @staticmethod
    def _procesar_datos_empleo(datos: Dict) -> pd.DataFrame:
        """Procesa datos de empleo"""
        try:
            registros = []
            for dato in datos:
                nombre = dato.get('Nombre', '').strip()
                valores = dato.get('Data', [])
                
                if not nombre or not valores:
                    continue
                    
                # Extraer componentes del nombre
                partes = nombre.split('.')
                if len(partes) < 2:
                    continue
                    
                tipo_tasa = partes[0].strip()
                provincia = partes[1].strip()
                
                # Procesar valores históricos
                for valor in valores:
                    periodo = valor.get('Periodo', '')
                    valor_numerico = valor.get('Valor')
                    
                    if not periodo or valor_numerico is None:
                        continue
                        
                    registros.append({
                        'Provincia': provincia,
                        'Tipo_Tasa': tipo_tasa,
                        'Periodo': periodo,
                        'Valor': float(valor_numerico)
                    })
                    
            if not registros:
                raise ValueError("No se encontraron datos de empleo válidos")
                
            # Crear DataFrame
            df = pd.DataFrame(registros)
            
            # Convertir tipos de datos
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            
            # Ordenar por período
            df = df.sort_values(['Periodo', 'Provincia'], ascending=[False, True])
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error al procesar datos de empleo: {str(e)}")

    @staticmethod
    def _procesar_datos_nacimientos(datos: Dict) -> pd.DataFrame:
        """Procesa datos de tasas de nacimientos por provincia"""
        try:
            registros = []
            for dato in datos:
                nombre = dato.get('Nombre', '').strip()
                valores = dato.get('Data', [])
                
                if not nombre or not valores:
                    continue
                
                # Extraer partes del nombre
                partes = [p.strip() for p in nombre.split('.')]
                if len(partes) < 2:
                    continue
                
                # Extraer provincia
                provincia = partes[0].strip()
                
                # Procesar valores históricos
                for valor in valores:
                    periodo = valor.get('NombrePeriodo', '')
                    valor_numerico = valor.get('Valor')
                    
                    if not periodo or valor_numerico is None:
                        continue
                    
                    registros.append({
                        'Provincia': provincia,
                        'Tipo': 'Nacimientos',
                        'Periodo': periodo,
                        'Valor': float(valor_numerico)
                    })
            
            if not registros:
                raise ValueError("No se encontraron datos de nacimientos válidos")
            
            # Crear DataFrame
            df = pd.DataFrame(registros)
            
            # Convertir tipos de datos
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            df['Periodo'] = pd.to_numeric(df['Periodo'], errors='coerce')
            
            # Ordenar por período
            df = df.sort_values('Periodo', ascending=False)
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error al procesar datos de nacimientos: {str(e)}")

    @staticmethod
    def _procesar_datos_defunciones(datos: Dict) -> pd.DataFrame:
        """Procesa datos de tasas de defunciones por provincia"""
        try:
            registros = []
            for dato in datos:
                nombre = dato.get('Nombre', '').strip()
                valores = dato.get('Data', [])
                
                if not nombre or not valores:
                    continue
                
                # Extraer provincia y tipo de dato
                partes = [p.strip() for p in nombre.split('.')]
                if len(partes) < 2:
                    continue
                
                provincia = partes[0]
                
                # Procesar valores históricos
                for valor in valores:
                    periodo = valor.get('NombrePeriodo', '')
                    valor_numerico = valor.get('Valor')
                    
                    if not periodo or valor_numerico is None:
                        continue
                    
                    registros.append({
                        'Provincia': provincia,
                        'Tipo': 'Defunciones',
                        'Periodo': str(periodo),
                        'Valor': float(valor_numerico)
                    })
            
            if not registros:
                raise ValueError("No se encontraron datos de defunciones válidos")
            
            df = pd.DataFrame(registros)
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            df['Periodo'] = pd.to_numeric(df['Periodo'], errors='coerce')
            
            return df.sort_values('Periodo', ascending=False)
            
        except Exception as e:
            raise ValueError(f"Error al procesar datos de defunciones: {str(e)}")

    @staticmethod
    def _aplicar_filtros(df: pd.DataFrame, filtros: Dict) -> pd.DataFrame:
        """Aplica filtros al DataFrame"""
        try:
            df_filtrado = df.copy()
            
            # Aplicar cada filtro
            for columna, valor in filtros.items():
                if columna in df_filtrado.columns:
                    if isinstance(valor, (list, tuple)):
                        df_filtrado = df_filtrado[df_filtrado[columna].isin(valor)]
                    else:
                        df_filtrado = df_filtrado[df_filtrado[columna] == valor]
                        
            return df_filtrado
            
        except Exception as e:
            raise ValueError(f"Error al aplicar filtros: {str(e)}")

    @staticmethod
    def calcular_estadisticas(df: pd.DataFrame, columna: str) -> Dict:
        """Calcula estadísticas básicas de una columna numérica"""
        try:
            if columna not in df.columns:
                raise ValueError(f"Columna {columna} no encontrada en el DataFrame")
                
            return {
                'media': df[columna].mean(),
                'mediana': df[columna].median(),
                'desviacion': df[columna].std(),
                'minimo': df[columna].min(),
                'maximo': df[columna].max()
            }
            
        except Exception as e:
            raise ValueError(f"Error al calcular estadísticas: {str(e)}")

    @staticmethod
    def normalizar_valores(df: pd.DataFrame, columna: str) -> pd.DataFrame:
        """Normaliza los valores de una columna usando Min-Max scaling"""
        try:
            if columna not in df.columns:
                raise ValueError(f"Columna {columna} no encontrada en el DataFrame")
                
            df_norm = df.copy()
            scaler = MinMaxScaler()
            df_norm[f"{columna}_normalizado"] = scaler.fit_transform(df_norm[[columna]])
            
            return df_norm
            
        except Exception as e:
            raise ValueError(f"Error al normalizar valores: {str(e)}")

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
    def calcular_correlaciones(df: pd.DataFrame, columnas: List[str]) -> pd.DataFrame:
        """Calcula matriz de correlaciones entre columnas numéricas"""
        try:
            return df[columnas].corr()
        except Exception as e:
            raise ValueError(f"Error al calcular correlaciones: {str(e)}")

    @staticmethod
    def analisis_series_temporales(df: pd.DataFrame, columna_tiempo: str, columna_valor: str, periodo_estacional: int = 4) -> Dict:
        """Realiza análisis de series temporales avanzado
        
        Args:
            df: DataFrame con los datos
            columna_tiempo: Nombre de la columna temporal
            columna_valor: Nombre de la columna con valores
            periodo_estacional: Número de períodos en un ciclo estacional (default 4 para datos trimestrales)
            
        Returns:
            Diccionario con resultados del análisis
        """
        try:
            # Preparar serie temporal
            serie = df.sort_values(columna_tiempo).set_index(columna_tiempo)[columna_valor]
            
            # Descomposición de la serie
            descomposicion = seasonal_decompose(serie, period=periodo_estacional)
            
            # Análisis de tendencia
            x = np.arange(len(serie))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, serie)
            
            # Calcular tasas de cambio
            tasas_cambio = serie.pct_change().dropna()
            
            # Calcular medias móviles
            ma_corto = serie.rolling(window=2).mean()  # Media móvil corta
            ma_medio = serie.rolling(window=4).mean()  # Media móvil media
            ma_largo = serie.rolling(window=8).mean()  # Media móvil larga
            
            # Calcular tasas de crecimiento
            tasa_crecimiento_interanual = serie.pct_change(periods=4) * 100  # Cambio respecto al mismo trimestre del año anterior
            tasa_crecimiento_trimestral = serie.pct_change() * 100  # Cambio respecto al trimestre anterior
            
            # Test de estacionariedad (Dickey-Fuller aumentado)
            from statsmodels.tsa.stattools import adfuller
            adf_test = adfuller(serie.dropna())
            
            # Análisis de estacionalidad
            indices_estacionales = {}
            if len(serie) >= periodo_estacional:
                for i in range(periodo_estacional):
                    estacion_valores = serie.iloc[i::periodo_estacional]
                    indices_estacionales[f'T{i+1}'] = estacion_valores.mean()
            
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
                'medias_moviles': {
                    'corto_plazo': ma_corto,
                    'medio_plazo': ma_medio,
                    'largo_plazo': ma_largo
                },
                'tasas_crecimiento': {
                    'interanual': tasa_crecimiento_interanual,
                    'trimestral': tasa_crecimiento_trimestral
                },
                'estacionalidad': {
                    'indices': indices_estacionales
                },
                'estacionariedad': {
                    'adf_estadistico': adf_test[0],
                    'p_valor': adf_test[1],
                    'valores_criticos': adf_test[4]
                },
                'tasas_cambio': {
                    'media': tasas_cambio.mean(),
                    'desv_std': tasas_cambio.std(),
                    'max': tasas_cambio.max(),
                    'min': tasas_cambio.min()
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

    @staticmethod
    def calcular_indice_gini(df: pd.DataFrame, columna_valor: str = 'Valor') -> float:
        """Calcula el índice de Gini para medir la concentración de explotaciones"""
        try:
            if df.empty:
                return 0.0
                
            # Ordenar valores de menor a mayor
            valores_ordenados = sorted(df[columna_valor].values)
            n = len(valores_ordenados)
            
            if n == 0:
                return 0.0
                
            # Calcular índice de Gini
            numerador = sum((i+1)*yi for i, yi in enumerate(valores_ordenados))
            denominador = n * sum(valores_ordenados)
            
            if denominador == 0:
                return 0.0
                
            return (2 * numerador)/(n * denominador) - (n + 1)/n
            
        except Exception as e:
            raise ValueError(f"Error al calcular índice de Gini: {str(e)}")
    
    @staticmethod
    def calcular_indice_especializacion(df: pd.DataFrame, 
                                      columna_territorio: str = 'Comarca',
                                      columna_tipo: str = 'Tipo_Dato',
                                      columna_valor: str = 'Valor') -> pd.DataFrame:
        """Calcula índices de especialización agraria por territorio"""
        try:
            # Calcular total por territorio
            total_territorio = df.groupby(columna_territorio)[columna_valor].sum()
            total_global = total_territorio.sum()
            
            # Calcular total por tipo
            total_tipo = df.groupby(columna_tipo)[columna_valor].sum()
            
            indices = []
            for territorio in df[columna_territorio].unique():
                for tipo in df[columna_tipo].unique():
                    valor_local = df[
                        (df[columna_territorio] == territorio) & 
                        (df[columna_tipo] == tipo)
                    ][columna_valor].sum()
                    
                    # Calcular índice de especialización
                    ie = (valor_local / total_territorio[territorio]) / (total_tipo[tipo] / total_global)
                    
                    indices.append({
                        'Territorio': territorio,
                        'Tipo': tipo,
                        'Indice_Especializacion': ie
                    })
            
            return pd.DataFrame(indices)
            
        except Exception as e:
            raise ValueError(f"Error al calcular índices de especialización: {str(e)}")
    
    @staticmethod
    def analizar_eficiencia_agraria(df: pd.DataFrame) -> pd.DataFrame:
        """Analiza la eficiencia agraria relacionando SAU y PET"""
        try:
            # Filtrar datos de SAU y PET
            df_sau = df[df['Tipo_Dato'] == 'SAU (ha.)'].copy()
            df_pet = df[df['Tipo_Dato'] == 'PET (miles €)'].copy()
            
            resultados = []
            for comarca in df_sau['Comarca'].unique():
                sau_total = df_sau[df_sau['Comarca'] == comarca]['Valor'].sum()
                pet_total = df_pet[df_pet['Comarca'] == comarca]['Valor'].sum()
                
                # Calcular indicadores de eficiencia
                if sau_total > 0:
                    eficiencia = pet_total / sau_total  # PET por hectárea
                else:
                    eficiencia = 0
                    
                resultados.append({
                    'Comarca': comarca,
                    'SAU_Total': sau_total,
                    'PET_Total': pet_total,
                    'Eficiencia_PET_por_ha': eficiencia
                })
            
            return pd.DataFrame(resultados)
            
        except Exception as e:
            raise ValueError(f"Error al analizar eficiencia agraria: {str(e)}")
    
    @staticmethod
    def analizar_distribucion_tamano(df: pd.DataFrame) -> Dict:
        """Analiza la distribución por tamaño de las explotaciones"""
        try:
            # Filtrar datos de explotaciones
            df_expl = df[df['Tipo_Dato'] == 'Número de explotaciones'].copy()
            
            total_explotaciones = df_expl['Valor'].sum()
            
            # Calcular totales
            totales_juridica = df_expl.groupby('Personalidad_Juridica')['Valor'].sum()
            totales_territorial = df_expl.groupby('Comarca')['Valor'].sum()
            
            # Calcular porcentajes
            porcentajes_juridica = (totales_juridica / total_explotaciones) * 100
            porcentajes_territorial = (totales_territorial / total_explotaciones) * 100
            
            # Crear DataFrames separados
            dist_juridica = pd.DataFrame({
                'total': totales_juridica,
                'porcentaje': porcentajes_juridica
            })
            
            dist_territorial = pd.DataFrame({
                'total': totales_territorial,
                'porcentaje': porcentajes_territorial
            })
            
            # Construir diccionario de resultados
            stats = {
                'total_explotaciones': total_explotaciones,
                'distribucion_juridica': dist_juridica.to_dict('index'),
                'distribucion_territorial': dist_territorial.to_dict('index')
            }
            
            return stats
            
        except Exception as e:
            raise ValueError(f"Error al analizar distribución por tamaño: {str(e)}")

    
    @staticmethod
    def _procesar_datos_empleo(datos: Dict) -> pd.DataFrame:
        """Procesa datos de empleo (tasas de actividad, paro y empleo)"""
        try:
            registros = []
            for dato in datos:
                nombre = dato.get('Nombre', '').strip()
                valores = dato.get('Data', [])
                
                if not nombre or not valores:
                    continue
                
                # Extraer información del nombre usando split('.')
                partes = [p.strip() for p in nombre.split('.')]
                if len(partes) < 3:
                    continue
                
                # Extraer indicador (primer elemento)
                indicador = partes[0].strip()
                if not any(tasa in indicador.lower() for tasa in ['tasa de actividad', 'tasa de paro', 'tasa de empleo']):
                    continue
                
                # Normalizar el indicador
                if 'actividad' in indicador.lower():
                    indicador = 'Tasa de actividad'
                elif 'paro' in indicador.lower():
                    indicador = 'Tasa de paro'
                elif 'empleo' in indicador.lower():
                    indicador = 'Tasa de empleo'
                
                # Extraer género (segundo elemento)
                genero = partes[1].strip()
                if 'hombres' in genero.lower():
                    genero = 'Hombres'
                elif 'mujeres' in genero.lower():
                    genero = 'Mujeres'
                else:
                    genero = 'Ambos sexos'
                
                # Extraer región (tercer elemento)
                region = partes[2].strip()
                if not region:
                    region = 'Total Nacional'
                
                # Procesar valores históricos
                for valor in valores:
                    periodo = valor.get('Periodo', '')
                    valor_numerico = valor.get('Valor')
                    
                    # Validar que el período y valor existan y no sean nulos
                    if not periodo or valor_numerico is None:
                        continue
                        
                    # Crear registro con los datos procesados
                    registros.append({
                        'Indicador': indicador,
                        'Genero': genero,
                        'Region': region,
                        'Periodo': periodo,
                        'Valor': float(valor_numerico)  # Asegurar que el valor sea float
                    })
            
            if not registros:
                raise ValueError("No se encontraron datos de empleo válidos para procesar")
            
            # Crear DataFrame
            df = pd.DataFrame(registros)
            
            # Convertir el valor a numérico manteniendo decimales
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            
            # Ordenar por período
            df = df.sort_values('Periodo', ascending=False)
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error al procesar datos de empleo: {str(e)}")


    @staticmethod
    def _extraer_personalidad_juridica(nombre: str) -> str:
        """Extrae la personalidad jurídica del nombre del dato"""
        nombre_lower = nombre.lower()
        if 'persona física' in nombre_lower:
            return 'Persona Física'
        elif 'persona jurídica' in nombre_lower:
            return 'Persona Jurídica'
        elif 'sociedad mercantil' in nombre_lower:
            return 'Sociedad Mercantil'
        elif 'cooperativa' in nombre_lower:
            return 'Cooperativa'
        return 'Total'

    @staticmethod
    def filtrar_datos_por_tipo(df: pd.DataFrame, tipo: str = 'superficie', tipo_censo: str = 'explotaciones_tamano') -> pd.DataFrame:
        """Filtra los datos según el tipo y el tipo de censo
        
        Args:
            df: DataFrame a filtrar
            tipo: Tipo de datos ('superficie' o 'tamaño')
            tipo_censo: Tipo de censo ('explotaciones_tamano' o 'distribucion_superficie')
        """
        df_filtrado = df.copy()
        
        if tipo_censo == 'distribucion_superficie':
            return df_filtrado[df_filtrado['Tipo_Cultivo'] != 'Total'].copy()
        else:  # tipo_censo == 'explotaciones_tamano'
            if tipo.lower() == 'superficie':
                return df_filtrado[
                    (df_filtrado['Rango_Tamano'] == 'Total') & 
                    (df_filtrado['Tipo_Cultivo'] != 'Total')
                ].copy()
            else:  # tipo == 'tamaño'
                return df_filtrado[
                    (df_filtrado['Rango_Tamano'] != 'Total') & 
                    (df_filtrado['Tipo_Cultivo'] == 'Total')

                ].copy()