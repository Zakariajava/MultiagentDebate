"""
Configuración para usar GitHub Models con LangChain.

Este módulo proporciona una interfaz unificada para acceder a modelos de lenguaje 
alojados en GitHub Models mediante la integración con LangChain. Simplifica la 
configuración de modelos diferentes y gestiona la autenticación, permitiendo un 
acceso consistente a varios tipos de modelos para diferentes roles en el sistema 
de debates.

El módulo implementa un patrón Singleton con una instancia global del proveedor 
de modelos, además de funciones de utilidad para acceder a modelos específicos 
según los roles del debate (supervisor PRO, supervisor CONTRA, agentes).

Requiere las siguientes variables de entorno:
- GITHUB_TOKEN: Token de autenticación para GitHub Models
- GITHUB_MODELS_ENDPOINT: URL del endpoint de la API (opcional, tiene valor por defecto)
- SUPERVISOR_PRO_MODEL: Nombre del modelo para el supervisor PRO
- SUPERVISOR_CONTRA_MODEL: Nombre del modelo para el supervisor CONTRA
- AGENT_MODEL: Nombre del modelo para los agentes investigadores
"""
import os
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.language_models import BaseChatModel
from dotenv import load_dotenv
import logging

# Configurar logging básico para el módulo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno al iniciar el módulo
load_dotenv()

class GitHubModelsProvider:
    """
    Proveedor de modelos de GitHub para el sistema de debates.
    
    Esta clase gestiona la configuración y acceso a los modelos de lenguaje
    alojados en GitHub Models, encapsulando la lógica de autenticación y
    configuración específica para cada tipo de modelo.
    
    Attributes:
        token (str): Token de autenticación para GitHub Models.
        endpoint (str): URL del endpoint de la API.
        base_config (dict): Configuración base común para todos los modelos.
    """
    
    def __init__(self):
        """
        Inicializa el proveedor de modelos con la configuración desde variables de entorno.
        
        Carga el token de autenticación y endpoint desde las variables de entorno,
        configurando los headers y parámetros base para todos los modelos.
        
        Raises:
            ValueError: Si GITHUB_TOKEN no está definido en el archivo .env
        """
        self.token = os.getenv("GITHUB_TOKEN")
        self.endpoint = os.getenv("GITHUB_MODELS_ENDPOINT", "https://models.inference.ai.azure.com")
        
        if not self.token:
            raise ValueError("GITHUB_TOKEN no encontrado en .env")
        
        # Configuración base para todos los modelos
        self.base_config = {
            "base_url": self.endpoint,
            "api_key": self.token,
            "default_headers": {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        }
        
        logger.info(f"GitHub Models configurado con endpoint: {self.endpoint}")
    
    def get_chat_model(self, model_name: str, **kwargs) -> BaseChatModel:
        """
        Obtiene un modelo de chat configurado según los parámetros especificados.
        
        Crea y configura una instancia de ChatOpenAI con el modelo solicitado
        y los parámetros proporcionados, combinados con la configuración base.
        
        Args:
            model_name (str): Nombre del modelo de lenguaje a utilizar.
            **kwargs: Parámetros adicionales específicos para el modelo.
                      Comunes: temperature, max_tokens, etc.
        
        Returns:
            BaseChatModel: Instancia configurada del modelo de chat solicitado.
        """
        config = {
            **self.base_config,
            "model": model_name,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
            **kwargs
        }
        
        # Remover duplicados si existen en kwargs
        if "api_key" in kwargs:
            config.pop("api_key")
        
        logger.info(f"Creando modelo de chat: {model_name}")
        
        return ChatOpenAI(**config)
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión con GitHub Models enviando una solicitud simple.
        
        Intenta crear un modelo y realizar una llamada básica para verificar
        que la configuración y autenticación funcionan correctamente.
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario.
        """
        try:
            model = self.get_chat_model("Mistral-Nemo")
            response = model.invoke("Responde solo con 'OK' si recibes este mensaje")
            logger.info(f"Conexión exitosa. Respuesta: {response.content}")
            return True
        except Exception as e:
            logger.error(f"Error al conectar con GitHub Models: {e}")
            return False

# Instancia global del proveedor para uso en todo el sistema
github_models = GitHubModelsProvider()

# Funciones de conveniencia para acceder a modelos específicos

def get_supervisor_pro_model(**kwargs) -> BaseChatModel:
    """
    Obtiene el modelo configurado para el Supervisor PRO.
    
    Crea una instancia del modelo especificado en la variable de entorno
    SUPERVISOR_PRO_MODEL con los parámetros proporcionados.
    
    Args:
        **kwargs: Parámetros de configuración adicionales para el modelo.
    
    Returns:
        BaseChatModel: Modelo configurado para el Supervisor PRO.
    """
    model_name = os.getenv("SUPERVISOR_PRO_MODEL", "gpt-4.1-nano")
    return github_models.get_chat_model(model_name, **kwargs)

def get_supervisor_contra_model(**kwargs) -> BaseChatModel:
    """
    Obtiene el modelo configurado para el Supervisor CONTRA.
    
    Crea una instancia del modelo especificado en la variable de entorno
    SUPERVISOR_CONTRA_MODEL con los parámetros proporcionados.
    
    Args:
        **kwargs: Parámetros de configuración adicionales para el modelo.
    
    Returns:
        BaseChatModel: Modelo configurado para el Supervisor CONTRA.
    """
    model_name = os.getenv("SUPERVISOR_CONTRA_MODEL", "Llama-4-Scout-17B-16E-Instruct")
    return github_models.get_chat_model(model_name, **kwargs)

def get_agent_model(**kwargs) -> BaseChatModel:
    """
    Obtiene el modelo configurado para los agentes investigadores.
    
    Crea una instancia del modelo especificado en la variable de entorno
    AGENT_MODEL con los parámetros proporcionados.
    
    Args:
        **kwargs: Parámetros de configuración adicionales para el modelo.
    
    Returns:
        BaseChatModel: Modelo configurado para los agentes investigadores.
    """
    model_name = os.getenv("AGENT_MODEL", "Mistral-Nemo")
    return github_models.get_chat_model(model_name, **kwargs)