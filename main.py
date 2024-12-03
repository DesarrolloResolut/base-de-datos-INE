from datetime import datetime
from utils import exportar_a_excel, exportar_a_csv
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
    elif categoria_seleccionada == "censo_agrario":
        st.markdown("""
        Esta aplicación muestra los datos del Censo Agrario, proporcionados por el Instituto Nacional de Estadística (INE).
        Los datos incluyen:
        - Número de explotaciones por tamaño según superficie agrícola utilizada (SAU)
        - Datos por personalidad jurídica del titular
        - Análisis por provincia y comarca
        - Indicadores específicos del sector agrario
        """)
    
    elif categoria_seleccionada == "tasa_empleo":
        st.markdown("""
        Esta aplicación muestra las tasas de actividad, paro y empleo, proporcionadas por el Instituto Nacional de Estadística (INE).
        Los datos incluyen:
        - Tasas de actividad por género
        - Tasas de paro por género
        - Tasas de empleo por género
        - Evolución temporal de los indicadores
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
                    municipios = ['Total'] + [m for m in municipios if m != 'Total']  # Asegurar que Total está al principio
                    municipio_seleccionado = st.selectbox(
                        "Municipio:",
                        options=municipios,
                        index=0  # Total será el valor por defecto
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
                    # Filtro de provincia
                    provincias = sorted(df['Provincia'].unique().tolist())
                    provincia_seleccionada = st.selectbox(
                        "Provincia:",
                        options=provincias,
                        index=provincias.index('Albacete') if 'Albacete' in provincias else 0
                    )
                    
                    # Filtro de período
                    periodos = DataProcessor.obtener_periodos(df)
                    periodo_seleccionado = st.multiselect(
                        "Años:",
                        options=periodos,
                        default=periodos[-4:] if len(periodos) > 4 else periodos
                    )
                    
                    # Filtro de rangos
                    rangos_ordenados = [
                        'Total',
                        'Menos de 101 habitantes',
                        'De 101 a 500',
                        'De 501 a 1.000',
                        'De 1.001 a 2.000',
                        'De 2.001 a 5.000',
                        'De 5.001 a 10.000',
                        'De 10.001 a 20.000',
                        'De 20.001 a 50.000',
                        'De 50.001 a 100.000',
                        'De 100.001 a 500.000',
                        'Más de 500.000'
                    ]

                    rango_seleccionado = st.selectbox(
                        "Rangos de población:",
                        options=rangos_ordenados,
                        index=0  # Total será el valor por defecto
                    )
                elif categoria_seleccionada == "censo_agrario":
                    # Filtro de ámbito territorial
                    provincias = sorted(df['Provincia'].unique().tolist())
                    provincia_seleccionada = st.selectbox(
                        "Provincia:",
                        options=provincias
                    )
                    
                    # Filtro de tipo
                    tipos_disponibles = sorted(df['Tipo_Dato'].unique().tolist())
                    tipo_seleccionado = st.selectbox(
                        "Tipo:",
                        options=['Todos'] + tipos_disponibles,
                        index=0
                    )
                    
                    # Filtro de tipo de censo
                    tipos_censo = [
                        'Explotaciones por tamaño según SAU y personalidad jurídica',
                        'Distribución general de la superficie agrícola utilizada ecológica',
                        'Distribución por tipo de cultivo'
                    ]
                    tipo_censo_seleccionado = st.selectbox(
                        "Tipo de Censo:",
                        options=tipos_censo,
                        index=0
                    )
                    
                    # Procesamiento específico según tipo de censo
                    if tipo_censo_seleccionado == 'Distribución por tipo de cultivo':
                        # Procesamiento de datos por tipo de cultivo
                        df_cultivos = DataProcessor.procesar_datos_cultivos(df)
                        
                        if not df_cultivos.empty:
                            # Filtros específicos para cultivos
                            st.sidebar.subheader("Filtros de Cultivos")
                            
                            # Selector de tipo de cultivo
                            tipos_cultivo = ['Todos'] + sorted(df_cultivos['Tipo_Cultivo'].unique().tolist())
                            tipo_cultivo_seleccionado = st.sidebar.selectbox(
                                "Tipo de Cultivo:",
                                options=tipos_cultivo,
                                index=0
                            )
                            
                            # Filtro de comarca
                            comarcas = ['Todas'] + sorted(df_cultivos['Comarca'].unique().tolist())
                            comarca_seleccionada = st.sidebar.selectbox(
                                "Comarca:",
                                options=comarcas,
                                index=0
                            )
                            
                            # Aplicar filtros
                            df_filtrado = df_cultivos.copy()
                            if tipo_cultivo_seleccionado != 'Todos':
                                df_filtrado = df_filtrado[df_filtrado['Tipo_Cultivo'] == tipo_cultivo_seleccionado]
                            if comarca_seleccionada != 'Todas':
                                df_filtrado = df_filtrado[df_filtrado['Comarca'] == comarca_seleccionada]
                            
                            # Visualizaciones
                            st.subheader("Análisis por Tipo de Cultivo en Teruel")
                            
                            # Crear pestañas para diferentes visualizaciones
                            tab_superficie, tab_explotaciones, tab_comparativa = st.tabs([
                                "Superficie", "Explotaciones", "Análisis Comparativo"
                            ])
                            
                            with tab_superficie:
                                st.subheader("Análisis de Superficie")
                                
                                # Distribución de superficie por tipo de cultivo
                                fig_superficie = DataVisualizer.crear_grafico_barras(
                                    df_filtrado,
                                    x='Tipo_Cultivo',
                                    y='Superficie',
                                    color='Comarca' if comarca_seleccionada == 'Todas' else None,
                                    titulo="Distribución de Superficie por Tipo de Cultivo"
                                )
                                st.plotly_chart(fig_superficie, use_container_width=True)
                                
                                # Gráfico circular para ver la proporción de cada tipo de cultivo
                                fig_proporcion = DataVisualizer.crear_grafico_pastel(
                                    df_filtrado,
                                    names='Tipo_Cultivo',
                                    values='Superficie',
                                    titulo=f"Proporción de Superficie por Tipo de Cultivo {f'en {comarca_seleccionada}' if comarca_seleccionada != 'Todas' else 'por Comarca'}"
                                )
                                st.plotly_chart(fig_proporcion, use_container_width=True)
                                
                                # Métricas de superficie
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    total_superficie = df_filtrado['Superficie'].sum()
                                    st.metric("Superficie Total (ha)", f"{total_superficie:,.2f}")
                                with col2:
                                    media_superficie = df_filtrado['Superficie'].mean()
                                    st.metric("Superficie Media (ha)", f"{media_superficie:,.2f}")
                                with col3:
                                    max_superficie = df_filtrado['Superficie'].max()
                                    st.metric("Superficie Máxima (ha)", f"{max_superficie:,.2f}")
                            
                            with tab_explotaciones:
                                st.subheader("Análisis de Explotaciones")
                                
                                # Distribución del número de explotaciones
                                fig_explotaciones = DataVisualizer.crear_grafico_barras(
                                    df_filtrado,
                                    x='Tipo_Cultivo',
                                    y='Num_Explotaciones',
                                    color='Comarca' if comarca_seleccionada == 'Todas' else None,
                                    titulo="Número de Explotaciones por Tipo de Cultivo"
                                )
                                st.plotly_chart(fig_explotaciones, use_container_width=True)
                                
                                # Gráfico circular para ver la proporción de explotaciones
                                fig_proporcion_expl = DataVisualizer.crear_grafico_pastel(
                                    df_filtrado,
                                    names='Tipo_Cultivo',
                                    values='Num_Explotaciones',
                                    titulo=f"Proporción de Explotaciones por Tipo de Cultivo {f'en {comarca_seleccionada}' if comarca_seleccionada != 'Todas' else 'por Comarca'}"
                                )
                                st.plotly_chart(fig_proporcion_expl, use_container_width=True)
                                
                                # Métricas de explotaciones
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    total_expl = df_filtrado['Num_Explotaciones'].sum()
                                    st.metric("Total Explotaciones", f"{total_expl:,.0f}")
                                with col2:
                                    media_expl = df_filtrado['Num_Explotaciones'].mean()
                                    st.metric("Media Explotaciones", f"{media_expl:,.1f}")
                                with col3:
                                    max_expl = df_filtrado['Num_Explotaciones'].max()
                                    st.metric("Máximo Explotaciones", f"{max_expl:,.0f}")
                            
                            with tab_comparativa:
                                st.subheader("Análisis Comparativo")
                                
                                # Gráfico de dispersión Superficie vs Número de Explotaciones
                                fig_dispersion = DataVisualizer.crear_grafico_dispersion(
                                    df_filtrado,
                                    x='Superficie',
                                    y='Num_Explotaciones',
                                    text='Tipo_Cultivo',
                                    titulo="Relación entre Superficie y Número de Explotaciones"
                                )
                                st.plotly_chart(fig_dispersion, use_container_width=True)
                                
                                # Tabla de resumen
                                st.subheader("Resumen por Tipo de Cultivo")
                                df_resumen = df_filtrado.groupby('Tipo_Cultivo').agg({
                                    'Superficie': ['sum', 'mean'],
                                    'Num_Explotaciones': ['sum', 'mean']
                                }).round(2)
                                df_resumen.columns = ['Superficie Total', 'Superficie Media', 
                                                    'Total Explotaciones', 'Media Explotaciones']
                                st.dataframe(df_resumen)
                            
                            # Análisis de rendimiento
                            if 'Rendimiento' in df_filtrado.columns:
                                fig_rendimiento = DataVisualizer.crear_grafico_barras(
                                    df_filtrado,
                                    x='Tipo_Cultivo',
                                    y='Rendimiento',
                                    color='Comarca' if comarca_seleccionada == 'Todas' else None,
                                    titulo="Rendimiento por Tipo de Cultivo (Toneladas/ha)"
                                )
                                st.plotly_chart(fig_rendimiento, use_container_width=True)
                            
                            # Métricas clave
                            st.subheader("Métricas Clave")
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                total_superficie = df_filtrado['Superficie'].sum()
                                st.metric("Superficie Total (ha)", f"{total_superficie:,.2f}")
                            
                            with col2:
                                total_explotaciones = df_filtrado['Num_Explotaciones'].sum()
                                st.metric("Total Explotaciones", f"{total_explotaciones:,.0f}")
                            
                            with col3:
                                promedio_superficie = df_filtrado['Superficie'].mean()
                                st.metric("Superficie Media (ha)", f"{promedio_superficie:,.2f}")
                            
                            with col4:
                                if 'Rendimiento' in df_filtrado.columns:
                                    promedio_rendimiento = df_filtrado['Rendimiento'].mean()
                                    st.metric("Rendimiento Medio (Ton/ha)", f"{promedio_rendimiento:,.2f}")
                            
                            # Tabla de resumen
                            st.subheader("Resumen Detallado")
                            tabla_resumen = df_filtrado.groupby('Tipo_Cultivo').agg({
                                'Superficie': ['sum', 'mean'],
                                'Num_Explotaciones': ['sum', 'mean']
                            }).round(2)
                            tabla_resumen.columns = ['Superficie Total', 'Superficie Media', 
                                                   'Total Explotaciones', 'Media Explotaciones']
                            st.dataframe(tabla_resumen)
                    
                    elif tipo_censo_seleccionado == 'Distribución general de la superficie agrícola utilizada ecológica':
                        df_ecologico = DataProcessor.procesar_datos_ecologicos(df)
                        
                        # Crear pestañas para diferentes análisis
                        tab_general, tab_comparativo = st.tabs([
                            "Análisis General",
                            "Análisis Comparativo Superficie-Explotaciones"
                        ])
                        
                        with tab_general:
                            # Mostrar datos por tipo de explotación y cultivo
                            st.subheader("Análisis de Superficie Agrícola Ecológica")
                            
                        with tab_comparativo:
                            st.subheader("Análisis Comparativo de Superficie y Explotaciones")
                            
                            # Gráfico de dispersión comparativo
                            fig_comparativa = DataVisualizer.crear_grafico_dispersion(
                                df_ecologico,
                                x='Superficie (ha.)',
                                y='Nº explotaciones',
                                text='Tipo_Cultivo',
                                titulo="Relación entre Superficie y Número de Explotaciones"
                            )
                            st.plotly_chart(fig_comparativa, use_container_width=True)
                            
                            # Gráficos de barras comparativos
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                df_sup = df_ecologico[df_ecologico['Metrica'] == 'Superficie (ha.)']
                                fig_sup = DataVisualizer.crear_grafico_barras(
                                    df_sup,
                                    x='Tipo_Explotacion',
                                    y='Valor',
                                    color='Tipo_Cultivo',
                                    titulo="Superficie por Tipo de Explotación"
                                )
                                st.plotly_chart(fig_sup, use_container_width=True)
                            
                            with col2:
                                df_expl = df_ecologico[df_ecologico['Metrica'] == 'Nº explotaciones']
                                fig_expl = DataVisualizer.crear_grafico_barras(
                                    df_expl,
                                    x='Tipo_Explotacion',
                                    y='Valor',
                                    color='Tipo_Cultivo',
                                    titulo="Número de Explotaciones por Tipo"
                                )
                                st.plotly_chart(fig_expl, use_container_width=True)
                            
                            # Tabla comparativa
                            st.subheader("Resumen Comparativo")
                            df_resumen = df_ecologico.pivot_table(
                                index=['Tipo_Explotacion', 'Tipo_Cultivo'],
                                columns='Metrica',
                                values='Valor',
                                aggfunc='sum'
                            ).round(2)
                            st.dataframe(df_resumen)
                        
                        # Selección de tipo de explotación
                        tipos_explotacion = ['Todas las explotaciones'] + sorted(
                            [t for t in df_ecologico['Tipo_Explotacion'].unique() 
                             if t != 'Todas las explotaciones']
                        )
                        tipo_explotacion = st.selectbox(
                            "Tipo de Explotación:",
                            options=tipos_explotacion
                        )
                        
                        # Filtrar por tipo de explotación
                        df_filtrado = df_ecologico[
                            df_ecologico['Tipo_Explotacion'] == tipo_explotacion
                        ]
                        
                        # Mostrar datos en pestañas
                        tab_expl, tab_sup, tab_tam = st.tabs([
                            "Número de Explotaciones",
                            "Superficie",
                            "Tamaño Medio"
                        ])
                        
                        with tab_expl:
                            df_expl = df_filtrado[
                                df_filtrado['Metrica'] == 'Nº explotaciones'
                            ]
                            if not df_expl.empty:
                                fig_expl = DataVisualizer.crear_grafico_barras(
                                    df_expl,
                                    x='Tipo_Cultivo',
                                    y='Valor',
                                    titulo=f"Número de Explotaciones por Tipo de Cultivo - {tipo_explotacion}"
                                )
                                st.plotly_chart(fig_expl, use_container_width=True)
                            
                        with tab_sup:
                            df_sup = df_filtrado[
                                df_filtrado['Metrica'] == 'Superficie (ha.)'
                            ]
                            if not df_sup.empty:
                                fig_sup = DataVisualizer.crear_grafico_barras(
                                    df_sup,
                                    x='Tipo_Cultivo',
                                    y='Valor',
                                    titulo=f"Superficie (ha.) por Tipo de Cultivo - {tipo_explotacion}"
                                )
                                st.plotly_chart(fig_sup, use_container_width=True)
                                
                                # Gráfico circular para distribución
                                fig_pie = DataVisualizer.crear_grafico_pastel(
                                    df_sup,
                                    names='Tipo_Cultivo',
                                    values='Valor',
                                    titulo=f"Distribución de Superficie por Tipo de Cultivo - {tipo_explotacion}"
                                )
                                st.plotly_chart(fig_pie, use_container_width=True)
                            
                        with tab_tam:
                            df_tam = df_filtrado[
                                df_filtrado['Metrica'] == 'Tamaño medio'
                            ]
                            if not df_tam.empty:
                                fig_tam = DataVisualizer.crear_grafico_barras(
                                    df_tam,
                                    x='Tipo_Cultivo',
                                    y='Valor',
                                    titulo=f"Tamaño Medio por Tipo de Cultivo - {tipo_explotacion}"
                                )
                                st.plotly_chart(fig_tam, use_container_width=True)
                    
                    # Filtro de personalidad jurídica
                    personalidades = sorted(df['Personalidad_Juridica'].unique().tolist())
                    personalidad_seleccionada = st.multiselect(
                        "Personalidad Jurídica:",
                        options=personalidades,
                        default=personalidades
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
                    'Provincia': provincia_seleccionada,
                    'Periodo': periodo_seleccionado,
                    'Rango': [rango_seleccionado] if rango_seleccionado != 'Total' else df['Rango'].unique().tolist()
                }
            elif categoria_seleccionada == "censo_agrario":
                filtros = {
                    'Provincia': provincia_seleccionada,
                    'Tipo_Dato': tipo_seleccionado if 'tipo_seleccionado' in locals() and tipo_seleccionado != 'Todos' else None,
                    'Personalidad_Juridica': personalidad_seleccionada
                }
            
            elif categoria_seleccionada == "tasa_empleo":
                # Filtros específicos para tasas de empleo
                with st.sidebar:
                    # Filtro de indicador
                    indicadores = ['Tasa de actividad', 'Tasa de paro', 'Tasa de empleo']
                    indicador_seleccionado = st.selectbox(
                        "Indicador:",
                        options=indicadores
                    )
                    
                    # Filtro de género
                    generos = ['Todos', 'Hombres', 'Mujeres']
                    genero_seleccionado = st.selectbox(
                        "Género:",
                        options=generos
                    )
                    
                    # Filtro de periodo
                    periodos = sorted(df['Periodo'].unique().tolist(), reverse=True)
                    periodo_seleccionado = st.multiselect(
                        "Períodos:",
                        options=periodos,
                        default=periodos[:4]  # Últimos 4 trimestres por defecto
                    )
                
                filtros = {
                    'Indicador': indicador_seleccionado,
                    'Genero': genero_seleccionado,
                    'Periodo': periodo_seleccionado
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
        
        # Sección de exportación
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Exportar a Excel", key="btn_excel_1"):
                # Generar nombre de archivo con timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"datos_ine_{timestamp}.xlsx"
                resultado = exportar_a_excel(df, filename)
                if "exitosamente" in resultado:
                    with open(filename, 'rb') as f:
                        st.download_button(
                            label="Descargar Excel",
                            data=f,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="download_excel_1"
                        )
                else:
                    st.error(resultado)
        
        with col2:
            if st.button("Exportar a CSV", key="btn_csv_1"):
                # Generar nombre de archivo con timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"datos_ine_{timestamp}.csv"
                resultado = exportar_a_csv(df, filename)
                if "exitosamente" in resultado:
                    with open(filename, 'rb') as f:
                        st.download_button(
                            label="Descargar CSV",
                            data=f,
                            file_name=filename,
                            mime="text/csv",
                            key="download_csv_1"
                        )
                else:
                    st.error(resultado)
        
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
                
            # Removed censo_cultivo section as requested

            elif categoria_seleccionada == "tasa_empleo":
                # Visualizaciones para tasas de empleo
                st.subheader("Análisis de Tasas de Empleo")
                
                # Mostrar tablas para cada tipo de tasa
                for indicador in ['Tasa de actividad', 'Tasa de paro', 'Tasa de empleo']:
                    st.subheader(f"{indicador}")
                    df_indicador = df[df['Indicador'] == indicador]
                    
                    # Formatear los valores con 2 decimales
                    df_indicador = df_indicador.copy()
                    df_indicador['Valor'] = df_indicador['Valor'].round(2)
                    
                    # Mostrar tabla con las columnas especificadas
                    st.dataframe(
                        df_indicador[['Periodo', 'Genero', 'Valor']],
                        use_container_width=True
                    )
                
                # Crear pestañas para diferentes análisis
                tab_evolucion, tab_comparativa, tab_genero = st.tabs([
                    "Evolución Temporal",
                    "Comparativa de Tasas",
                    "Análisis por Género"
                ])
                
                with tab_evolucion:
                    # Gráfico de evolución temporal
                    fig_evolucion = DataVisualizer.crear_grafico_lineas(
                        df,
                        x='Periodo',
                        y='Valor',
                        color='Indicador',
                        titulo=f"Evolución temporal de {indicador_seleccionado}"
                    )
                    st.plotly_chart(fig_evolucion, use_container_width=True)
                    
                    # Métricas de evolución
                    st.subheader("Métricas de Evolución")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        ultimo_valor = df[df['Periodo'] == df['Periodo'].max()]['Valor'].iloc[0]
                        st.metric("Último valor", f"{ultimo_valor:.2f}%")
                    with col2:
                        valor_medio = df['Valor'].mean()
                        st.metric("Media del período", f"{valor_medio:.2f}%")
                    with col3:
                        variacion = ultimo_valor - df[df['Periodo'] == df['Periodo'].min()]['Valor'].iloc[0]
                        st.metric("Variación en el período", f"{variacion:+.2f}%")
                
                with tab_comparativa:
                    # Gráfico comparativo de tasas
                    fig_comparativa = DataVisualizer.crear_grafico_barras(
                        df[df['Periodo'] == df['Periodo'].max()],
                        x='Indicador',
                        y='Valor',
                        color='Genero',
                        titulo="Comparativa de Tasas por Género"
                    )
                    st.plotly_chart(fig_comparativa, use_container_width=True)
                    
                    # Tabla comparativa
                    st.subheader("Resumen Comparativo")
                    df_resumen = df.pivot_table(
                        index=['Indicador', 'Genero'],
                        values='Valor',
                        aggfunc=['mean', 'min', 'max']
                    ).round(2)
                    df_resumen.columns = ['Media', 'Mínimo', 'Máximo']
                    st.dataframe(df_resumen)
                
                with tab_genero:
                    # Gráfico de dispersión por género
                    fig_genero = DataVisualizer.crear_grafico_barras(
                        df,
                        x='Periodo',
                        y='Valor',
                        color='Genero',
                        titulo=f"Distribución por Género - {indicador_seleccionado}"
                    )
                    st.plotly_chart(fig_genero, use_container_width=True)
                    
                    # Análisis de brecha de género
                    st.subheader("Análisis de Brecha de Género")
                    df_ultimo_periodo = df[df['Periodo'] == df['Periodo'].max()]
                    hombres = df_ultimo_periodo[df_ultimo_periodo['Genero'] == 'Hombres']['Valor'].iloc[0]
                    mujeres = df_ultimo_periodo[df_ultimo_periodo['Genero'] == 'Mujeres']['Valor'].iloc[0]
                    brecha = hombres - mujeres
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Tasa Hombres", f"{hombres:.2f}%")
                    with col2:
                        st.metric("Tasa Mujeres", f"{mujeres:.2f}%")
                    with col3:
                        st.metric("Brecha de Género", f"{brecha:+.2f}%")
                
                # Crear pestañas para diferentes visualizaciones
                tab_evolucion, tab_genero, tab_comparativa = st.tabs([
                    "Evolución Temporal", "Análisis por Género", "Comparativa"
                ])
                
                with tab_evolucion:
                    st.subheader("Evolución Temporal de Tasas")
                    # Gráfico de evolución temporal
                    fig_evolucion = DataVisualizer.crear_grafico_lineas(
                        df,
                        x='Periodo',
                        y='Valor',
                        color='Indicador',
                        titulo=f"Evolución de {indicador_seleccionado}"
                    )
                    st.plotly_chart(fig_evolucion, use_container_width=True)
                    
                    # Métricas clave
                    col1, col2, col3 = st.columns(3)
                    ultimo_periodo = max(df['Periodo'])
                    df_ultimo = df[df['Periodo'] == ultimo_periodo]
                    
                    with col1:
                        valor_actual = df_ultimo['Valor'].mean()
                        st.metric("Valor Actual", f"{valor_actual:.2f}%")
                    with col2:
                        valor_min = df['Valor'].min()
                        st.metric("Mínimo", f"{valor_min:.2f}%")
                    with col3:
                        valor_max = df['Valor'].max()
                        st.metric("Máximo", f"{valor_max:.2f}%")
                
                with tab_genero:
                    st.subheader("Análisis por Género")
                    # Gráfico de barras por género
                    df_ultimo_periodo = df[df['Periodo'] == df['Periodo'].max()]
                    fig_genero = DataVisualizer.crear_grafico_barras(
                        df_ultimo_periodo,
                        x='Genero',
                        y='Valor',
                        color='Indicador',
                        titulo=f"Comparativa por Género ({df['Periodo'].max()})"
                    )
                    st.plotly_chart(fig_genero, use_container_width=True)
                
                with tab_comparativa:
                    st.subheader("Análisis Comparativo")
                    # Gráfico de dispersión para ver relaciones
                    fig_comparativa = DataVisualizer.crear_grafico_barras(
                        df,
                        x='Periodo',
                        y='Valor',
                        color='Genero',
                        titulo=f"Comparativa de {indicador_seleccionado} por Género y Periodo"
                    )
                    st.plotly_chart(fig_comparativa, use_container_width=True)
                    
                    # Tabla resumen
                    st.subheader("Resumen Estadístico")
                    df_resumen = df.groupby(['Indicador', 'Genero'])['Valor'].agg([
                        ('Media', 'mean'),
                        ('Mínimo', 'min'),
                        ('Máximo', 'max')
                    ]).round(2)
                    st.dataframe(df_resumen)

            elif categoria_seleccionada == "censo_agrario":
                try:
                    # Visualizaciones específicas para censo agrario
                    st.subheader("Análisis del Censo Agrario")
                    
                    if df.empty:
                        st.warning("No hay datos disponibles para mostrar.")
                        return

                    # Tabs para diferentes tipos de visualizaciones
                    tab_explotaciones, tab_sau, tab_pet, tab_comparativa = st.tabs([
                        "Explotaciones", "Superficie Agrícola", "Producción Económica", "Análisis Comparativo"
                    ])

                    with tab_explotaciones:
                        st.subheader("Análisis de Explotaciones")
                        # Filtrar datos por tipo
                        df_explotaciones = df[df['Tipo_Dato'] == 'Número de explotaciones'].copy()
                        if not df_explotaciones.empty:
                            # Distribución por personalidad jurídica
                            fig_distribucion = DataVisualizer.crear_grafico_barras(
                                df_explotaciones,
                                x='Personalidad_Juridica',
                                y='Valor',
                                titulo="Distribución de Explotaciones por Personalidad Jurídica"
                            )
                            st.plotly_chart(fig_distribucion, use_container_width=True)

                            # Distribución por comarca
                            fig_comarca = DataVisualizer.crear_grafico_barras(
                                df_explotaciones,
                                x='Comarca',
                                y='Valor',
                                color='Personalidad_Juridica',
                                titulo="Distribución de Explotaciones por Comarca"
                            )
                            st.plotly_chart(fig_comarca, use_container_width=True)

                    with tab_sau:
                        st.subheader("Análisis de Superficie Agrícola Utilizada (SAU)")
                        df_sau = df[df['Tipo_Dato'] == 'SAU (ha.)'].copy()
                        if not df_sau.empty:
                            # Gráfico de SAU por comarca
                            fig_sau_comarca = DataVisualizer.crear_grafico_barras(
                                df_sau,
                                x='Comarca',
                                y='Valor',
                                color='Personalidad_Juridica',
                                titulo="Superficie Agrícola por Comarca"
                            )
                            st.plotly_chart(fig_sau_comarca, use_container_width=True)

                            # Gráfico circular de distribución de SAU
                            fig_sau_pie = DataVisualizer.crear_grafico_pastel(
                                df_sau,
                                names='Personalidad_Juridica',
                                values='Valor',
                                titulo="Distribución de SAU por Personalidad Jurídica"
                            )
                            st.plotly_chart(fig_sau_pie, use_container_width=True)

                    with tab_pet:
                        st.subheader("Análisis de Producción Estándar Total (PET)")
                        df_pet = df[df['Tipo_Dato'] == 'PET (miles €)'].copy()
                        if not df_pet.empty:
                            # Gráfico de PET por comarca
                            fig_pet_comarca = DataVisualizer.crear_grafico_barras(
                                df_pet,
                                x='Comarca',
                                y='Valor',
                                color='Personalidad_Juridica',
                                titulo="Producción Estándar Total por Comarca"
                            )
                            st.plotly_chart(fig_pet_comarca, use_container_width=True)

                            # Gráfico de dispersión PET vs SAU
                            if not df_sau.empty:
                                df_merged = pd.merge(
                                    df_pet.groupby('Comarca')['Valor'].sum().reset_index(),
                                    df_sau.groupby('Comarca')['Valor'].sum().reset_index(),
                                    on='Comarca', suffixes=('_PET', '_SAU')
                                )
                                fig_correlacion = DataVisualizer.crear_grafico_dispersion(
                                    df_merged,
                                    x='Valor_SAU',
                                    y='Valor_PET',
                                    text='Comarca',
                                    titulo="Correlación entre SAU y PET por Comarca"
                                )
                                st.plotly_chart(fig_correlacion, use_container_width=True)

                    with tab_comparativa:
                        st.subheader("Análisis Estadístico Avanzado")
                        
                        # Análisis de concentración (Índice de Gini)
                        st.write("### Análisis de Concentración")
                        df_explotaciones = df[df['Tipo_Dato'] == 'Número de explotaciones']
                        if not df_explotaciones.empty:
                            gini = DataProcessor.calcular_indice_gini(df_explotaciones)
                            st.metric(
                                "Índice de Gini",
                                f"{gini:.4f}",
                                help="Mide la concentración de explotaciones (0=distribución equitativa, 1=máxima concentración)"
                            )
                        
                        # Índices de especialización
                        st.write("### Índices de Especialización Agraria")
                        indices_esp = DataProcessor.calcular_indice_especializacion(df)
                        if not indices_esp.empty:
                            st.dataframe(
                                indices_esp.pivot(
                                    index='Territorio',
                                    columns='Tipo',
                                    values='Indice_Especializacion'
                                ).round(2)
                            )
                        
                        # Análisis de eficiencia
                        st.write("### Análisis de Eficiencia Agraria")
                        eficiencia = DataProcessor.analizar_eficiencia_agraria(df)
                        if not eficiencia.empty:
                            # Mostrar métricas de eficiencia
                            st.dataframe(eficiencia.sort_values('Eficiencia_PET_por_ha', ascending=False))
                            
                            # Gráfico de eficiencia
                            fig_eficiencia = DataVisualizer.crear_grafico_barras(
                                eficiencia,
                                x='Comarca',
                                y='Eficiencia_PET_por_ha',
                                titulo='Eficiencia (PET por hectárea) por Comarca'
                            )
                            st.plotly_chart(fig_eficiencia, use_container_width=True)
                        
                        # Análisis de distribución por tamaño
                        st.write("### Distribución por Tamaño")
                        dist_tamano = DataProcessor.analizar_distribucion_tamano(df)
                        if dist_tamano:
                            # Mostrar distribución por personalidad jurídica
                            st.write("#### Distribución por Personalidad Jurídica")
                            dist_juridica = pd.DataFrame(dist_tamano['distribucion_juridica']).round(2)
                            st.dataframe(dist_juridica)
                            
                            # Mostrar distribución territorial
                            st.write("#### Distribución Territorial")
                            dist_terr = pd.DataFrame(dist_tamano['distribucion_territorial']).round(2)
                            st.dataframe(dist_terr)
                        
                        # Resumen estadístico por tipo de dato
                        st.write("### Resumen Estadístico por Tipo de Dato")
                        for tipo_dato in df['Tipo_Dato'].unique():
                            df_tipo = df[df['Tipo_Dato'] == tipo_dato]
                            stats = DataProcessor.calcular_estadisticas(df_tipo, 'Valor')
                            
                            st.write(f"#### {tipo_dato}")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Media", f"{stats['media']:,.2f}")
                            with col2:
                                st.metric("Mediana", f"{stats['mediana']:,.2f}")
                            with col3:
                                st.metric("Desv. Estándar", f"{stats['desv_std']:,.2f}")

                        # Gráfico comparativo de todos los indicadores
                        fig_comparativa = DataVisualizer.crear_grafico_barras(
                            df,
                            x='Tipo_Dato',
                            y='Valor',
                            color='Comarca',
                            titulo="Comparativa General por Tipo de Dato y Comarca"
                        )
                        st.plotly_chart(fig_comparativa, use_container_width=True)
                    
                    # Métricas clave
                    st.subheader("Métricas Clave")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        total_explotaciones = df_explotaciones['Valor'].sum() if not df_explotaciones.empty else 0
                        st.metric("Total Explotaciones", f"{total_explotaciones:,.0f}")
                    
                    with col2:
                        df_sau = df[df['Tipo_Dato'] == 'SAU (ha.)']
                        promedio_sau = df_sau['Valor'].mean() if not df_sau.empty else 0
                        st.metric("Promedio SAU (ha.)", f"{promedio_sau:,.2f}")
                    
                    with col3:
                        df_pet = df[df['Tipo_Dato'] == 'PET (miles €)']
                        if not df_pet.empty:
                            promedio_pet = df_pet['Valor'].mean()
                            st.metric("Promedio PET (miles €)", f"{promedio_pet:,.2f}")
                    
                    # Análisis por tipo de dato
                    st.subheader("Análisis por Tipo de Dato")
                    tipo_dato_seleccionado = st.selectbox(
                        "Seleccione el tipo de dato a analizar:",
                        options=df['Tipo_Dato'].unique()
                    )
                    
                    df_tipo = df[df['Tipo_Dato'] == tipo_dato_seleccionado]
                    if not df_tipo.empty:
                        fig_tipo = DataVisualizer.crear_grafico_barras(
                            df_tipo,
                            x='Personalidad_Juridica',
                            y='Valor',
                            color='Comarca',
                            titulo=f"Distribución de {tipo_dato_seleccionado}"
                        )
                        st.plotly_chart(fig_tipo, use_container_width=True)

                except Exception as e:
                    st.error(f"Error al crear los gráficos para censo agrario: {str(e)}")
            
            elif categoria_seleccionada == "provincias":
                # Gráfico de evolución temporal por municipio
                st.subheader("Evolución temporal")
                fig_evolucion = DataVisualizer.crear_grafico_lineas(
                    df,
                    x='Periodo',
                    y='Valor',
                    color='Genero',
                    titulo=f"Evolución temporal - {municipio_seleccionado}"
                )
                st.plotly_chart(fig_evolucion, use_container_width=True)
                
                # Gráfico comparativo por género y municipio
                st.subheader("Comparativa por género")
                df_actual = df[df['Periodo'] == df['Periodo'].max()]
                fig_comparativa = DataVisualizer.crear_grafico_barras(
                    df_actual,
                    x='Genero',
                    y='Valor',
                    titulo=f"Distribución por Género - {municipio_seleccionado} ({df['Periodo'].max()})"
                )
                st.plotly_chart(fig_comparativa, use_container_width=True)
                
                # Comparativa entre municipios si hay más de uno seleccionado
                if len(municipios) > 1:
                    st.subheader("Comparativa entre municipios")
                    df_municipios = df[df['Genero'] == 'Total']
                    fig_municipios = DataVisualizer.crear_grafico_lineas(
                        df_municipios,
                        x='Periodo',
                        y='Valor',
                        color='Municipio',
                        titulo="Comparativa de población entre municipios"
                    )
                    st.plotly_chart(fig_municipios, use_container_width=True)
            
            elif categoria_seleccionada == "tasa_empleo":
                # Visualizaciones para tasas de empleo
                st.subheader("Evolución Temporal de Tasas")
                
                # Gráfico de evolución temporal
                fig_evolucion = DataVisualizer.crear_grafico_lineas(
                    df,
                    x='Periodo',
                    y='Valor',
                    color='Genero',
                    titulo=f"Evolución de {indicador_seleccionado}"
                )
                st.plotly_chart(fig_evolucion, use_container_width=True)
                
                # Comparativa por género
                if genero_seleccionado == 'Todos':
                    st.subheader("Comparativa por Género")
                    fig_genero = DataVisualizer.crear_grafico_barras(
                        df[df['Periodo'] == df['Periodo'].max()],
                        x='Genero',
                        y='Valor',
                        titulo=f"{indicador_seleccionado} por Género ({df['Periodo'].max()})"
                    )
                    st.plotly_chart(fig_genero, use_container_width=True)
                
                # Métricas clave
                st.subheader("Métricas Clave")
                ultimo_periodo = df['Periodo'].max()
                df_actual = df[df['Periodo'] == ultimo_periodo]
                
                col1, col2 = st.columns(2)
                with col1:
                    valor_hombres = df_actual[df_actual['Genero'] == 'Hombres']['Valor'].iloc[0]
                    st.metric("Hombres", f"{valor_hombres:.2f}%")
                with col2:
                    valor_mujeres = df_actual[df_actual['Genero'] == 'Mujeres']['Valor'].iloc[0]
                    st.metric("Mujeres", f"{valor_mujeres:.2f}%")
                    
                    fig_municipios = DataVisualizer.crear_grafico_lineas(
                        df_actual,
                        x='Periodo',
                        y='Valor',
                        titulo="Comparativa de población entre municipios"
                    )
                    st.plotly_chart(fig_municipios, use_container_width=True)
                    
            elif categoria_seleccionada == "tasa_empleo":
                # Visualización de tasas de actividad, paro y empleo
                st.subheader("Tasas de Actividad, Paro y Empleo")
                
                # Procesar datos de empleo
                df_empleo = DataProcessor.procesar_datos(df, "tasa_empleo")
                
                # Filtros
                col1, col2, col3 = st.columns(3)
                with col1:
                    tipo_tasa = st.selectbox(
                        "Tipo de tasa",
                        options=sorted(df_empleo['Indicador'].unique()),
                        key="tasa_tipo"
                    )
                with col2:
                    genero = st.selectbox(
                        "Género",
                        options=sorted(df_empleo['Genero'].unique()),
                        key="tasa_genero"
                    )
                with col3:
                    periodo = st.selectbox(
                        "Período",
                        options=sorted(df_empleo['Periodo'].unique(), reverse=True),
                        key="tasa_periodo"
                    )
                
                # Filtrar datos según selección
                df_filtrado = df_empleo[
                    (df_empleo['Indicador'] == tipo_tasa) &
                    (df_empleo['Genero'] == genero)
                ]
                
                # Mostrar valor actual
                valor_actual = df_filtrado[df_filtrado['Periodo'] == periodo]['Valor'].iloc[0]
                st.metric(
                    f"Tasa de {tipo_tasa} - {genero}",
                    f"{valor_actual:.2f}%",
                    help=f"Valor para el período {periodo}"
                )
                
                # Gráfico de evolución temporal por género
                st.subheader("Evolución Temporal por Género")
                df_evolucion = df_empleo[df_empleo['Indicador'] == tipo_tasa]
                fig_evolucion = DataVisualizer.crear_grafico_lineas(
                    df_evolucion,
                    x='Periodo',
                    y='Valor',
                    color='Genero',
                    titulo=f"Evolución de la Tasa de {tipo_tasa} por Género"
                )
                st.plotly_chart(fig_evolucion, use_container_width=True)
                
                # Gráfico comparativo entre tasas
                st.subheader("Comparativa entre Tasas")
                df_comparativa = df_empleo[
                    (df_empleo['Periodo'] == periodo) &
                    (df_empleo['Genero'] == genero)
                ]
                fig_comparativa = DataVisualizer.crear_grafico_barras(
                    df_comparativa,
                    x='Indicador',
                    y='Valor',
                    titulo=f"Comparativa de Tasas - {genero} ({periodo})"
                )
                st.plotly_chart(fig_comparativa, use_container_width=True)
                
                # Gráfico específico por indicador
                st.subheader(f"Análisis Detallado - {tipo_tasa}")
                df_detalle = df_empleo[
                    (df_empleo['Indicador'] == tipo_tasa) &
                    (df_empleo['Periodo'] == periodo)
                ]
                fig_detalle = DataVisualizer.crear_grafico_barras(
                    df_detalle,
                    x='Genero',
                    y='Valor',
                    titulo=f"Tasa de {tipo_tasa} por Género ({periodo})"
                )
                st.plotly_chart(fig_detalle, use_container_width=True)
                
            elif categoria_seleccionada == "municipios_habitantes":
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
                st.subheader("Estadísticas Básicas")
                if categoria_seleccionada == "provincias":
                    ultimo_periodo = df['Periodo'].max()
                    datos_recientes = df[df['Periodo'] == ultimo_periodo]
                    
                    total = datos_recientes[datos_recientes['Genero'] == 'Total']['Valor'].iloc[0]
                    hombres = datos_recientes[datos_recientes['Genero'] == 'HOMBRE']['Valor'].iloc[0]
                    mujeres = datos_recientes[datos_recientes['Genero'] == 'MUJER']['Valor'].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total población", f"{total:,.0f}")
                        st.metric("Hombres", f"{hombres:,.0f}")
                    with col2:
                        st.metric("Mujeres", f"{mujeres:,.0f}")
                        st.metric("% Hombres", f"{(hombres/total)*100:.1f}%")
                        st.metric("% Mujeres", f"{(mujeres/total)*100:.1f}%")
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
        
        # Exportar datos
        st.header("Exportar Datos")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Exportar a Excel", key="btn_excel_2"):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"datos_{categoria_seleccionada}_{timestamp}.xlsx"
                    mensaje = exportar_a_excel(df, filename)
                    st.success(f"{mensaje}: {filename}")
                except Exception as e:
                    st.error(f"Error al exportar a Excel: {str(e)}")
        
        with col2:
            if st.button("Exportar a CSV", key="btn_csv_2"):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"datos_{categoria_seleccionada}_{timestamp}.csv"
                    mensaje = exportar_a_csv(df, filename)
                    st.success(f"{mensaje}: {filename}")
                except Exception as e:
                    st.error(f"Error al exportar a CSV: {str(e)}")
        
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
                            
        elif categoria_seleccionada == "provincias":
            if tipo_analisis == "Tendencias y Proyecciones":
                st.subheader("Análisis de Tendencias Demográficas")
                
                # Análisis por género
                for genero in ['Total', 'HOMBRE', 'MUJER']:
                    df_genero = df[df['Genero'] == genero]
                    if not df_genero.empty:
                        st.write(f"### {genero}")
                        
                        try:
                            resultados_series = DataProcessor.analisis_series_temporales(
                                df_genero, 'Periodo', 'Valor'
                            )
                            
                            if resultados_series:
                                # Mostrar métricas de tendencia
                                col1, col2 = st.columns(2)
                                with col1:
                                    tendencia = resultados_series['tendencia']['coeficiente']
                                    direccion = "Crecimiento" if tendencia > 0 else "Decrecimiento"
                                    st.metric(
                                        "Tendencia", 
                                        f"{direccion}",
                                        f"{abs(tendencia):.0f} personas/año"
                                    )
                                    st.metric(
                                        "Significancia estadística", 
                                        "Significativo" if resultados_series['tendencia']['p_valor'] < 0.05 else "No significativo",
                                        f"p={resultados_series['tendencia']['p_valor']:.4f}"
                                    )
                                
                                with col2:
                                    st.metric(
                                        "Tasa de cambio anual media", 
                                        f"{resultados_series['tasas_cambio']['media']*100:.2f}%"
                                    )
                                    st.metric(
                                        "Volatilidad", 
                                        f"{resultados_series['tasas_cambio']['desv_std']*100:.2f}%"
                                    )
                                
                                # Gráfico de tendencia
                                serie_temporal = pd.Series(
                                    df_genero['Valor'].values,
                                    index=df_genero['Periodo']
                                )
                                
                                fig_tendencia = DataVisualizer.crear_grafico_series_temporales(
                                    resultados_series,
                                    serie_temporal,
                                    titulo=f"Análisis de Tendencia - {genero}"
                                )
                                st.plotly_chart(fig_tendencia, use_container_width=True)
                                
                        except Exception as e:
                            st.warning(f"No se pudo realizar el análisis de tendencias para {genero}: {str(e)}")
                            
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
                if categoria_seleccionada == "provincias":
                    df_crecimiento = DataProcessor.calcular_crecimiento_poblacional(df)
                    if not df_crecimiento.empty:
                        st.subheader("Análisis de Crecimiento Poblacional")
                        
                        # Mostrar métricas de crecimiento
                        df_ultimo_periodo = df_crecimiento[df_crecimiento['Periodo'] == df_crecimiento['Periodo'].max()]
                        crecimiento_actual = df_ultimo_periodo['Crecimiento'].iloc[0]
                        
                        # Métricas de crecimiento
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(
                                "Crecimiento último año",
                                f"{crecimiento_actual:+.2f}%",
                                help="Porcentaje de cambio respecto al año anterior"
                            )
                            st.metric(
                                "Crecimiento promedio",
                                f"{df_crecimiento['Crecimiento'].mean():+.2f}%",
                                help="Media del crecimiento anual"
                            )
                        with col2:
                            st.metric(
                                "Crecimiento máximo",
                                f"{df_crecimiento['Crecimiento'].max():+.2f}%",
                                help="Mayor crecimiento anual registrado"
                            )
                            st.metric(
                                "Crecimiento mínimo",
                                f"{df_crecimiento['Crecimiento'].min():+.2f}%",
                                help="Menor crecimiento anual registrado"
                            )
                        
                        # Gráfico de crecimiento
                        fig_crecimiento = DataVisualizer.crear_grafico_lineas(
                            df_crecimiento,
                            x='Periodo',
                            y='Crecimiento',
                            titulo="Tasa de Crecimiento Poblacional Anual (%)"
                        )
                        st.plotly_chart(fig_crecimiento, use_container_width=True)
                        
                        # Tabla de crecimiento
                        st.subheader("Tasas de Crecimiento por Año")
                        df_tabla = df_crecimiento[['Periodo', 'Valor', 'Crecimiento']].copy()
                        df_tabla.columns = ['Año', 'Población', 'Crecimiento (%)']
                        st.dataframe(df_tabla.sort_values('Año', ascending=False))
                else:
                    st.info("El análisis de crecimiento no está disponible para esta categoría")

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