import pandas as pd
import plotly.io as pio
from datetime import datetime
import os
from typing import Dict, List, Optional
from data_processor import DataProcessor
from visualizer import DataVisualizer

class ReportGenerator:
    """Generador de informes automatizados"""
    
    @staticmethod
    def generar_informe_completo(df: pd.DataFrame, municipio: str, formato: str = 'excel') -> str:
        """
        Genera un informe completo con datos, gráficos y análisis estadístico
        """
        try:
            # Crear nombre de archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"informe_{municipio.lower()}_{timestamp}"
            
            if formato == 'excel':
                return ReportGenerator._generar_informe_excel(df, filename, municipio)
            elif formato == 'csv':
                return ReportGenerator._generar_informe_csv(df, filename, municipio)
            else:
                raise ValueError(f"Formato de informe no soportado: {formato}")
                
        except Exception as e:
            print(f"Error al generar informe: {str(e)}")
            return ""

    @staticmethod
    def _generar_informe_excel(df: pd.DataFrame, filename: str, municipio: str) -> str:
        """Genera informe en formato Excel con múltiples hojas"""
        try:
            # Crear archivo Excel
            excel_file = f"{filename}.xlsx"
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # Hoja 1: Datos principales
                df.to_excel(writer, sheet_name='Datos', index=False)
                
                # Hoja 2: Estadísticas
                stats = pd.DataFrame(DataProcessor.calcular_estadisticas(df, 'Valor'), index=[0])
                stats.to_excel(writer, sheet_name='Estadísticas', index=False)
                
                # Hoja 3: Análisis de crecimiento
                df_growth = DataProcessor.calcular_crecimiento_poblacional(df)
                if not df_growth.empty:
                    df_growth.to_excel(writer, sheet_name='Crecimiento', index=False)
                
                # Hoja 4: Análisis temporal
                resultados_series = DataProcessor.analisis_series_temporales(df, 'Periodo', 'Valor')
                if resultados_series:
                    df_series = pd.DataFrame({
                        'Tendencia': resultados_series['descomposicion']['tendencia'],
                        'Estacional': resultados_series['descomposicion']['estacional'],
                        'Residual': resultados_series['descomposicion']['residual']
                    })
                    df_series.to_excel(writer, sheet_name='Análisis Temporal', index=False)
                
                # Generar y guardar gráficos
                fig_evolucion = DataVisualizer.crear_grafico_lineas(
                    df, 'Periodo', 'Valor', 'Genero',
                    f"Evolución de la Población en {municipio}"
                )
                fig_evolucion.write_image(f"temp_evolucion.png")
                
                fig_genero = DataVisualizer.crear_grafico_barras(
                    df[df['Periodo'] == df['Periodo'].max()],
                    'Genero', 'Valor',
                    f"Distribución por Género en {municipio} ({df['Periodo'].max()})"
                )
                fig_genero.write_image(f"temp_genero.png")

            return excel_file
            
        except Exception as e:
            print(f"Error al generar informe Excel: {str(e)}")
            return ""
        finally:
            # Limpiar archivos temporales
            for temp_file in ['temp_evolucion.png', 'temp_genero.png']:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

    @staticmethod
    def _generar_informe_csv(df: pd.DataFrame, filename: str, municipio: str) -> str:
        """Genera informe en formato CSV con datos principales"""
        try:
            # Crear archivo CSV
            csv_file = f"{filename}.csv"
            
            # Agregar estadísticas como filas adicionales
            stats = DataProcessor.calcular_estadisticas(df, 'Valor')
            stats_df = pd.DataFrame([stats])
            
            # Combinar DataFrames
            df_final = pd.concat([
                df,
                pd.DataFrame([{"Municipio": "ESTADÍSTICAS"}]),  # Separador
                stats_df.assign(Municipio="Media", Periodo="-", Genero="-"),
                stats_df.assign(Municipio="Mediana", Periodo="-", Genero="-"),
                stats_df.assign(Municipio="Desv. Std.", Periodo="-", Genero="-")
            ])
            
            # Guardar a CSV
            df_final.to_csv(csv_file, index=False, encoding='utf-8-sig')
            
            return csv_file
            
        except Exception as e:
            print(f"Error al generar informe CSV: {str(e)}")
            return ""
