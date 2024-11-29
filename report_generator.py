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
            
            if formato == 'excel':
                # Adaptar el procesamiento según la categoría
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
            # Crear PDF con orientación horizontal para gráficos
            pdf = FPDF(orientation='L')
            pdf.add_page()
            
            # Título
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Informe de Sectores Manufactureros', ln=True, align='C')
            
            # Resumen de indicadores por sector
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Resumen por Sector', ln=True)
            
            ultimo_periodo = df['Periodo'].max()
            datos_recientes = df[df['Periodo'] == ultimo_periodo]
            
            for sector in datos_recientes['Sector'].unique():
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f"\n{sector}", ln=True)
                
                sector_data = datos_recientes[datos_recientes['Sector'] == sector]
                pdf.set_font('Arial', '', 11)
                
                for _, row in sector_data.iterrows():
                    # Formatear valor según el tipo de indicador
                    valor = row['Valor']
                    if 'porcentaje' in row['Tipo'].lower() or '%' in row['Tipo']:
                        valor_str = f"{valor:.1f}%"
                    else:
                        valor_str = f"{valor:,.1f}"
                    
                    pdf.cell(0, 8, f"{row['Tipo']}: {valor_str}", ln=True)
            
            # Estadísticas y análisis
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Estadísticas por Tipo de Indicador', ln=True)
            
            for tipo in df['Tipo'].unique():
                datos_tipo = df[df['Tipo'] == tipo]
                stats = DataProcessor.calcular_estadisticas(datos_tipo, 'Valor')
                
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f"\n{tipo}:", ln=True)
                pdf.set_font('Arial', '', 11)
                
                for key, value in stats.items():
                    if 'porcentaje' in tipo.lower() or '%' in tipo:
                        pdf.cell(0, 8, f"{key.capitalize()}: {value:.1f}%", ln=True)
                    else:
                        pdf.cell(0, 8, f"{key.capitalize()}: {value:,.1f}", ln=True)
            
            # Guardar PDF
            pdf_file = f"{filename}.pdf"
            pdf.output(pdf_file)
            return pdf_file
            
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

        except Exception as e:
            print(f"Error al generar informe PDF: {str(e)}")
            return ""
