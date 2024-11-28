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
        
        # Selector de categorías principal
        categoria_seleccionada = st.selectbox(
            "Categoría:",
            options=list(INEApiClient.CATEGORIES.keys()),
            format_func=lambda x: INEApiClient.CATEGORIES[x]['name']
        )

    # Título dinámico según la categoría
    st.title(f"📊 {INEApiClient.CATEGORIES[categoria_seleccionada]['name']} - INE")
    
    # Mensaje explicativo según la categoría
    if categoria_seleccionada == "provincias":
        st.markdown("""
        Esta aplicación muestra los datos oficiales de población por provincia, proporcionados por el Instituto Nacional de Estadística (INE).
        Los datos incluyen:
        - Población total por provincia
        - Distribución por género
        - Evolución temporal
        """)
    elif categoria_seleccionada == "municipios_habitantes":
        st.markdown("""
        Esta aplicación muestra la distribución de municipios según su población, proporcionados por el Instituto Nacional de Estadística (INE).
        Los datos incluyen:
        - Número de municipios por rango de habitantes
        - Evolución temporal de la distribución
        - Análisis comparativo por rangos
        """)
        st.markdown("""
        Esta aplicación muestra los datos oficiales de sectores manufactureros de alta y media-alta tecnología, proporcionados por el Instituto Nacional de Estadística (INE).
        Los datos incluyen:
        - Número de ocupados
        - Porcentaje sobre el total
        - Distribución por género
        - Análisis por sector
        """)
    
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
                if categoria_seleccionada == "provincias":
                    # Filtro de provincia (por ahora solo Albacete)
                    provincia_seleccionada = st.selectbox(
                        "Provincia:",
                        options=['Albacete'],
                        index=0
                    )
                    
                    # Filtro de municipios
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

                elif categoria_seleccionada == "municipios_habitantes":
                    # Filtro de período
                    periodos = DataProcessor.obtener_periodos(df)
                    periodo_seleccionado = st.multiselect(
                        "Años:",
                        options=periodos,
                        default=periodos[-4:] if len(periodos) > 4 else periodos
                    )
                    
                    # Filtro de rangos
                    rangos = sorted(df['Rango'].unique().tolist())
                    rango_seleccionado = st.multiselect(
                        "Rangos de población:",
                        options=rangos,
                        default=rangos
                    )
                    # Filtro de sector
                    sectores = sorted(df['Sector'].unique().tolist())
                    sector_seleccionado = st.multiselect(
                        "Sector:",
                        options=sectores,
                        default=sectores
                    )
                    
                    # Filtro de período
                    periodos = DataProcessor.obtener_periodos(df)
                    periodo_seleccionado = st.multiselect(
                        "Años:",
                        options=periodos,
                        default=periodos[-4:] if len(periodos) > 4 else periodos
                    )
                    
                    # Filtro de tipo de indicador
                    tipos = sorted(df['Tipo'].unique().tolist())
                    tipo_seleccionado = st.multiselect(
                        "Tipo de indicador:",
                        options=tipos,
                        default=tipos
                    )
            
            # Aplicar filtros según la categoría
            if categoria_seleccionada == "provincias":
                filtros = {
                    'Municipio': municipio_seleccionado,
                    'Periodo': periodo_seleccionado,
                    'Genero': genero_seleccionado
                }
            elif categoria_seleccionada == "municipios_habitantes":
                filtros = {
                    'Periodo': periodo_seleccionado,
                    'Rango': rango_seleccionado
                }
                filtros = {
                    'Sector': sector_seleccionado,
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
            if categoria_seleccionada == "sectores_manufactureros":
                # Resumen actual por sector
                st.subheader("Resumen de Indicadores por Sector")
                ultimo_periodo = df['Periodo'].max()
                df_actual = df[df['Periodo'] == ultimo_periodo]
                
                for sector in df_actual['Sector'].unique():
                    st.write(f"### {sector}")
                    df_sector = df_actual[df_actual['Sector'] == sector]
                    
                    # Crear columnas para métricas
                    cols = st.columns(len(df_sector['Tipo'].unique()))
                    for i, (tipo, datos_tipo) in enumerate(df_sector.groupby('Tipo')):
                        valor = datos_tipo['Valor'].iloc[0]
                        # Formatear según tipo de indicador
                        if 'porcentaje' in tipo.lower() or '%' in tipo:
                            valor_str = f"{valor:.1f}%"
                        else:
                            valor_str = f"{valor:,.0f}"
                        cols[i].metric(tipo, valor_str)
                
                # Gráfico de evolución temporal por sector
                st.subheader("Evolución Temporal por Sector")
                fig_evolucion = DataVisualizer.crear_grafico_lineas(
                    df,
                    x='Periodo',
                    y='Valor',
                    color='Sector',
                    titulo="Evolución temporal por sector y tipo"
                )
                st.plotly_chart(fig_evolucion, use_container_width=True)
                
                # Gráfico comparativo de tipos por sector
                st.subheader("Comparativa por Tipo y Sector")
                df_ultimo = df[df['Periodo'] == df['Periodo'].max()]
                fig_barras = DataVisualizer.crear_grafico_barras(
                    df_ultimo,
                    x='Sector',
                    y='Valor',
                    color='Tipo',
                    titulo=f"Comparativa por sector y tipo ({df['Periodo'].max()})"
                )
                st.plotly_chart(fig_barras, use_container_width=True)
                
            else:  # demografía
                if categoria_seleccionada == "demografia_provincia":
                    # Gráfico de evolución temporal
                    st.subheader("Evolución temporal")
                    fig_evolucion = DataVisualizer.crear_grafico_lineas(
                        df,
                        x='Periodo',
                        y='Valor',
                        color='Genero',
                        titulo="Evolución temporal - Población por género"
                    )
                    st.plotly_chart(fig_evolucion, use_container_width=True)
                    
                    # Gráfico comparativo por género
                    st.subheader("Comparativa por género")
                    fig_comparativa = DataVisualizer.crear_grafico_barras(
                        df[df['Periodo'] == df['Periodo'].max()],
                        x='Genero',
                        y='Valor',
                        titulo=f"Distribución por Género - Provincia Albacete ({df['Periodo'].max()})"
                    )
                    st.plotly_chart(fig_comparativa, use_container_width=True)
                    
                elif categoria_seleccionada == "demografia_municipios":
                    # Gráfico de barras para distribución de municipios
                    st.subheader("Distribución de Municipios por Tamaño")
                    fig_barras = DataVisualizer.crear_grafico_barras(
                        df[df['Periodo'] == df['Periodo'].max()],
                        x='Rango',
                        y='Valor',
                        titulo=f"Municipios por Rango de Población ({df['Periodo'].max()})"
                    )
                    st.plotly_chart(fig_barras, use_container_width=True)
                    
                    # Gráfico de pastel para distribución porcentual
                    st.subheader("Distribución Porcentual de Municipios")
                    fig_pie = DataVisualizer.crear_grafico_pastel(
                        df[df['Periodo'] == df['Periodo'].max()],
                        names='Rango',
                        values='Valor',
                        titulo=f"Distribución Porcentual de Municipios ({df['Periodo'].max()})"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error al crear los gráficos: {str(e)}")
        
        # Estadísticas básicas
        if st.checkbox("Mostrar estadísticas básicas"):
            try:
                st.subheader("Estadísticas")
                if categoria_seleccionada == "sectores_manufactureros":
                    for tipo in df['Tipo'].unique():
                        st.write(f"#### {tipo}")
                        df_tipo = df[df['Tipo'] == tipo]
                        stats = DataProcessor.calcular_estadisticas(df_tipo, 'Valor')
                        if stats:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Media", f"{stats['media']:.2f}")
                                st.metric("Mediana", f"{stats['mediana']:.2f}")
                                st.metric("Desviación estándar", f"{stats['desv_std']:.2f}")
                            with col2:
                                st.metric("Mínimo", f"{stats['min']:.2f}")
                                st.metric("Máximo", f"{stats['max']:.2f}")
                else:
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
                st.subheader("Análisis de Tendencias por Sector")
                
                for sector in df['Sector'].unique():
                    st.write(f"### {sector}")
                    df_sector = df[df['Sector'] == sector]
                    
                    for tipo in df_sector['Tipo'].unique():
                        st.write(f"#### {tipo}")
                        df_tipo = df_sector[df_sector['Tipo'] == tipo]
                        
                        try:
                            resultados_series = DataProcessor.analisis_series_temporales(df_tipo, 'Periodo', 'Valor')
                            if resultados_series:
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Tendencia", 
                                            f"{resultados_series['tendencia']['coeficiente']:.3f}")
                                    st.metric("P-valor", 
                                            f"{resultados_series['tendencia']['p_valor']:.4f}")
                                with col2:
                                    st.metric("Tasa de cambio media", 
                                            f"{resultados_series['tasas_cambio']['media']*100:.2f}%")
                                    st.metric("Volatilidad", 
                                            f"{resultados_series['tasas_cambio']['desv_std']*100:.2f}%")
                        except Exception as e:
                            st.warning(f"No se pudo realizar el análisis de tendencias para {tipo}: {str(e)}")
                            
        elif tipo_analisis == "Correlaciones":
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
                if categoria_seleccionada == "demografia":
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
                else:
                    st.info("El análisis de crecimiento no está disponible para datos de sectores manufactureros")

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
                    "Todos" if categoria_seleccionada == "sectores_manufactureros" else "provincia_albacete",
                    formato=formato,
                    categoria=categoria_seleccionada
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
