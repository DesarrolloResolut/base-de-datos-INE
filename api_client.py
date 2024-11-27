import requests
from typing import Dict, List, Optional
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            # Loguear respuesta raw para debugging
            logger.info(f"Respuesta raw de la API: {response.text[:1000]}...")
            
            data = response.json()
            if not isinstance(data, (list, dict)):
                error_msg = "La respuesta no tiene un formato JSON válido"
                logger.error(f"{error_msg}. Contenido: {response.text[:500]}...")
                raise ValueError(error_msg)
            return data
        except requests.exceptions.JSONDecodeError as e:
            error_msg = f"Error al decodificar JSON: {str(e)}"
            logger.error(f"{error_msg}. Contenido: {response.text[:500]}...")
            raise ValueError(error_msg)
        except requests.exceptions.HTTPError as e:
            error_msg = f"Error en la solicitud HTTP: {response.status_code} - {str(e)}"
            logger.error(f"{error_msg}. Contenido: {response.text[:500]}...")
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error inesperado al procesar la respuesta: {str(e)}"
            logger.error(f"{error_msg}. Contenido: {response.text[:500]}...")
            raise ValueError(error_msg)
    
    @staticmethod
    def _validar_operacion(operacion: Dict) -> bool:
        """Valida si una operación tiene los campos mínimos necesarios"""
        logger.info(f"Validando operación: {json.dumps(operacion, indent=2)}")
        
        # Solo requerimos el nombre como campo obligatorio
        if not operacion.get('Nombre'):
            logger.warning(f"Operación sin nombre válido: {json.dumps(operacion, indent=2)}")
            return False
            
        # Agregar valores por defecto para campos faltantes
        if 'Periodicidad' not in operacion:
            operacion['Periodicidad'] = 'No especificada'
            logger.info(f"Agregando periodicidad por defecto para operación: {operacion['Nombre']}")
            
        if 'Codigo' not in operacion:
            operacion['Codigo'] = 'N/A'
            logger.info(f"Agregando código por defecto para operación: {operacion['Nombre']}")
            
        logger.info(f"Operación válida encontrada: {operacion['Nombre']}")
        return True

    @staticmethod
    def get_operaciones() -> List[Dict]:
        """Obtiene lista de operaciones estadísticas"""
        try:
            session = INEApiClient._get_session()
            url = f"{INEApiClient.BASE_URL}/operaciones"
            logger.info(f"Consultando operaciones en: {url}")
            
            response = session.get(url)
            data = INEApiClient._validate_json_response(response)
            
            if not isinstance(data, list):
                error_msg = "La respuesta no contiene una lista de operaciones"
                logger.error(f"{error_msg}. Contenido recibido: {type(data)}")
                raise ValueError(error_msg)
            
            # Loguear información de todas las operaciones
            logger.info(f"Total de operaciones recibidas: {len(data)}")
            
            # Filtrar operaciones válidas
            operaciones_validas = [
                op for op in data 
                if INEApiClient._validar_operacion(op)
            ]
            
            logger.info(f"Operaciones válidas encontradas: {len(operaciones_validas)}")
            
            if not operaciones_validas:
                error_msg = "No se encontraron operaciones con datos válidos"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Ordenar operaciones por nombre
            return sorted(operaciones_validas, key=lambda x: x.get('Nombre', '').lower())
            
        except Exception as e:
            error_msg = f"Error al obtener operaciones del INE: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    @staticmethod
    def get_tablas_operacion(operacion_id: str) -> List[Dict]:
        """Obtiene tablas de una operación específica"""
        try:
            if not operacion_id:
                error_msg = "No se proporcionó el ID de la operación"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            session = INEApiClient._get_session()
            url = f"{INEApiClient.BASE_URL}/tabla/{operacion_id}"
            logger.info(f"Consultando tablas para operación {operacion_id} en: {url}")
            
            response = session.get(url)
            data = INEApiClient._validate_json_response(response)
            
            if not isinstance(data, list):
                error_msg = "La respuesta no contiene una lista de tablas válida"
                logger.error(f"{error_msg}. Tipo de dato recibido: {type(data)}")
                raise ValueError(error_msg)
            
            logger.info(f"Tablas encontradas para operación {operacion_id}: {len(data)}")
            
            if not data:
                error_msg = f"No se encontraron tablas para la operación {operacion_id}"
                logger.warning(error_msg)
                raise ValueError(error_msg)
            
            return sorted(data, key=lambda x: x.get('nombre', '').lower())
            
        except Exception as e:
            error_msg = f"Error al obtener tablas de la operación {operacion_id}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    @staticmethod
    def get_datos_tabla(tabla_id: str, modo: str = "datos") -> Dict:
        """Obtiene datos de una tabla específica
        Args:
            tabla_id: ID de la tabla
            modo: 'datos' para datos amigables, 'metadatos' para metadatos
        """
        try:
            if not tabla_id:
                error_msg = "No se proporcionó el ID de la tabla"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            endpoint = "valores" if modo == "datos" else "metadata"
            url = f"{INEApiClient.BASE_URL}/{endpoint}/{tabla_id}"
            logger.info(f"Consultando {modo} de tabla {tabla_id} en: {url}")
            
            session = INEApiClient._get_session()
            response = session.get(url)
            data = INEApiClient._validate_json_response(response)
            
            if not data:
                error_msg = f"No se encontraron {modo} para la tabla {tabla_id}"
                logger.warning(error_msg)
                raise ValueError(error_msg)
                
            logger.info(f"Datos obtenidos correctamente para tabla {tabla_id}")
            return data
            
        except Exception as e:
            error_msg = f"Error al obtener {modo} de la tabla {tabla_id}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
