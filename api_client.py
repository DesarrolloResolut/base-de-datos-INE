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
        """Configura una sesión de requests con retry más robusto"""
        session = requests.Session()
        retry = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            respect_retry_after_header=True
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.headers.update({'Accept': 'application/json'})
        return session

    @staticmethod
    def _validate_json_response(response: requests.Response) -> Dict:
        """Valida la respuesta JSON de la API"""
        try:
            response.raise_for_status()
            
            # Validar content-type y manejar respuestas no-JSON
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('application/json'):
                logger.warning(f"Respuesta no es JSON. Content-Type: {content_type}")
                logger.warning(f"URL: {response.url}")
                logger.warning(f"Status Code: {response.status_code}")
                logger.warning(f"Headers: {dict(response.headers)}")
                logger.warning(f"Contenido: {response.text[:500]}...")
                if response.text.strip().startswith('La operación indicada no existe'):
                    raise ValueError(f"La operación o tabla indicada no existe: {response.text}")
            
            # Loguear respuesta raw para debugging
            logger.info(f"URL consultada: {response.url}")
            logger.info(f"Status code: {response.status_code}")
            logger.info(f"Respuesta raw de la API: {response.text[:1000]}...")
            
            data = response.json()
            if not isinstance(data, (list, dict)):
                error_msg = "La respuesta no tiene un formato JSON válido"
                logger.error(f"{error_msg}. Contenido: {response.text[:500]}...")
                raise ValueError(error_msg)
            return data
            
        except requests.exceptions.JSONDecodeError as e:
            error_msg = f"Error al decodificar JSON: {str(e)}"
            logger.error(f"{error_msg}. URL: {response.url}")
            logger.error(f"Contenido: {response.text[:500]}...")
            raise ValueError(error_msg)
        except requests.exceptions.HTTPError as e:
            error_msg = f"Error en la solicitud HTTP: {response.status_code} - {str(e)}"
            logger.error(f"{error_msg}. URL: {response.url}")
            logger.error(f"Contenido: {response.text[:500]}...")
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error inesperado al procesar la respuesta: {str(e)}"
            logger.error(f"{error_msg}. URL: {response.url}")
            logger.error(f"Contenido: {response.text[:500]}...")
            raise ValueError(error_msg)
    
    @staticmethod
    def _validar_operacion(operacion: Dict) -> bool:
        """Valida si una operación tiene los campos mínimos necesarios"""
        logger.info(f"Validando operación: {json.dumps(operacion, indent=2)}")
        
        # Validar ID
        if not isinstance(operacion.get('Id'), (int, str)) and not isinstance(operacion.get('id'), (int, str)):
            logger.warning(f"Operación sin ID válido: {json.dumps(operacion, indent=2)}")
            return False
        
        # Solo requerimos el nombre como campo obligatorio
        nombre = operacion.get('Nombre') or operacion.get('nombre')
        if not nombre:
            logger.warning(f"Operación sin nombre válido: {json.dumps(operacion, indent=2)}")
            return False
            
        # Normalizar el campo nombre
        operacion['Nombre'] = nombre
            
        # Agregar valores por defecto para campos faltantes
        if 'Periodicidad' not in operacion and 'periodicidad' not in operacion:
            operacion['Periodicidad'] = 'No especificada'
            logger.info(f"Agregando periodicidad por defecto para operación: {nombre}")
            
        if 'Codigo' not in operacion and 'codigo' not in operacion:
            operacion['Codigo'] = 'N/A'
            logger.info(f"Agregando código por defecto para operación: {nombre}")
            
        logger.info(f"Operación válida encontrada: {nombre}")
        return True

    @staticmethod
    def _es_operacion_demografica(operacion: Dict) -> bool:
        """Determina si una operación está relacionada con datos demográficos"""
        palabras_clave = [
            'población', 'demografía', 'censo', 'nacimientos',
            'defunciones', 'matrimonios', 'migraciones', 'padrón',
            'habitantes', 'residentes', 'demográfico', 'demográfica'
        ]
        
        nombre = operacion.get('Nombre') or operacion.get('nombre')
        if not nombre:
            return False
            
        nombre = nombre.lower()
        return any(palabra in nombre for palabra in palabras_clave)

    @staticmethod
    def get_operaciones() -> List[Dict]:
        """Obtiene lista de operaciones estadísticas demográficas"""
        try:
            session = INEApiClient._get_session()
            url = f"{INEApiClient.BASE_URL}/OPERACIONES_DISPONIBLES"
            params = {'geo': '1', 'det': '2'}
            logger.info(f"Consultando operaciones en: {url}")
            
            response = session.get(url, params=params)
            data = INEApiClient._validate_json_response(response)
            
            if not isinstance(data, list):
                error_msg = "La respuesta no contiene una lista de operaciones"
                logger.error(f"{error_msg}. Contenido recibido: {type(data)}")
                raise ValueError(error_msg)
            
            # Loguear información de todas las operaciones
            logger.info(f"Total de operaciones recibidas: {len(data)}")
            
            # Normalizar IDs y filtrar operaciones válidas y demográficas
            operaciones_procesadas = []
            for op in data:
                # Validar y normalizar operación
                if INEApiClient._validar_operacion(op) and INEApiClient._es_operacion_demografica(op):
                    op['id'] = op.get('Id') or op.get('id')
                    operaciones_procesadas.append(op)
                    logger.debug(f"Operación válida agregada: {op.get('Nombre')}")
            
            logger.info(f"Operaciones válidas encontradas: {len(operaciones_procesadas)}")
            
            if not operaciones_procesadas:
                logger.warning("No se encontraron operaciones válidas después del filtrado")
                raise ValueError("No se encontraron operaciones con datos válidos")
            
            # Ordenar operaciones por nombre
            return sorted(operaciones_procesadas, key=lambda x: x.get('Nombre', '').lower())
            
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
            
            # Intentar primero con el endpoint operaciones_tabla
            url = f"{INEApiClient.BASE_URL}/TABLAS_OPERACION/{operacion_id}"
            params = {'geo': '1'}
            logger.info(f"Consultando tablas para operación {operacion_id} en: {url}")
            
            try:
                response = session.get(url)
                
                # Si la respuesta es texto plano, puede ser un error
                if response.headers.get('content-type', '').startswith('text/plain'):
                    # Intentar con el endpoint alternativo
                    url_alt = f"{INEApiClient.BASE_URL}/variables/{operacion_id}"
                    logger.info(f"Intentando endpoint alternativo: {url_alt}")
                    response = session.get(url_alt)
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Error en la solicitud HTTP: {str(e)}")
                raise ValueError(f"Error al conectar con el servidor: {str(e)}")
                
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
            
            # Normalizar y validar las tablas
            tablas_procesadas = []
            for tabla in data:
                if isinstance(tabla, dict) and tabla.get('nombre'):
                    tablas_procesadas.append(tabla)
                    
            return sorted(tablas_procesadas, key=lambda x: x.get('nombre', '').lower())
            
        except Exception as e:
            error_msg = f"Error al obtener tablas de la operación {operacion_id}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    @staticmethod
    def get_datos_tabla(tabla_id: str = "9687") -> Dict:
        """Obtiene datos de población residente
        Args:
            tabla_id: ID de la tabla (por defecto '9687' para población residente)
        """
        try:
            url = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/9687"
            params = {'nult': '2', 'tip': 'AM'}
            logger.info(f"Consultando datos de población residente en: {url}")
            
            session = INEApiClient._get_session()
            try:
                response = session.get(url, params=params)
                
                if response.headers.get('content-type', '').startswith('text/plain'):
                    error_msg = response.text.strip()
                    raise ValueError(error_msg)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error en la solicitud HTTP: {str(e)}")
                raise ValueError(f"Error al conectar con el servidor: {str(e)}")
                
            data = INEApiClient._validate_json_response(response)
            
            if not data:
                error_msg = "No se encontraron datos de población residente"
                logger.warning(error_msg)
                raise ValueError(error_msg)
                
            logger.info("Datos de población residente obtenidos correctamente")
            return data
            
        except Exception as e:
            error_msg = f"Error al obtener datos de población residente: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
