import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict

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
    def crear_mapa_espana(df: pd.DataFrame,
                         columna_ccaa: str,
                         columna_valores: str,
                         titulo: str = "Distribución por Comunidades Autónomas") -> go.Figure:
        """Crea mapa coroplético de España"""
        fig = px.choropleth(df,
                           locations=columna_ccaa,
                           color=columna_valores,
                           scope="europe",
                           title=titulo,
                           labels={columna_valores: columna_valores.replace('_', ' ').title()})
        fig.update_layout(
            template='plotly_white',
            geo_scope='europe'
        )
        return fig
        
    @staticmethod
    def crear_piramide_poblacion(df: pd.DataFrame,
                               col_edad: str,
                               col_hombres: str,
                               col_mujeres: str,
                               titulo: str = "Pirámide de Población") -> go.Figure:
        """Crea una pirámide de población"""
        fig = go.Figure()
        
        # Hombres (valores negativos para mostrar a la izquierda)
        fig.add_trace(go.Bar(
            y=df[col_edad],
            x=-df[col_hombres],
            name='Hombres',
            orientation='h',
            marker_color='blue'
        ))
        
        # Mujeres (valores positivos para mostrar a la derecha)
        fig.add_trace(go.Bar(
            y=df[col_edad],
            x=df[col_mujeres],
            name='Mujeres',
            orientation='h',
            marker_color='red'
        ))
        
        fig.update_layout(
            title=titulo,
            template='plotly_white',
            barmode='relative',
            bargap=0.1,
            xaxis=dict(title='Población'),
            yaxis=dict(title='Grupo de edad')
        )
        
        return fig
