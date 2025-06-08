"""
Configuración principal del sistema de debates
VERSIÓN CORREGIDA: Propiedades arregladas, sin focus_areas, con rate limiting

Este módulo centraliza toda la configuración del sistema de debates, proporcionando
una interfaz unificada para acceder a parámetros de configuración. Implementa un patrón
Singleton para la carga de variables de entorno y utiliza métodos de clase para
acceder a los valores de configuración de manera eficiente.
"""
import os
from enum import Enum
from typing import Dict, List, Any
from dotenv import load_dotenv

class Config:
    """
    Configuración principal del sistema - VERSIÓN COMPLETAMENTE CORREGIDA
    
    Esta clase implementa un patrón Singleton para la carga de variables de entorno
    y proporciona acceso a todos los parámetros de configuración del sistema mediante
    métodos de clase. Garantiza que las variables de entorno se carguen una sola vez
    y mantiene constantes para diversos aspectos del sistema.
    
    CORRECCIONES:
    - Propiedades de clase definidas correctamente
    - Variables de entorno cargadas una sola vez
    - Sin mezclar @property con @classmethod
    - Configuración más conservadora para evitar rate limiting
    """
    
    # Flag para indicar si las variables de entorno ya fueron cargadas
    _loaded = False
    
    @classmethod
    def _ensure_loaded(cls):
        """
        Asegura que las variables de entorno estén cargadas.
        
        Implementa un patrón lazy-loading para cargar las variables
        de entorno solo cuando son necesarias y una única vez.
        """
        if not cls._loaded:
            load_dotenv()
            cls._loaded = True
    
    # Métodos de configuración dinámica desde variables de entorno
    @classmethod
    def MAX_ROUNDS(cls) -> int:
        """
        Obtiene el número máximo de rondas para el debate.
        
        Returns:
            int: Número máximo de rondas, por defecto 3 si no está configurado.
        """
        cls._ensure_loaded()
        return int(os.getenv("MAX_ROUNDS", "3"))
    
    @classmethod
    def AGENTS_PER_TEAM(cls) -> int:
        """
        Obtiene el número de agentes por equipo.
        
        Returns:
            int: Número de agentes por equipo, por defecto 5 si no está configurado.
        """
        cls._ensure_loaded()
        return int(os.getenv("AGENTS_PER_TEAM", "5"))
    
    @classmethod
    def DEBUG_MODE(cls) -> bool:
        """
        Determina si el sistema está en modo debug.
        
        Returns:
            bool: True si está en modo debug, False en caso contrario.
        """
        cls._ensure_loaded()
        return os.getenv("DEBUG_MODE", "True").lower() == "true"
    
    # Constantes de tiempos de espera para operaciones
    SEARCH_TIMEOUT = 30  # segundos máximos para operaciones de búsqueda
    MODEL_TIMEOUT = 60   # segundos máximos para llamadas a modelos LLM
    AGENT_COORDINATION_DELAY = 3  # segundos entre agentes para evitar solapamiento
    SUPERVISOR_DELAY = 2  # segundos entre llamadas a supervisores
    
    # Constantes para limitar el uso de recursos y API calls
    MAX_FRAGMENTS_PER_AGENT = 5  # máximo de fragmentos que puede recolectar un agente
    MAX_QUERIES_PER_AGENT = 2    # máximo de consultas de búsqueda por agente
    MAX_RESULTS_PER_QUERY = 2    # máximo de resultados a procesar por consulta
    MAX_ARGUMENT_LENGTH = 1500   # longitud máxima de argumentos en caracteres
    
    # Umbrales de puntuación para evaluación de fragmentos
    MIN_FRAGMENT_SCORE = 0.6     # puntuación mínima para considerar un fragmento válido
    SIMILARITY_THRESHOLD = 0.85  # umbral para considerar dos fragmentos como similares
    
    # Configuración para controlar rate limiting de APIs
    MIN_DELAY_BETWEEN_API_CALLS = 1.5  # segundos mínimos entre llamadas a APIs
    MIN_DELAY_BETWEEN_SEARCHES = 2.0   # segundos mínimos entre búsquedas
    MAX_API_CALLS_PER_MINUTE = 30      # límite de llamadas a APIs por minuto
    
    @classmethod
    def ensure_loaded(cls):
        """
        Método público para asegurar carga de configuración.
        
        Puede ser llamado explícitamente para garantizar que
        las variables de entorno estén cargadas antes de usar
        la configuración.
        """
        cls._ensure_loaded()
    
    @classmethod
    def get_environment_config(cls) -> Dict[str, Any]:
        """
        Devuelve configuración según el ambiente de ejecución.
        
        Proporciona parámetros optimizados para cada ambiente
        (producción, testing, desarrollo).
        
        Returns:
            Dict[str, Any]: Diccionario con la configuración específica del ambiente.
        """
        cls._ensure_loaded()
        env = os.getenv("ENVIRONMENT", "development")
        
        configs = {
            "production": {
                "max_rounds": 5,
                "max_queries_per_agent": 3,
                "max_results_per_query": 3,
                "agent_delay": 5,
                "supervisor_delay": 3,
                "min_fragment_score": 0.7
            },
            "testing": {
                "max_rounds": 2,
                "max_queries_per_agent": 1,
                "max_results_per_query": 2,
                "agent_delay": 1,
                "supervisor_delay": 1,
                "min_fragment_score": 0.5
            },
            "development": {
                "max_rounds": 3,
                "max_queries_per_agent": 2,
                "max_results_per_query": 2,
                "agent_delay": 3,
                "supervisor_delay": 2,
                "min_fragment_score": 0.6
            }
        }
        
        return configs.get(env, configs["development"])

