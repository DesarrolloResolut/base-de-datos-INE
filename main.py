import streamlit as st
import pandas as pd
from api_client import INEApiClient
from data_processor import DataProcessor
from visualizer import DataVisualizer
from utils import (format_nombre_operacion, format_nombre_tabla, 
                  exportar_a_excel, exportar_a_csv)

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
    st.title("📊 Explorador de Población de Albacete - INE")
    
    # Mensaje explicativo sobre los datos
    st.markdown("""
    Esta aplicación muestra los datos oficiales de población de Albacete y sus municipios, proporcionados por el Instituto Nacional de Estadística (INE).
    Los datos incluyen:
    - Población por municipio
    - Distribución por género
    - Evolución temporal
    
    Los datos se actualizan anualmente y provienen de la tabla 2855 del INE.
    """)
    
    # Sidebar para filtros
    with st.sidebar:
        st.header("Filtros")
        
        try:
            # Cargar datos de población
            with st.spinner("Cargando datos de población..."):
                datos = INEApiClient.get_datos_tabla()
                if not datos:
                    st.error("No se pudieron obtener los datos de población.")
                    return
                    
                df = DataProcessor.json_to_dataframe(datos)
                if df.empty:
                    st.error("No hay datos disponibles para mostrar.")
                    return
                
                # Filtros específicos
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
                
                # Aplicar filtros
                filtros = {
                    'Municipio': municipio_seleccionado,
                    'Periodo': periodo_seleccionado,
                    'Genero': genero_seleccionado
                }
                
                df_filtrado = DataProcessor.filtrar_datos(df, filtros)
                st.session_state.datos_actuales = df_filtrado
                
        except Exception as e:
            st.error(f"Error al cargar los datos: {str(e)}")
    
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
            st.subheader("Evolución temporal de la población")
            fig_evolucion = DataVisualizer.crear_grafico_lineas(
                df,
                x='Periodo',
                y='Valor',
                color='Genero',
                titulo=f"Evolución de la Población en {municipio_seleccionado}"
            )
            st.plotly_chart(fig_evolucion, use_container_width=True)
            
            # Gráfico de comparativa por género
            st.subheader("Comparativa por género")
            fig_genero = DataVisualizer.crear_grafico_barras(
                df[df['Periodo'] == df['Periodo'].max()],
                x='Genero',
                y='Valor',
                titulo=f"Distribución por Género en {municipio_seleccionado} ({df['Periodo'].max()})"
            )
            st.plotly_chart(fig_genero, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error al crear los gráficos: {str(e)}")
        
        # Estadísticas básicas
        if st.checkbox("Mostrar estadísticas básicas"):
            try:
                st.subheader("Estadísticas de población")
                stats = DataProcessor.calcular_estadisticas(df, 'Valor')
                if stats:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Población media", f"{stats['media']:.0f}")
                        st.metric("Población mediana", f"{stats['mediana']:.0f}")
                        st.metric("Desviación estándar", f"{stats['desv_std']:.0f}")
                    with col2:
                        st.metric("Población mínima", f"{stats['min']:.0f}")
                        st.metric("Población máxima", f"{stats['max']:.0f}")
            except Exception as e:
                st.error(f"Error al calcular estadísticas: {str(e)}")
        
        # Análisis Avanzado
        st.header("Análisis Avanzado")
        tipo_analisis = st.selectbox(
            "Tipo de análisis",
            ["Tendencias y Proyecciones", "Correlaciones", "Crecimiento Poblacional"]
        )

        if tipo_analisis == "Tendencias y Proyecciones":
            try:
                # Análisis de tendencias
                resultados_tendencia = DataProcessor.analizar_tendencias(df)
                if resultados_tendencia:
                    st.subheader("Análisis de Tendencia Poblacional")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Tendencia de crecimiento", 
                                f"{resultados_tendencia['pendiente']:.2f} habitantes/año")
                        st.metric("R² (Ajuste del modelo)", 
                                f"{resultados_tendencia['r2']:.3f}")
                    
                    # Gráfico de tendencia
                    fig_tendencia = DataVisualizer.crear_grafico_tendencia(
                        df,
                        x='Periodo',
                        y='Valor',
                        titulo=f"Tendencia Poblacional - {municipio_seleccionado}"
                    )
                    st.plotly_chart(fig_tendencia, use_container_width=True)

            except Exception as e:
                st.error(f"Error en el análisis de tendencias: {str(e)}")

        elif tipo_analisis == "Correlaciones":
            try:
                # Análisis de correlaciones
                variables_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
                if len(variables_numericas) > 1:
                    fig_corr = DataVisualizer.crear_heatmap_correlacion(
                        df,
                        variables_numericas,
                        titulo=f"Correlaciones - {municipio_seleccionado}"
                    )
                    st.plotly_chart(fig_corr, use_container_width=True)
                else:
                    st.warning("No hay suficientes variables numéricas para análisis de correlación")

            except Exception as e:
                st.error(f"Error en el análisis de correlaciones: {str(e)}")

        elif tipo_analisis == "Crecimiento Poblacional":
            try:
                # Análisis de crecimiento poblacional
                df_crecimiento = DataProcessor.calcular_crecimiento_poblacional(df)
                if not df_crecimiento.empty:
                    st.subheader("Análisis de Crecimiento Poblacional")
                    fig_crecimiento = DataVisualizer.crear_grafico_lineas(
                        df_crecimiento,
                        x='Periodo',
                        y='Crecimiento',
                        titulo=f"Tasa de Crecimiento Poblacional - {municipio_seleccionado}"
                    )
                    st.plotly_chart(fig_crecimiento, use_container_width=True)

            except Exception as e:
                st.error(f"Error en el análisis de crecimiento: {str(e)}")
        # Exportación
        st.header("Exportar datos")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Exportar a Excel"):
                try:
                    df_export = st.session_state.datos_actuales.copy()
                    nombre_archivo = f"datos_poblacion_{municipio_seleccionado.lower()}.xlsx"
                    mensaje = exportar_a_excel(df_export, nombre_archivo)
                    st.success(mensaje)
                    with open(nombre_archivo, "rb") as f:
                        st.download_button(
                            label="Descargar Excel",
                            data=f,
                            file_name=nombre_archivo,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"Error al exportar a Excel: {str(e)}")
                
        with col2:
            if st.button("Exportar a CSV"):
                try:
                    df_export = st.session_state.datos_actuales.copy()
                    nombre_archivo = f"datos_poblacion_{municipio_seleccionado.lower()}.csv"
                    mensaje = exportar_a_csv(df_export, nombre_archivo)
                    st.success(mensaje)
                    with open(nombre_archivo, "rb") as f:
                        st.download_button(
                            label="Descargar CSV",
                            data=f,
                            file_name=nombre_archivo,
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"Error al exportar a CSV: {str(e)}")

if __name__ == "__main__":
    main()
