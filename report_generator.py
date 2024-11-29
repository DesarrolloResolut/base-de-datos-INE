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
            categoria: Categoría de datos ('demografia', 'sectores_manufactureros' o 'censo_agrario')
        """
        try:
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_base = f"informe_{municipio.lower()}_{timestamp}"
            
            # Generar informe según formato
            if formato == 'excel':
                if categoria == 'demografia':
                    return ReportGenerator._generar_informe_excel(df, f"{nombre_base}.xlsx", municipio)
                elif categoria == 'censo_agrario':
                    return ReportGenerator._generar_informe_excel_censo_agrario(df, f"{nombre_base}.xlsx")
                else:  # sectores_manufactureros
                    return ReportGenerator._generar_informe_excel_sectores(df, f"{nombre_base}.xlsx")
            elif formato == 'pdf':
                if categoria == 'demografia':
                    return ReportGenerator._generar_informe_pdf(df, nombre_base, municipio)
                elif categoria == 'censo_agrario':
                    return ReportGenerator._generar_informe_pdf_censo_agrario(df, nombre_base)
                else:  # sectores_manufactureros
                    return ReportGenerator._generar_informe_pdf_sectores(df, nombre_base)
            else:
                raise ValueError(f"Formato no válido: {formato}")
        except Exception as e:
            print(f"Error al generar informe: {str(e)}")
            return ""

    @staticmethod
    def _generar_informe_excel(df: pd.DataFrame, filename: str, municipio: str) -> str:
        """Genera informe Excel para datos demográficos"""
        try:
            df.to_excel(filename, index=False, engine='openpyxl')
            return filename
        except Exception as e:
            print(f"Error al generar informe Excel: {str(e)}")
            return ""

    @staticmethod
    def _generar_informe_excel_sectores(df: pd.DataFrame, filename: str) -> str:
        """Genera informe Excel para datos de sectores manufactureros"""
        try:
            df.to_excel(filename, index=False, engine='openpyxl')
            return filename
        except Exception as e:
            print(f"Error al generar informe Excel de sectores: {str(e)}")
            return ""

    @staticmethod
    def _generar_informe_pdf(df: pd.DataFrame, filename: str, municipio: str) -> str:
        """Genera informe PDF para datos demográficos"""
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Título
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, f'Informe Demográfico - {municipio}', ln=True, align='C')
            
            # Añadir contenido
            pdf.set_font('Arial', '', 12)
            
            # Tabla de datos
            pdf.cell(0, 10, 'Datos demográficos:', ln=True)
            
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
            pdf = FPDF()
            pdf.add_page()
            
            # Título
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Informe de Sectores Manufactureros', ln=True, align='C')
            
            # Guardar PDF
            pdf_file = f"{filename}.pdf"
            pdf.output(pdf_file)
            return pdf_file
        except Exception as e:
            print(f"Error al generar informe PDF de sectores: {str(e)}")
            return ""

    @staticmethod
    def _generar_informe_excel_censo_agrario(df: pd.DataFrame, filename: str) -> str:
        """Genera informe Excel para datos del censo agrario"""
        try:
            # Crear una copia del DataFrame y convertir columnas categóricas a string
            df_export = df.copy()
            
            # Convertir columnas categóricas a string
            columnas_categoricas = ['Provincia', 'Comarca', 'Personalidad_Juridica', 'Tipo_Dato']
            for col in columnas_categoricas:
                if col in df_export.columns:
                    df_export[col] = df_export[col].astype(str)
            
            # Limpiar datos
            df_export = df_export.fillna('')
            
            # Ordenar por provincia, comarca y personalidad jurídica
            df_export = df_export.sort_values(['Provincia', 'Comarca', 'Personalidad_Juridica', 'Tipo_Dato'])
            
            # Exportar a Excel
            df_export.to_excel(
                filename,
                index=False,
                engine='openpyxl'
            )
            return filename
        except Exception as e:
            print(f"Error al generar informe Excel del censo agrario: {str(e)}")
            return ""

    @staticmethod
    def _generar_informe_pdf_censo_agrario(df: pd.DataFrame, filename: str) -> str:
        """Genera informe PDF para datos del censo agrario"""
        try:
            # Crear PDF con orientación horizontal para gráficos
            pdf = FPDF(orientation='L')
            pdf.add_page()
            
            # Título
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Informe del Censo Agrario', ln=True, align='C')
            
            # Resumen por tipo de dato
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Resumen por Tipo de Dato', ln=True)
            
            for tipo_dato in df['Tipo_Dato'].unique():
                df_tipo = df[df['Tipo_Dato'] == tipo_dato]
                
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f"\n{tipo_dato}", ln=True)
                
                stats = DataProcessor.calcular_estadisticas(df_tipo, 'Valor')
                pdf.set_font('Arial', '', 11)
                
                for key, value in stats.items():
                    pdf.cell(0, 8, f"{key.capitalize()}: {value:,.2f}", ln=True)
            
            # Resumen por comarca
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Resumen por Comarca', ln=True)
            
            for comarca in df['Comarca'].unique():
                df_comarca = df[df['Comarca'] == comarca]
                
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f"\n{comarca}", ln=True)
                pdf.set_font('Arial', '', 11)
                
                for tipo_dato in df_comarca['Tipo_Dato'].unique():
                    df_tipo = df_comarca[df_comarca['Tipo_Dato'] == tipo_dato]
                    total = df_tipo['Valor'].sum()
                    pdf.cell(0, 8, f"{tipo_dato}: {total:,.2f}", ln=True)
            
            # Guardar PDF
            pdf_file = f"{filename}.pdf"
            pdf.output(pdf_file)
            return pdf_file
        except Exception as e:
            print(f"Error al generar informe PDF del censo agrario: {str(e)}")
            return ""