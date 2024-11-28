import streamlit as st
import pandas as pd
import numpy as np
from api_client import INEApiClient
from data_processor import DataProcessor
from visualizer import DataVisualizer
from utils import (format_nombre_operacion, format_nombre_tabla, 
                  exportar_a_excel, exportar_a_csv)
from report_generator import ReportGenerator

st.set_page_config(
    page_title="Explorador de Datos INE",
    page_icon="📊",
    layout="wide"
)

# Inicialización de estado de la aplicación
if 'datos_actuales' not in st.session_state:
    st.session_state.datos_actuales = None

@st.cache_data(ttl=3600)
def cargar_operaciones():
    """Carga y cachea las operaciones del INE"""
    try:
        return INEApiClient.get_operaciones()
    except Exception as e:
        st.error(f"Error al cargar operaciones: {str(e)}")
        return []

def main():
    # En la sección de sidebar
    with st.sidebar:
        st.header("Filtros")
        
        # Selector de categorías
        categoria_seleccionada = st.selectbox(
            "Categoría:",
            options=list(INEApiClient.CATEGORIES.keys()),
            format_func=lambda x: INEApiClient.CATEGORIES[x]['name']
        )

    # Título dinámico según la categoría
    st.title(f"📊 {INEApiClient.CATEGORIES[categoria_seleccionada]['name']} - INE")
    
    # Mensaje explicativo según la categoría
    if categoria_seleccionada == "demografia":
        st.markdown("""
        Esta aplicación muestra los datos oficiales de población de Albacete y sus municipios, proporcionados por el Instituto Nacional de Estadística (INE).
        Los datos incluyen:
        - Población por municipio
        - Distribución por género
        - Evolución temporal
        """)
    elif categoria_seleccionada == "sectores_manufactureros":
        st.markdown("""
        Esta aplicación muestra los datos oficiales de sectores manufactureros de alta y media-alta tecnología, proporcionados por el Instituto Nacional de Estadística (INE).
        Los datos incluyen:
        - Número de ocupados
        - Porcentaje sobre el total
        - Distribución por género
        """)
    
    # Sidebar para filtros
    try:
        # Cargar datos según la categoría seleccionada
        with st.spinner(f"Cargando datos de {INEApiClient.CATEGORIES[categoria_seleccionada]['name']}..."):
            datos = INEApiClient.get_datos_tabla(categoria=categoria_seleccionada)
            if not datos:
                st.error(f"No se pudieron obtener los datos de {INEApiClient.CATEGORIES[categoria_seleccionada]['name']}.")
                return
                
            df = DataProcessor.json_to_dataframe(datos, categoria=categoria_seleccionada)
            if df.empty:
                st.error("No hay datos disponibles para mostrar.")
                return
            
            with st.sidebar:
                # Filtros específicos según la categoría
                if categoria_seleccionada == "demografia":
                    # Filtro de municipio
                    municipios = DataProcessor.obtener_municipios(df)
                    municipio_seleccionado = st.selectbox(
                        "Municipio:",
                        options=municipios,
                        index=0 if 'Albacete' in municipios else 0
                    )
                    
                    # Filtro de período
                    periodos = DataProcessor.obtener_periodos(df)
                    periodo_seleccionado = st.multiselect(
                        "Años:",
                        options=periodos,
                        default=periodos[-4:] if len(periodos) > 4 else periodos
                    )
                    
                    # Filtro de género
                    generos = ['Total', 'HOMBRE', 'MUJER']
                    genero_seleccionado = st.multiselect(
                        "Género:",
                        options=generos,
                        default=generos
                    )
                
                elif categoria_seleccionada == "sectores_manufactureros":
                    # Filtro de período
                    periodos = DataProcessor.obtener_periodos(df)
                    periodo_seleccionado = st.multiselect(
                        "Años:",
                        options=periodos,
                        default=periodos[-4:] if len(periodos) > 4 else periodos
                    )
                    
                    # Filtro de tipo de indicador
                    tipos = df['Tipo'].unique().tolist()
                    tipo_seleccionado = st.multiselect(
                        "Tipo de indicador:",
                        options=tipos,
                        default=tipos
                    )
            
            # Aplicar filtros según la categoría
            if categoria_seleccionada == "demografia":
                filtros = {
                    'Municipio': municipio_seleccionado,
                    'Periodo': periodo_seleccionado,
                    'Genero': genero_seleccionado
                }
            elif categoria_seleccionada == "sectores_manufactureros":
                filtros = {
                    'Periodo': periodo_seleccionado,
                    'Tipo': tipo_seleccionado
                }
            
            df_filtrado = DataProcessor.filtrar_datos(df, filtros)
            st.session_state.datos_actuales = df_filtrado
            
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return
    
    # Área principal
    if st.session_state.datos_actuales is not None:
        df = st.session_state.datos_actuales
        
        if df.empty:
            st.warning("No hay datos disponibles para mostrar.")
            return
        
        # Mostrar datos en tabla
        st.header("Datos")
        st.dataframe(df)
        
        # Visualizaciones
        st.header("Visualizaciones")
        
        try:
            # Gráfico de evolución temporal
            st.subheader("Evolución temporal")
            fig_evolucion = DataVisualizer.crear_grafico_lineas(
                df,
                x='Periodo',
                y='Valor',
                color='Genero' if categoria_seleccionada == "demografia" else 'Tipo',
                titulo=f"Evolución temporal - {categoria_seleccionada}"
            )
            st.plotly_chart(fig_evolucion, use_container_width=True)
            
            # Gráfico comparativo
            if categoria_seleccionada == "demografia":
                st.subheader("Comparativa por género")
                fig_comparativa = DataVisualizer.crear_grafico_barras(
                    df[df['Periodo'] == df['Periodo'].max()],
                    x='Genero',
                    y='Valor',
                    titulo=f"Distribución por Género - {municipio_seleccionado} ({df['Periodo'].max()})"
                )
            else:
                st.subheader("Comparativa por tipo")
                fig_comparativa = DataVisualizer.crear_grafico_barras(
                    df[df['Periodo'] == df['Periodo'].max()],
                    x='Tipo',
                    y='Valor',
                    titulo=f"Distribución por Tipo ({df['Periodo'].max()})"
                )
            st.plotly_chart(fig_comparativa, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error al crear los gráficos: {str(e)}")
        
        # Estadísticas básicas
        if st.checkbox("Mostrar estadísticas básicas"):
            try:
                st.subheader("Estadísticas")
                stats = DataProcessor.calcular_estadisticas(df, 'Valor')
                if stats:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Media", f"{stats['media']:.2f}")
                        st.metric("Mediana", f"{stats['mediana']:.2f}")
                        st.metric("Desviación estándar", f"{stats['desv_std']:.2f}")
                    with col2:
                        st.metric("Mínimo", f"{stats['min']:.2f}")
                        st.metric("Máximo", f"{stats['max']:.2f}")
            except Exception as e:
                st.error(f"Error al calcular estadísticas: {str(e)}")
        
        # Análisis Avanzado
        st.header("Análisis Avanzado")
        tipo_analisis = st.selectbox(
            "Tipo de análisis",
            ["Tendencias y Proyecciones", "Correlaciones", "Crecimiento"]
        )

        if categoria_seleccionada == "sectores_manufactureros":
            if tipo_analisis == "Tendencias y Proyecciones":
                st.info("El análisis de tendencias no está disponible para datos de sectores manufactureros.")
                
                # Mostrar resumen actual
                st.subheader("Resumen de Indicadores")
                ultimo_periodo = df['Periodo'].max()
                df_actual = df[df['Periodo'] == ultimo_periodo]
                
                for sector in df_actual['Sector'].unique():
                    st.write(f"### {sector}")
                    df_sector = df_actual[df_actual['Sector'] == sector]
                    
                    cols = st.columns(4)
                    for i, (tipo, valor) in enumerate(df_sector.groupby('Tipo')['Valor'].first().items()):
                        cols[i].metric(tipo, f"{valor:.1f}")
        else:
            if tipo_analisis == "Tendencias y Proyecciones":
                try:
                    resultados_series = DataProcessor.analisis_series_temporales(df, 'Periodo', 'Valor')
                    if resultados_series:
                        st.subheader("Análisis de Series Temporales")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Coeficiente de tendencia", 
                                    f"{resultados_series['tendencia']['coeficiente']:.3f}")
                            st.metric("P-valor", 
                                    f"{resultados_series['tendencia']['p_valor']:.4f}")
                        with col2:
                            st.metric("Tasa de cambio media", 
                                    f"{resultados_series['tasas_cambio']['media']*100:.2f}%")
                            st.metric("Volatilidad", 
                                    f"{resultados_series['tasas_cambio']['desv_std']*100:.2f}%")
                        
                        fig_series = DataVisualizer.crear_grafico_series_temporales(
                            resultados_series,
                            df['Valor'],
                            titulo="Descomposición Temporal"
                        )
                        st.plotly_chart(fig_series, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Error en el análisis de tendencias: {str(e)}")

        if tipo_analisis == "Correlaciones":
            try:
                variables_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
                if len(variables_numericas) > 1:
                    resultados_corr = DataProcessor.calcular_correlaciones(df, variables_numericas)
                    
                    st.subheader("Matriz de Correlaciones")
                    fig_corr = DataVisualizer.crear_heatmap_correlacion(
                        df,
                        variables_numericas,
                        titulo="Correlaciones"
                    )
                    st.plotly_chart(fig_corr, use_container_width=True)
                else:
                    st.warning("No hay suficientes variables numéricas para análisis de correlación")

            except Exception as e:
                st.error(f"Error en el análisis de correlaciones: {str(e)}")

        elif tipo_analisis == "Crecimiento":
            try:
                df_crecimiento = DataProcessor.calcular_crecimiento_poblacional(df)
                if not df_crecimiento.empty:
                    st.subheader("Análisis de Crecimiento")
                    fig_crecimiento = DataVisualizer.crear_grafico_lineas(
                        df_crecimiento,
                        x='Periodo',
                        y='Crecimiento',
                        titulo="Tasa de Crecimiento"
                    )
                    st.plotly_chart(fig_crecimiento, use_container_width=True)

            except Exception as e:
                st.error(f"Error en el análisis de crecimiento: {str(e)}")
        
        # Exportación de informes
        st.header("Exportar Informes")
        
        tipo_informe = st.radio(
            "Tipo de informe",
            ["Informe completo (Excel)", "Informe detallado (PDF)"]
        )

        if st.button("Generar Informe"):
            try:
                df_export = st.session_state.datos_actuales.copy()
                
                if tipo_informe == "Informe completo (Excel)":
                    formato = 'excel'
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                else:  # PDF
                    formato = 'pdf'
                    mime_type = "application/pdf"
                
                nombre_archivo = ReportGenerator.generar_informe_completo(
                    df_export,
                    "Todos" if categoria_seleccionada == "sectores_manufactureros" else municipio_seleccionado,
                    formato=formato
                )
                
                if nombre_archivo:
                    st.success("Informe generado correctamente")
                    with open(nombre_archivo, "rb") as f:
                        st.download_button(
                            label=f"Descargar {tipo_informe.split('(')[0].strip()}",
                            data=f,
                            file_name=nombre_archivo,
                            mime=mime_type
                        )
                else:
                    st.error("Error al generar el informe")
                    
            except Exception as e:
                st.error(f"Error al generar el informe: {str(e)}")

if __name__ == "__main__":
    main()
