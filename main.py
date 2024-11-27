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
    st.title("📊 Explorador de Datos Demográficos INE")
    
    # Sidebar para selección
    with st.sidebar:
        try:
            # Obtener y mostrar operaciones demográficas
            operaciones = cargar_operaciones()
            
            if not operaciones:
                st.error("No se pudieron cargar las operaciones demográficas. Por favor, intente más tarde.")
                return
            
            # Categorizar operaciones
            categorias = {
                "Población": ["población", "padrón", "habitantes", "residentes"],
                "Nacimientos y Defunciones": ["nacimientos", "defunciones", "natalidad", "mortalidad"],
                "Matrimonios": ["matrimonios", "nupcialidad"],
                "Migraciones": ["migraciones", "migratoria", "extranjeros"]
            }
            
            categoria_seleccionada = st.selectbox(
                "Seleccione una categoría:",
                options=list(categorias.keys())
            )
            
            # Filtrar operaciones por categoría
            palabras_clave = categorias[categoria_seleccionada]
            operaciones_categoria = [
                op for op in operaciones
                if any(palabra in op.get('Nombre', '').lower() for palabra in palabras_clave)
            ]
            
            operacion_seleccionada = st.selectbox(
                "Seleccione una operación:",
                options=operaciones_categoria,
                format_func=format_nombre_operacion
            )
            
            if operacion_seleccionada:
                # Obtener y mostrar tablas
                try:
                    id_operacion = operacion_seleccionada.get('id')
                    if not id_operacion:
                        st.error("Error: ID de operación no disponible")
                        return
                        
                    tablas = INEApiClient.get_tablas_operacion(id_operacion)
                    
                    if not tablas:
                        st.warning("No se encontraron tablas para esta operación.")
                        return
                        
                    tabla_seleccionada = st.selectbox(
                        "Seleccione una tabla:",
                        options=tablas,
                        format_func=format_nombre_tabla
                    )
                    
                    # Opciones de descarga
                    modo_datos = st.radio(
                        "Tipo de datos:",
                        ["datos", "metadatos"],
                        format_func=lambda x: "Datos" if x == "datos" else "Metadatos"
                    )
                    
                    if st.button("Cargar datos"):
                        with st.spinner("Cargando datos..."):
                            id_tabla = tabla_seleccionada.get('id')
                            if not id_tabla:
                                st.error("Error: ID de tabla no disponible")
                                return
                                
                            datos = INEApiClient.get_datos_tabla(id_tabla, modo_datos)
                            if not datos:
                                st.error("No se pudieron obtener los datos.")
                                return
                                
                            st.session_state.datos_actuales = DataProcessor.json_to_dataframe(datos)
                            
                except Exception as e:
                    st.error(f"Error al cargar los datos: {str(e)}")
        except Exception as e:
            st.error(f"Error inesperado: {str(e)}")
    
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
