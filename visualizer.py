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
