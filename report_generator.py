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
            elif formato == 'pdf':
                return ReportGenerator._generar_informe_pdf(df, filename, municipio)
            else:
                raise ValueError(f"Formato de informe no soportado: {formato}")
                
        except Exception as e:
            print(f"Error al generar informe: {str(e)}")
            return ""

    @staticmethod
    def _generar_informe_excel(df: pd.DataFrame, filename: str, municipio: str) -> str:
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
                
                try:
                    # Intentar generar y guardar gráficos
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
                except Exception as e:
                    print(f"Advertencia: No se pudieron generar los gráficos: {str(e)}")
                    # Continuar con el informe sin gráficos

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

    @staticmethod
    def _generar_informe_pdf(df: pd.DataFrame, filename: str, municipio: str) -> str:
        try:
            from fpdf import FPDF
            
            # Crear PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Título
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, f'Informe Demográfico: {municipio}', ln=True, align='C')
            
            # Población total y por género
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Datos de Población', ln=True)
            pdf.set_font('Arial', '', 12)
            
            ultimo_periodo = df['Periodo'].max()
            datos_recientes = df[df['Periodo'] == ultimo_periodo]
            
            for _, row in datos_recientes.iterrows():
                pdf.cell(0, 10, f"{row['Genero']}: {row['Valor']:,.0f} habitantes", ln=True)
            
            # Estadísticas
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Estadísticas Básicas', ln=True)
            pdf.set_font('Arial', '', 12)
            
            stats = DataProcessor.calcular_estadisticas(df, 'Valor')
            for key, value in stats.items():
                pdf.cell(0, 10, f"{key.capitalize()}: {value:,.2f}", ln=True)
            
            # Tendencias
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Análisis de Tendencias', ln=True)
            pdf.set_font('Arial', '', 12)
            
            resultados_series = DataProcessor.analisis_series_temporales(df, 'Periodo', 'Valor')
            if resultados_series:
                tendencia = resultados_series['tendencia']
                pdf.cell(0, 10, f"Coeficiente de tendencia: {tendencia['coeficiente']:.3f}", ln=True)
                pdf.cell(0, 10, f"Significancia (p-valor): {tendencia['p_valor']:.4f}", ln=True)
            
            # Crecimiento
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Crecimiento Poblacional', ln=True)
            pdf.set_font('Arial', '', 12)
            
            df_growth = DataProcessor.calcular_crecimiento_poblacional(df)
            if not df_growth.empty:
                ultimo_crecimiento = df_growth['Crecimiento'].iloc[-1]
                pdf.cell(0, 10, f"Último crecimiento registrado: {ultimo_crecimiento:.2f}%", ln=True)
            
            # Guardar PDF
            pdf_file = f"{filename}.pdf"
            pdf.output(pdf_file)
            return pdf_file
            
        except Exception as e:
            print(f"Error al generar informe PDF: {str(e)}")
            return ""
            return ""
