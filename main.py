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
                stats = DataProcessor.calcular_estadisticas(df, col_y)
                if stats:
                    st.write({
                        "Media": stats['media'],
                        "Mediana": stats['mediana'],
                        "Desviación estándar": stats['desv_std'],
                        "Mínimo": stats['min'],
                        "Máximo": stats['max']
                    })
            except Exception as e:
                st.error(f"Error al calcular estadísticas: {str(e)}")
        
        # Exportación
        st.header("Exportar datos")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Exportar a Excel"):
                mensaje = exportar_a_excel(df, "datos_ine.xlsx")
                st.success(mensaje)
        with col2:
            if st.button("Exportar a CSV"):
                mensaje = exportar_a_csv(df, "datos_ine.csv")
                st.success(mensaje)

if __name__ == "__main__":
    main()
