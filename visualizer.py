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
                     labels={x: x.capitalize(), y: y.capitalize()})
        fig.update_layout(
            template='plotly_white',
            hovermode='x unified',
            legend_title_text=color.capitalize() if color else None
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
                    labels={x: x.capitalize(), y: y.capitalize()})
        fig.update_layout(
            template='plotly_white',
            barmode='group' if color else 'relative',
            legend_title_text=color.capitalize() if color else None
        )
        return fig
    
    @staticmethod
    def crear_mapa_espana(df: pd.DataFrame,
                         columna_ccaa: str,
                         columna_valores: str,
                         titulo: str = "Mapa por CCAA") -> go.Figure:
        """Crea mapa coroplético de España"""
        # Simplificado por ahora - requeriría geojson de CCAA
        fig = px.choropleth(df,
                           locations=columna_ccaa,
                           color=columna_valores,
                           scope="europe",
                           title=titulo)
        fig.update_layout(
            template='plotly_white',
            geo_scope='europe',
        )
        return fig
