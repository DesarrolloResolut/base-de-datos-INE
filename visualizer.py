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
            x=-hombres_df['Total'],  # Valores negativos para la izquierda
            name='Hombres',
            orientation='h',
            marker_color='rgb(0, 123, 255)'  # Azul
        ))
        
        # Mujeres (valores positivos para mostrar a la derecha)
        fig.add_trace(go.Bar(
            y=mujeres_df['Edad_desc'],
            x=mujeres_df['Total'],
            name='Mujeres',
            orientation='h',
            marker_color='rgb(255, 99, 132)'  # Rosa
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
                tickformat=',d',  # Formato de números con separadores de miles
                zeroline=True,
                zerolinecolor='black',
                zerolinewidth=1
            ),
            yaxis=dict(
                title='Grupo de edad',
                autorange="reversed"  # Invertir el eje Y para mostrar edades de mayor a menor
            ),
            height=800  # Altura fija para mejor visualización
        )
        
        return fig
