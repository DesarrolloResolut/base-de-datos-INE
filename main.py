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
    st.title("📊 Explorador de Población Residente - INE")
    
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
                # Filtro de fecha
                fechas = sorted(df['Periodo'].unique())
                fecha_seleccionada = st.selectbox(
                    "Fecha:",
                    options=fechas,
                    index=len(fechas)-1 if fechas else 0
                )
                
                # Filtro de sexo
                sexos = sorted(df['Sexo_desc'].unique())
                sexo_seleccionado = st.multiselect(
                    "Sexo:",
                    options=sexos,
                    default=sexos
                )
                
                # Filtro de edad
                edades = sorted(df['Edad_desc'].unique())
                edad_seleccionada = st.multiselect(
                    "Grupo de edad:",
                    options=edades,
                    default=edades[:5]  # Primeros 5 grupos por defecto
                )
                
                # Aplicar filtros
                filtros = {
                    'Periodo': fecha_seleccionada,
                    'Sexo_desc': sexo_seleccionado,
                    'Edad_desc': edad_seleccionada
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
        cols = st.columns(2)
        
        # Selector de columnas para gráficos
        with cols[0]:
            col_x = st.selectbox("Variable eje X:", options=df.columns)
            col_y = st.selectbox("Variable eje Y:", options=df.columns)
            col_color = st.selectbox("Variable de color (opcional):", 
                                   options=['Ninguno'] + list(df.columns))
        
        # Tipo de gráfico
        with cols[1]:
            tipo_grafico = st.selectbox(
                "Tipo de gráfico:",
                ["Líneas", "Barras"],
                format_func=lambda x: "Líneas" if x == "Líneas" else "Barras"
            )
            
        # Crear y mostrar gráfico
        try:
            if tipo_grafico == "Líneas":
                fig = DataVisualizer.crear_grafico_lineas(
                    df, col_x, col_y,
                    color=None if col_color == 'Ninguno' else col_color,
                    titulo=f"Evolución de {col_y} por {col_x}"
                )
            else:
                fig = DataVisualizer.crear_grafico_barras(
                    df, col_x, col_y,
                    color=None if col_color == 'Ninguno' else col_color,
                    titulo=f"Comparativa de {col_y} por {col_x}"
                )
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error al crear el gráfico: {str(e)}")
        
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
