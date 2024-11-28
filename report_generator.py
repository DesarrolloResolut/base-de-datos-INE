import os
from datetime import datetime
import pandas as pd
from fpdf import FPDF
from data_processor import DataProcessor

class ReportGenerator:
    """Generador de informes para datos del INE"""
    
    @staticmethod
    def generar_informe_completo(df: pd.DataFrame, municipio: str, formato: str = 'excel', categoria: str = 'demografia') -> str:
        """Genera informe completo en el formato especificado
        Args:
            df: DataFrame con los datos
            municipio: Nombre del municipio o 'Todos' para sectores
            formato: Formato del informe ('excel' o 'pdf')
            categoria: Categoría de datos ('demografia' o 'sectores_manufactureros')
        """
        try:
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_base = f"informe_{municipio.lower()}_{timestamp}"
            
            if formato == 'excel':
                # Adaptar el procesamiento según la categoría
                if categoria == 'demografia':
                    return ReportGenerator._generar_informe_excel(df, f"{nombre_base}.xlsx", municipio)
                else:  # sectores_manufactureros
                    return ReportGenerator._generar_informe_excel_sectores(df, f"{nombre_base}.xlsx")
            elif formato == 'pdf':
                if categoria == 'demografia':
                    return ReportGenerator._generar_informe_pdf(df, nombre_base, municipio)
                else:  # sectores_manufactureros
                    return ReportGenerator._generar_informe_pdf_sectores(df, nombre_base)
            else:
                raise ValueError(f"Formato no soportado: {formato}")
                
        except Exception as e:
            print(f"Error al generar informe: {str(e)}")
            return ""

    @staticmethod
    def _generar_informe_excel(df: pd.DataFrame, filename: str, municipio: str) -> str:
        """Genera informe Excel para datos demográficos"""
        try:
            # Crear una copia del DataFrame y limpiar datos
            df_export = df.copy()
            df_export = df_export.fillna('')
            
            # Exportar a Excel
            df_export.to_excel(
                filename,
                index=False,
                engine='openpyxl'
            )
            return filename
        except Exception as e:
            print(f"Error al generar informe Excel: {str(e)}")
            return ""

    @staticmethod
    def _generar_informe_excel_sectores(df: pd.DataFrame, filename: str) -> str:
        """Genera informe Excel para datos de sectores manufactureros"""
        try:
            # Crear una copia del DataFrame y limpiar datos
            df_export = df.copy()
            df_export = df_export.fillna('')
            
            # Ordenar por sector y período
            df_export = df_export.sort_values(['Sector', 'Periodo', 'Tipo'])
            
            # Exportar a Excel
            df_export.to_excel(
                filename,
                index=False,
                engine='openpyxl'
            )
            return filename
        except Exception as e:
            print(f"Error al generar informe Excel: {str(e)}")
            return ""

    @staticmethod
    def _generar_informe_pdf(df: pd.DataFrame, filename: str, municipio: str) -> str:
        """Genera informe PDF para datos demográficos"""
        try:
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
            
            # Guardar PDF
            pdf_file = f"{filename}.pdf"
            pdf.output(pdf_file)
            return pdf_file
            
        except Exception as e:
            print(f"Error al generar informe PDF: {str(e)}")
            return ""

    @staticmethod
    def _generar_informe_pdf_sectores(df: pd.DataFrame, filename: str) -> str:
        """Genera informe PDF para datos de sectores manufactureros"""
        try:
            # Crear PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Título
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Informe de Sectores Manufactureros', ln=True, align='C')
            
            # Datos por sector y tipo
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Datos por Sector', ln=True)
            pdf.set_font('Arial', '', 12)
            
            ultimo_periodo = df['Periodo'].max()
            datos_recientes = df[df['Periodo'] == ultimo_periodo]
            
            for sector in datos_recientes['Sector'].unique():
                pdf.cell(0, 10, f"\n{sector}", ln=True)
                sector_data = datos_recientes[datos_recientes['Sector'] == sector]
                
                for _, row in sector_data.iterrows():
                    pdf.cell(0, 10, f"{row['Tipo']}: {row['Valor']:,.2f}", ln=True)
            
            # Estadísticas básicas por tipo de indicador
            pdf.add_page()
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Estadísticas por Tipo de Indicador', ln=True)
            pdf.set_font('Arial', '', 12)
            
            for tipo in df['Tipo'].unique():
                pdf.cell(0, 10, f"\n{tipo}:", ln=True)
                datos_tipo = df[df['Tipo'] == tipo]
                stats = DataProcessor.calcular_estadisticas(datos_tipo, 'Valor')
                
                for key, value in stats.items():
                    pdf.cell(0, 10, f"{key.capitalize()}: {value:,.2f}", ln=True)
            
            # Guardar PDF
            pdf_file = f"{filename}.pdf"
            pdf.output(pdf_file)
            return pdf_file
            
        except Exception as e:
            print(f"Error al generar informe PDF: {str(e)}")
            return ""
