import requests
from typing import Dict, List, Optional
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json

class INEApiClient:
    """Cliente para la API del INE"""
    
    BASE_URL = "https://servicios.ine.es/wstempus/js/ES"
    
    @staticmethod
    def _get_session():
        """Configura una sesión de requests con retry"""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    @staticmethod
    def _validate_json_response(response: requests.Response) -> Dict:
        """Valida la respuesta JSON de la API"""
        try:
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, (list, dict)):
                raise ValueError("Formato de respuesta JSON inválido")
            return data
        except requests.exceptions.JSONDecodeError:
            raise ValueError("La respuesta no es un JSON válido")
        except requests.exceptions.HTTPError as e:
            raise ValueError(f"Error HTTP: {e}")
        except Exception as e:
            raise ValueError(f"Error al procesar la respuesta: {str(e)}")
    
    @staticmethod
    def get_operaciones() -> List[Dict]:
        """Obtiene lista de operaciones estadísticas"""
        try:
            session = INEApiClient._get_session()
            response = session.get(f"{INEApiClient.BASE_URL}/operaciones")
            data = INEApiClient._validate_json_response(response)
            
            # Ordenar operaciones por nombre
            if isinstance(data, list):
                return sorted(data, key=lambda x: x.get('nombre', '').lower())
            raise ValueError("La respuesta no contiene una lista de operaciones")
            
        except Exception as e:
            raise ValueError(f"Error al obtener operaciones: {str(e)}")
    
    @staticmethod
    def get_tablas_operacion(operacion_id: str) -> List[Dict]:
        """Obtiene tablas de una operación específica"""
        try:
            if not operacion_id:
                raise ValueError("ID de operación no proporcionado")
                
            session = INEApiClient._get_session()
            response = session.get(f"{INEApiClient.BASE_URL}/tabla/{operacion_id}")
            data = INEApiClient._validate_json_response(response)
            
            if isinstance(data, list):
                return sorted(data, key=lambda x: x.get('nombre', '').lower())
            raise ValueError("La respuesta no contiene una lista de tablas")
            
        except Exception as e:
            raise ValueError(f"Error al obtener tablas: {str(e)}")
    
    @staticmethod
    def get_datos_tabla(tabla_id: str, modo: str = "datos") -> Dict:
        """Obtiene datos de una tabla específica
        Args:
            tabla_id: ID de la tabla
            modo: 'datos' para datos amigables, 'metadatos' para metadatos
        """
        try:
            if not tabla_id:
                raise ValueError("ID de tabla no proporcionado")
                
            endpoint = "valores" if modo == "datos" else "metadata"
            session = INEApiClient._get_session()
            response = session.get(f"{INEApiClient.BASE_URL}/{endpoint}/{tabla_id}")
            return INEApiClient._validate_json_response(response)
            
        except Exception as e:
            raise ValueError(f"Error al obtener datos de la tabla: {str(e)}")
