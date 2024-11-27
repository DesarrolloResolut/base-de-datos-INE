import requests
from typing import Dict, List, Optional
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
from datetime import datetime

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
                raise ValueError("La respuesta no tiene un formato JSON válido")
            return data
        except requests.exceptions.JSONDecodeError:
            raise ValueError("La respuesta no es un JSON válido")
        except requests.exceptions.HTTPError as e:
            raise ValueError(f"Error en la solicitud HTTP: {e}")
        except Exception as e:
            raise ValueError(f"Error al procesar la respuesta: {str(e)}")
    
    @staticmethod
    def _validar_operacion(operacion: Dict) -> bool:
        """Valida si una operación tiene los campos mínimos necesarios"""
        campos_requeridos = ['nombre', 'periodicidad']
        return all(operacion.get(campo) for campo in campos_requeridos)

    @staticmethod
    def get_operaciones() -> List[Dict]:
        """Obtiene lista de operaciones estadísticas"""
        try:
            session = INEApiClient._get_session()
            response = session.get(f"{INEApiClient.BASE_URL}/operaciones")
            data = INEApiClient._validate_json_response(response)
            
            if not isinstance(data, list):
                raise ValueError("La respuesta no contiene una lista de operaciones")
            
            # Filtrar operaciones válidas
            operaciones_validas = [
                op for op in data 
                if INEApiClient._validar_operacion(op)
            ]
            
            if not operaciones_validas:
                raise ValueError("No se encontraron operaciones con datos válidos")
            
            # Ordenar operaciones por nombre
            return sorted(operaciones_validas, key=lambda x: x.get('nombre', '').lower())
            
        except Exception as e:
            raise ValueError(f"Error al obtener operaciones: {str(e)}")
    
    @staticmethod
    def get_tablas_operacion(operacion_id: str) -> List[Dict]:
        """Obtiene tablas de una operación específica"""
        try:
            if not operacion_id:
                raise ValueError("No se proporcionó el ID de la operación")
                
            session = INEApiClient._get_session()
            response = session.get(f"{INEApiClient.BASE_URL}/tabla/{operacion_id}")
            data = INEApiClient._validate_json_response(response)
            
            if not isinstance(data, list):
                raise ValueError("La respuesta no contiene una lista de tablas válida")
            
            if not data:
                raise ValueError("No se encontraron tablas para esta operación")
            
            return sorted(data, key=lambda x: x.get('nombre', '').lower())
            
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
                raise ValueError("No se proporcionó el ID de la tabla")
                
            endpoint = "valores" if modo == "datos" else "metadata"
            session = INEApiClient._get_session()
            response = session.get(f"{INEApiClient.BASE_URL}/{endpoint}/{tabla_id}")
            data = INEApiClient._validate_json_response(response)
            
            if not data:
                raise ValueError("No se encontraron datos para esta tabla")
                
            return data
            
        except Exception as e:
            raise ValueError(f"Error al obtener datos de la tabla: {str(e)}")
