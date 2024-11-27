import requests
from typing import Dict, List, Optional
import pandas as pd

class INEApiClient:
    """Cliente para la API del INE"""
    
    BASE_URL = "https://servicios.ine.es/wstempus/js/ES"
    
    @staticmethod
    def get_operaciones() -> List[Dict]:
        """Obtiene lista de operaciones estadísticas"""
        response = requests.get(f"{INEApiClient.BASE_URL}/operaciones")
        return response.json()
    
    @staticmethod
    def get_tablas_operacion(operacion_id: str) -> List[Dict]:
        """Obtiene tablas de una operación específica"""
        response = requests.get(f"{INEApiClient.BASE_URL}/tabla/{operacion_id}")
        return response.json()
    
    @staticmethod
    def get_datos_tabla(tabla_id: str, modo: str = "datos") -> Dict:
        """Obtiene datos de una tabla específica
        Args:
            tabla_id: ID de la tabla
            modo: 'datos' para datos amigables, 'metadatos' para metadatos
        """
        endpoint = "valores" if modo == "datos" else "metadata"
        response = requests.get(f"{INEApiClient.BASE_URL}/{endpoint}/{tabla_id}")
        return response.json()
    
    @staticmethod
    def buscar_operaciones(query: str) -> List[Dict]:
        """Busca operaciones por término"""
        operaciones = INEApiClient.get_operaciones()
        return [op for op in operaciones 
                if query.lower() in op.get('nombre', '').lower()]
