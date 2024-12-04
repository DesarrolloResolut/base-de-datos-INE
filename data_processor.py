import pandas as pd
from typing import Dict, List, Optional, Any
import json

class DataProcessor:
    @staticmethod
    def procesar_datos(datos: Dict, categoria: str) -> pd.DataFrame:
        """
        Procesa los datos según la categoría especificada
        """
        try:
            # Definir las categorías válidas y sus procesadores correspondientes
            categorias_validas = {
                "demografia": DataProcessor._procesar_datos_demografia,
                "municipios_habitantes": DataProcessor._procesar_datos_municipios,
                "censo_agrario": DataProcessor._procesar_datos_censo_agrario,
                "tasa_empleo": DataProcessor._procesar_datos_empleo,
                "tasa_nacimientos": DataProcessor._procesar_datos_nacimientos,
                "tasa_defunciones": DataProcessor._procesar_datos_defunciones
            }
            
            if categoria not in categorias_validas:
                raise ValueError(f"Categoría no válida: {categoria}")
            
            return categorias_validas[categoria](datos)
            
        except Exception as e:
            raise ValueError(f"Error al procesar datos: {str(e)}")

    @staticmethod
    def filtrar_datos(df: pd.DataFrame, filtros: Dict[str, Any]) -> pd.DataFrame:
        """
        Filtra el DataFrame según los criterios especificados
        """
        try:
            df_filtrado = df.copy()
            
            for columna, valor in filtros.items():
                if columna in df_filtrado.columns and valor is not None:
                    if isinstance(valor, list):
                        df_filtrado = df_filtrado[df_filtrado[columna].isin(valor)]
                    else:
                        df_filtrado = df_filtrado[df_filtrado[columna] == valor]
            
            return df_filtrado
            
        except Exception as e:
            raise ValueError(f"Error al filtrar datos: {str(e)}")

    @staticmethod
    def _procesar_datos_demografia(datos: Dict) -> pd.DataFrame:
        """Procesa datos demográficos"""
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
                
                municipio = partes[0]
                indicador = 'Total habitantes'
                
                # Procesar valores históricos
                for valor in valores:
                    periodo = valor.get('Periodo', '')
                    valor_numerico = valor.get('Valor')
                    
                    if not periodo or valor_numerico is None:
                        continue
                    
                    registros.append({
                        'Municipio': municipio,
                        'Indicador': indicador,
                        'Periodo': periodo,
                        'Valor': float(valor_numerico)
                    })
            
            if not registros:
                raise ValueError("No se encontraron datos demográficos válidos")
            
            # Crear DataFrame
            df = pd.DataFrame(registros)
            
            # Convertir tipos de datos
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            df['Periodo'] = pd.to_numeric(df['Periodo'], errors='coerce')
            
            # Ordenar por período
            df = df.sort_values('Periodo', ascending=False)
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error al procesar datos demográficos: {str(e)}")

    @staticmethod
    def _procesar_datos_municipios(datos: Dict) -> pd.DataFrame:
        """Procesa datos de municipios por habitantes"""
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
                
                # Extraer provincia y rango
                provincia = partes[0]
                rango = 'Total'  # Valor por defecto
                
                # Buscar el rango en las partes del nombre
                for parte in partes:
                    if 'De' in parte and 'habitantes' in parte:
                        rango = parte.strip()
                        break
                
                # Procesar valores históricos
                for valor in valores:
                    periodo = valor.get('Periodo', '')
                    valor_numerico = valor.get('Valor')
                    
                    if not periodo or valor_numerico is None:
                        continue
                    
                    registros.append({
                        'Provincia': provincia,
                        'Rango_Habitantes': rango,
                        'Periodo': periodo,
                        'Valor': float(valor_numerico)
                    })
            
            if not registros:
                raise ValueError("No se encontraron datos de municipios válidos")
            
            # Crear DataFrame
            df = pd.DataFrame(registros)
            
            # Convertir tipos de datos
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            df['Periodo'] = pd.to_numeric(df['Periodo'], errors='coerce')
            
            # Ordenar por período
            df = df.sort_values('Periodo', ascending=False)
            
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
                
                # Extraer partes del nombre
                partes = [p.strip() for p in nombre.split('.')]
                if len(partes) < 2:
                    continue
                
                # Extraer información relevante
                provincia = partes[0]
                tipo_cultivo = ''
                rango_tamano = ''
                
                # Procesar las partes del nombre para identificar tipo de cultivo y rango
                for parte in partes[1:]:
                    if 'ha' in parte.lower():
                        rango_tamano = parte
                    else:
                        tipo_cultivo = parte
                
                if not tipo_cultivo:
                    tipo_cultivo = 'Total'
                if not rango_tamano:
                    rango_tamano = 'Total'
                
                # Procesar valores históricos
                for valor in valores:
                    periodo = valor.get('Periodo', '')
                    valor_numerico = valor.get('Valor')
                    
                    if not periodo or valor_numerico is None:
                        continue
                    
                    registros.append({
                        'Provincia': provincia,
                        'Tipo_Cultivo': tipo_cultivo,
                        'Rango_Tamano': rango_tamano,
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
            df = df.sort_values('Periodo', ascending=False)
            
            # Filtrar para mostrar solo los registros relevantes
            return df[
                (df['Rango_Tamano'] != 'Total') & 
                (df['Tipo_Cultivo'] == 'Total')
            ].copy()
            
        except Exception as e:
            raise ValueError(f"Error al procesar datos del censo agrario: {str(e)}")

    @staticmethod
    def _procesar_datos_empleo(datos: Dict) -> pd.DataFrame:
        """Procesa datos de tasas de empleo"""
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
                provincia = partes[0]
                
                # Procesar valores históricos
                for valor in valores:
                    periodo = valor.get('Periodo', '')
                    valor_numerico = valor.get('Valor')
                    
                    if not periodo or valor_numerico is None:
                        continue
                    
                    registros.append({
                        'Provincia': provincia,
                        'Tipo': 'Empleo',
                        'Periodo': periodo,
                        'Valor': float(valor_numerico)
                    })
            
            if not registros:
                raise ValueError("No se encontraron datos de empleo válidos")
            
            # Crear DataFrame
            df = pd.DataFrame(registros)
            
            # Convertir tipos de datos
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            df['Periodo'] = pd.to_numeric(df['Periodo'], errors='coerce')
            
            # Ordenar por período
            df = df.sort_values('Periodo', ascending=False)
            
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
                provincia = partes[0]
                
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
                
                # Extraer partes del nombre
                partes = [p.strip() for p in nombre.split('.')]
                if len(partes) < 2:
                    continue
                
                # Extraer provincia (ahora tomamos la segunda parte)
                provincia = partes[1]
                
                # Procesar valores históricos
                for valor in valores:
                    periodo = valor.get('NombrePeriodo', '')
                    valor_numerico = valor.get('Valor')
                    
                    if not periodo or valor_numerico is None:
                        continue
                    
                    registros.append({
                        'Provincia': provincia,
                        'Tipo': 'Defunciones',
                        'Periodo': periodo,
                        'Valor': float(valor_numerico)
                    })
            
            if not registros:
                raise ValueError("No se encontraron datos de defunciones válidos")
            
            # Crear DataFrame
            df = pd.DataFrame(registros)
            
            # Convertir tipos de datos
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            df['Periodo'] = pd.to_numeric(df['Periodo'], errors='coerce')
            
            # Ordenar por período
            df = df.sort_values('Periodo', ascending=False)
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error al procesar datos de defunciones: {str(e)}")