class AgentRole(Enum):
    """
    Enumeración de roles especializados para los agentes investigadores.
    
    Cada rol tiene una especialidad específica para la búsqueda de
    información y evaluación de evidencia.
    """
    CIENTIFICO = "cientifico"   # Enfocado en evidencia científica y estudios
    ECONOMICO = "economico"     # Especializado en impactos económicos y financieros
    HISTORICO = "historico"     # Centrado en contexto histórico y antecedentes
    REFUTADOR = "refutador"     # Busca contraargumentos y limitaciones
    PSICOLOGICO = "psicologico" # Especializado en aspectos psicológicos y sociales

class DebatePhase(Enum):
    """
    Enumeración de las diferentes fases de un debate.
    
    Define el flujo de progresión del debate desde la investigación
    inicial hasta el cierre.
    """
    INVESTIGACION_INICIAL = "investigacion_inicial"  # Recolección de evidencia
    ARGUMENTACION = "argumentacion"                  # Presentación de argumentos iniciales
    REFUTACION = "refutacion"                        # Respuestas a argumentos opuestos
    PROFUNDIZACION = "profundizacion"                # Desarrollo de argumentos más complejos
    CIERRE = "cierre"                                # Conclusiones finales

class ModelConfig:
    """
    Configuración específica para modelos de lenguaje (LLM).
    
    Proporciona ajustes para diferentes modelos según su rol
    en el sistema de debates.
    """
    
    @classmethod
    def get_model_settings(cls) -> Dict[str, Any]:
        """
        Configuración de modelos según el ambiente.
        
        Proporciona configuraciones específicas para cada tipo de agente,
        optimizando parámetros como temperatura y tokens máximos.
        
        Returns:
            Dict[str, Any]: Configuraciones para los diferentes tipos de modelos.
        """
        Config.ensure_loaded()
        
        # Configuración base común para todos los modelos
        base_config = {
            "temperature": 0.7,     # Balance entre creatividad y coherencia
            "max_tokens": 1500,     # Límite de tokens en respuestas
            "timeout": 60           # Tiempo máximo de espera para respuestas
        }
        
        # Configuración específica por tipo de agente
        return {
            "supervisor_pro": {     # Supervisor del equipo PRO
                **base_config,
                "temperature": 0.7,  # Mayor creatividad para argumentación
                "max_tokens": 2000   # Respuestas más extensas
            },
            "supervisor_contra": {   # Supervisor del equipo CONTRA
                **base_config,
                "temperature": 0.7,  # Mayor creatividad para argumentación
                "max_tokens": 2000   # Respuestas más extensas
            },
            "agents": {              # Agentes investigadores
                **base_config,
                "temperature": 0.3,  # Menor temperatura para mayor precisión
                "max_tokens": 1500   # Respuestas más concisas
            }
        }

