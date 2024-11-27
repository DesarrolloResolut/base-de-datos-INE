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

def main():
    st.title("📊 Explorador de Datos INE")
    
    # Sidebar para búsqueda y filtros
    with st.sidebar:
        st.header("Búsqueda")
        busqueda = st.text_input("Buscar operaciones:", "")
        
        # Obtener y mostrar operaciones
        if busqueda:
            operaciones = INEApiClient.buscar_operaciones(busqueda)
        else:
            operaciones = INEApiClient.get_operaciones()
        
        if operaciones:
            operacion_seleccionada = st.selectbox(
                "Seleccione una operación:",
                options=operaciones,
                format_func=format_nombre_operacion
            )
            
            if operacion_seleccionada:
                # Obtener y mostrar tablas
                tablas = INEApiClient.get_tablas_operacion(
                    operacion_seleccionada['id']
                )
                tabla_seleccionada = st.selectbox(
                    "Seleccione una tabla:",
                    options=tablas,
                    format_func=format_nombre_tabla
                )
                
                # Opciones de descarga
                modo_datos = st.radio(
                    "Tipo de datos:",
                    ["datos", "metadatos"]
                )
                
                if st.button("Cargar datos"):
                    with st.spinner("Cargando datos..."):
                        datos = INEApiClient.get_datos_tabla(
                            tabla_seleccionada['id'],
                            modo_datos
                        )
                        st.session_state.datos_actuales = (
                            DataProcessor.json_to_dataframe(datos)
                        )
    
    # Área principal
    if st.session_state.datos_actuales is not None:
        df = st.session_state.datos_actuales
        
        # Mostrar datos en tabla
        st.header("Datos")
        st.dataframe(df)
        
        # Visualizaciones
        st.header("Visualizaciones")
        cols = st.columns(2)
        
        # Selector de columnas para gráficos
        with cols[0]:
            col_x = st.selectbox("Eje X:", options=df.columns)
            col_y = st.selectbox("Eje Y:", options=df.columns)
            col_color = st.selectbox("Color (opcional):", 
                                   options=['Ninguno'] + list(df.columns))
        
        # Tipo de gráfico
        with cols[1]:
            tipo_grafico = st.selectbox(
                "Tipo de gráfico:",
                ["Líneas", "Barras"]
            )
            
        # Crear y mostrar gráfico
        if tipo_grafico == "Líneas":
            fig = DataVisualizer.crear_grafico_lineas(
                df, col_x, col_y,
                color=None if col_color == 'Ninguno' else col_color
            )
        else:
            fig = DataVisualizer.crear_grafico_barras(
                df, col_x, col_y,
                color=None if col_color == 'Ninguno' else col_color
            )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Estadísticas básicas
        if st.checkbox("Mostrar estadísticas básicas"):
            st.write(DataProcessor.calcular_estadisticas(df, col_y))
        
        # Exportación
        st.header("Exportar datos")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Exportar a Excel"):
                exportar_a_excel(df, "datos_ine.xlsx")
                st.success("Datos exportados a Excel")
        with col2:
            if st.button("Exportar a CSV"):
                exportar_a_csv(df, "datos_ine.csv")
                st.success("Datos exportados a CSV")

if __name__ == "__main__":
    main()
