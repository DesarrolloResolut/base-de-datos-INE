import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List

class DataVisualizer:
    """Visualización de datos del INE"""
    
    @staticmethod
    def crear_grafico_lineas(df: pd.DataFrame, 
                         x: str, 
                         y: str, 
                         color: str = None,
                         titulo: str = "Evolución Temporal") -> go.Figure:
        """Crea gráfico de líneas temporal"""
        fig = px.line(df, x=x, y=y, color=color,
                     title=titulo,
                     labels={x: x.replace('_', ' ').title(), 
                            y: y.replace('_', ' ').title()})
        fig.update_layout(
            template='plotly_white',
            hovermode='x unified',
            legend_title_text=color.replace('_', ' ').title() if color else None,
            xaxis_title=x.replace('_', ' ').title(),
            yaxis_title=y.replace('_', ' ').title()
        )
        return fig
    
    @staticmethod
    def crear_grafico_barras(df: pd.DataFrame,
                         x: str,
                         y: str,
                         color: str = None,
                         titulo: str = "Comparativa") -> go.Figure:
        """Crea gráfico de barras"""
        fig = px.bar(df, x=x, y=y, color=color,
                    title=titulo,
                    labels={x: x.replace('_', ' ').title(), 
                           y: y.replace('_', ' ').title()})
        fig.update_layout(
            template='plotly_white',
            barmode='group' if color else 'relative',
            legend_title_text=color.replace('_', ' ').title() if color else None,
            xaxis_title=x.replace('_', ' ').title(),
            yaxis_title=y.replace('_', ' ').title()
        )
        return fig
    
    @staticmethod
    def crear_grafico_tendencia(df: pd.DataFrame,
                            x: str,
                            y: str,
                            titulo: str = "Análisis de Tendencia") -> go.Figure:
        """Crea gráfico de tendencia con línea de regresión"""
        fig = px.scatter(df, x=x, y=y,
                        title=titulo,
                        trendline="ols",
                        labels={x: x.replace('_', ' ').title(),
                               y: y.replace('_', ' ').title()})
        
        fig.update_layout(
            template='plotly_white',
            hovermode='x unified',
            xaxis_title=x.replace('_', ' ').title(),
            yaxis_title=y.replace('_', ' ').title()
        )
        return fig

    @staticmethod
    def crear_heatmap_correlacion(df: pd.DataFrame,
                              variables: List[str],
                              titulo: str = "Matriz de Correlaciones") -> go.Figure:
        """Crea un heatmap de correlaciones entre variables"""
        corr_matrix = df[variables].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix,
            x=variables,
            y=variables,
            colorscale='RdBu',
            zmin=-1,
            zmax=1
        ))
        
        fig.update_layout(
            title=titulo,
            template='plotly_white',
            xaxis_title="Variables",
            yaxis_title="Variables"
        )
        return fig

    @staticmethod
    def crear_grafico_proyeccion(df: pd.DataFrame,
                             x: str,
                             y: str,
                             predicciones: List[float],
                             periodos_futuros: List[str],
                             titulo: str = "Proyección de Población") -> go.Figure:
        """Crea gráfico de proyección poblacional"""
        # Crear figura base con datos históricos
        fig = go.Figure()
        
        # Añadir datos históricos
        fig.add_trace(go.Scatter(
            x=df[x],
            y=df[y],
            name='Datos históricos',
            mode='lines+markers'
        ))
        
        # Añadir proyección
        fig.add_trace(go.Scatter(
            x=periodos_futuros,
            y=predicciones,
            name='Proyección',
            mode='lines+markers',
            line=dict(dash='dash')
        ))
        
        fig.update_layout(
            title=titulo,
            template='plotly_white',
            hovermode='x unified',
            xaxis_title=x.replace('_', ' ').title(),
            yaxis_title=y.replace('_', ' ').title(),
            showlegend=True
        )
        return fig

    @staticmethod
    def crear_piramide_poblacion(df: pd.DataFrame,
                             periodo: str = None,
                             titulo: str = None) -> go.Figure:
        """Crea una pirámide de población optimizada para datos del INE"""
        # Preparar datos
        hombres_df = df[df['Sexo_desc'] == 'Hombres'].sort_values('Edad_desc')
        mujeres_df = df[df['Sexo_desc'] == 'Mujeres'].sort_values('Edad_desc')
        
        fig = go.Figure()
        
        # Hombres (valores negativos para mostrar a la izquierda)
        fig.add_trace(go.Bar(
            y=hombres_df['Edad_desc'],
            x=-hombres_df['Total'],
            name='Hombres',
            orientation='h',
            marker_color='rgb(0, 123, 255)'
        ))
        
        # Mujeres (valores positivos para mostrar a la derecha)
        fig.add_trace(go.Bar(
            y=mujeres_df['Edad_desc'],
            x=mujeres_df['Total'],
            name='Mujeres',
            orientation='h',
            marker_color='rgb(255, 99, 132)'
        ))
        
        # Título dinámico
        if not titulo:
            titulo = f"Pirámide de Población{' - ' + periodo if periodo else ''}"
        
        # Actualizar diseño
        fig.update_layout(
            title=titulo,
            template='plotly_white',
            barmode='relative',
            bargap=0.1,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                title='Población',
                tickformat=',d',
                zeroline=True,
                zerolinecolor='black',
                zerolinewidth=1
            ),
            yaxis=dict(
                title='Grupo de edad',
                autorange="reversed"
            ),
            height=800
        )
        return fig

    @staticmethod
    def crear_grafico_pastel(df: pd.DataFrame,
                           names: str,
                           values: str,
                           titulo: str = "Gráfico de Sectores") -> go.Figure:
        """Crea un gráfico circular (pie chart)
        
        Args:
            df: DataFrame con los datos
            names: Columna para las etiquetas
            values: Columna para los valores
            titulo: Título del gráfico
            
        Returns:
            Figura de plotly
        """
        fig = px.pie(df,
                    names=names,
                    values=values,
                    title=titulo)
        
        fig.update_layout(
            template='plotly_white',
            showlegend=True
        )
        
        return fig

    @staticmethod
    def crear_grafico_dispersion(df: pd.DataFrame,
                             x: str,
                             y: str,
                             text: str = None,
                             titulo: str = "Gráfico de Dispersión") -> go.Figure:
        """Crea gráfico de dispersión con etiquetas opcionales"""
        if text:
            fig = px.scatter(df, x=x, y=y, text=text,
                           title=titulo,
                           labels={x: x.replace('_', ' ').title(),
                                  y: y.replace('_', ' ').title()})
            fig.update_traces(textposition='top center')
        else:
            fig = px.scatter(df, x=x, y=y,
                           title=titulo,
                           labels={x: x.replace('_', ' ').title(),
                                  y: y.replace('_', ' ').title()})
            
        fig.update_layout(
            template='plotly_white',
            xaxis_title=x.replace('_', ' ').title(),
            yaxis_title=y.replace('_', ' ').title()
        )
        return fig


    @staticmethod
    def crear_grafico_regresion_multiple(resultados: Dict, titulo: str = "Análisis de Regresión Múltiple") -> go.Figure:
        """Crea gráfico de regresión múltiple"""
        fig = go.Figure()
        
        # Gráfico de dispersión para valores reales vs predicciones
        fig.add_trace(go.Scatter(
            x=resultados['valores_reales'],
            y=resultados['predicciones'],
            mode='markers',
            name='Predicciones vs Reales',
            marker=dict(color='blue')
        ))
        
        # Línea de referencia y=x
        min_val = min(min(resultados['valores_reales']), min(resultados['predicciones']))
        max_val = max(max(resultados['valores_reales']), max(resultados['predicciones']))
        fig.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            name='Línea de referencia',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title=titulo,
            xaxis_title='Valores reales',
            yaxis_title='Valores predichos',
            template='plotly_white',
            showlegend=True
        )
        
        return fig

    @staticmethod
    def crear_grafico_series_temporales(resultados: Dict, datos_originales: pd.Series, titulo: str = "Análisis de Series Temporales") -> go.Figure:
        """Crea gráfico de análisis de series temporales"""
        fig = go.Figure()
        
        # Datos originales
        fig.add_trace(go.Scatter(
            y=datos_originales,
            name='Datos originales',
            mode='lines+markers'
        ))
        
        # Tendencia
        fig.add_trace(go.Scatter(
            y=resultados['descomposicion']['tendencia'],
            name='Tendencia',
            line=dict(color='red')
        ))
        
        # Componente estacional
        fig.add_trace(go.Scatter(
            y=resultados['descomposicion']['estacional'],
            name='Estacional',
            line=dict(color='green')
        ))
        
        fig.update_layout(
            title=titulo,
            template='plotly_white',
            showlegend=True,
            xaxis_title='Tiempo',
            yaxis_title='Valor'
        )
        
        return fig

    @staticmethod
    def crear_heatmap(df, titulo=''):
        """Crea un mapa de calor usando los datos proporcionados"""
        import plotly.graph_objects as go
        
        fig = go.Figure(data=go.Heatmap(
            z=df.values,
            x=df.columns,
            y=df.index,
            colorscale='Viridis'
        ))
        
        fig.update_layout(
            title=titulo,
            xaxis_title='Rango de Habitantes',
            yaxis_title='Periodo',
            height=500,
            template='plotly_white'
        )
        
        return fig

    @staticmethod
    def crear_grafico_tendencia_nacimientos(df: pd.DataFrame,
                                          provincia: str = None,
                                          incluir_ma: bool = True) -> go.Figure:
        """
        Crea un gráfico de tendencia temporal para tasas de nacimientos
        
        Args:
            df: DataFrame con los datos de nacimientos
            provincia: Nombre de la provincia para filtrar (opcional)
            incluir_ma: Incluir medias móviles en el gráfico
            
        Returns:
            Figura de plotly con la visualización temporal
        """
        # Filtrar por provincia si se especifica
        if provincia:
            df = df[df['Provincia'] == provincia].copy()
            
        # Ordenar por período
        df = df.sort_values('Periodo')
        
        # Crear figura base
        fig = go.Figure()
        
        # Añadir línea principal de nacimientos
        fig.add_trace(go.Scatter(
            x=df['Periodo'],
            y=df['Valor'],
            name='Nacimientos',
            mode='lines+markers'
        ))
        
        if incluir_ma:
            # Calcular y añadir medias móviles
            df['MA_3'] = df['Valor'].rolling(window=3).mean()
            df['MA_5'] = df['Valor'].rolling(window=5).mean()
            
            fig.add_trace(go.Scatter(
                x=df['Periodo'],
                y=df['MA_3'],
                name='Media Móvil (3 años)',
                line=dict(dash='dash')
            ))
            
            fig.add_trace(go.Scatter(
                x=df['Periodo'],
                y=df['MA_5'],
                name='Media Móvil (5 años)',
                line=dict(dash='dot')
            ))
        
        # Configurar layout
        titulo = f"Tendencia Temporal de Nacimientos{' - ' + provincia if provincia else ''}"
        fig.update_layout(
            title=titulo,
            template='plotly_white',
            xaxis_title='Año',
            yaxis_title='Número de Nacimientos',
            hovermode='x unified',
            showlegend=True
        )
        
        return fig

    @staticmethod
    def crear_grafico_comparativo_provincias(df: pd.DataFrame,
                                           provincias: list = None,
                                           metrica: str = 'Valor') -> go.Figure:
        """
        Crea un gráfico comparativo entre provincias
        
        Args:
            df: DataFrame con los datos de nacimientos
            provincias: Lista de provincias a comparar
            metrica: Nombre de la columna con los valores a comparar
            
        Returns:
            Figura de plotly con la comparación entre provincias
        """
        if provincias:
            df = df[df['Provincia'].isin(provincias)].copy()
            
        # Ordenar por período
        df = df.sort_values(['Periodo', 'Provincia'])
        
        # Crear figura base
        fig = go.Figure()
        
        # Añadir una línea por provincia
        for provincia in df['Provincia'].unique():
            df_prov = df[df['Provincia'] == provincia]
            
            fig.add_trace(go.Scatter(
                x=df_prov['Periodo'],
                y=df_prov[metrica],
                name=provincia,
                mode='lines+markers'
            ))
        
        # Configurar layout
        fig.update_layout(
            title='Comparativa entre Provincias',
            template='plotly_white',
            xaxis_title='Año',
            yaxis_title='Tasa de Nacimientos',
            hovermode='x unified',
            showlegend=True
        )
        
        return fig