class ConfigValidator:
    """
    Valida que la configuración sea correcta y completa.
    
    Proporciona métodos para verificar variables de entorno,
    límites y generar reportes de validación.
    """
    
    @staticmethod
    def validate_environment() -> List[str]:
        """
        Valida que todas las variables de entorno necesarias estén configuradas.
        
        Verifica la presencia y formato de variables críticas como tokens
        de API y endpoints.
        
        Returns:
            List[str]: Lista de errores encontrados en la configuración.
        """
        Config.ensure_loaded()
        errors = []
        
        # Variables esenciales para el funcionamiento del sistema
        required_vars = [
            "GITHUB_TOKEN",
            "GITHUB_MODELS_ENDPOINT", 
            "SUPERVISOR_PRO_MODEL",
            "SUPERVISOR_CONTRA_MODEL",
            "AGENT_MODEL"
        ]
        
        # Verificar presencia de variables requeridas
        for var in required_vars:
            if not os.getenv(var):
                errors.append(f"Variable de entorno requerida no encontrada: {var}")
        
        # Validar formato de token de GitHub
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token and not github_token.startswith("ghp_"):
            errors.append("GITHUB_TOKEN debe empezar con 'ghp_'")
        
        # Validar configuración de API de búsqueda
        tavily_key = os.getenv("TAVILY_API_KEY")
        if not tavily_key or tavily_key == "your_tavily_api_key_here":
            errors.append("TAVILY_API_KEY no configurada o usando valor por defecto")
        
        return errors
    
    @staticmethod
    def validate_limits() -> List[str]:
        """
        Valida que los límites configurados sean razonables.
        
        Verifica que los parámetros de límites no excedan umbrales
        que podrían causar problemas de rendimiento o rate limiting.
        
        Returns:
            List[str]: Lista de advertencias sobre límites problemáticos.
        """
        errors = []
        
        # Verificar límites potencialmente problemáticos
        if Config.MAX_ROUNDS() > 10:
            errors.append("MAX_ROUNDS muy alto (>10), puede causar rate limiting")
        
        if Config.MAX_QUERIES_PER_AGENT > 5:
            errors.append("MAX_QUERIES_PER_AGENT muy alto (>5), puede causar rate limiting")
        
        if Config.MAX_FRAGMENTS_PER_AGENT > 15:
            errors.append("MAX_FRAGMENTS_PER_AGENT muy alto (>15), puede ser lento")
        
        return errors
    
    @staticmethod
    def get_validation_report() -> Dict[str, List[str]]:
        """
        Devuelve un reporte completo de validación de la configuración.
        
        Combina resultados de diferentes validaciones en un único reporte.
        
        Returns:
            Dict[str, List[str]]: Reporte completo con errores y advertencias.
        """
        return {
            "environment_errors": ConfigValidator.validate_environment(),
            "limits_warnings": ConfigValidator.validate_limits(),
            "config_loaded": Config._loaded
        }

class LogConfig:
    """
    Configuración para el sistema de logging.
    
    Proporciona ajustes para el registro de eventos según
    el ambiente de ejecución.
    """
    
    @staticmethod
    def get_logging_config() -> Dict[str, Any]:
        """
        Configuración de logging según el ambiente.
        
        Ajusta nivel de detalle, formato y destino de los logs
        según el ambiente de ejecución (producción, testing, desarrollo).
        
        Returns:
            Dict[str, Any]: Configuración de logging para el ambiente actual.
        """
        Config.ensure_loaded()
        env = os.getenv("ENVIRONMENT", "development")
        
        # Configuraciones específicas por ambiente
        if env == "production":
            level = "INFO"
            format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        elif env == "testing":
            level = "WARNING"
            format_str = "%(levelname)s: %(message)s"
        else:  # development
            level = "DEBUG" if Config.DEBUG_MODE() else "INFO"
            format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        return {
            "level": level,                # Nivel de detalle de los logs
            "format": format_str,          # Formato de los mensajes
            "filename": f"debate_{env}.log" if env == "production" else None,  # Archivo de log en producción
            "console": True                # Mostrar logs en consola
        }