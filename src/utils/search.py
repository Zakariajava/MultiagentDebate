"""
Sistema de búsqueda REAL para el debate.

Este módulo implementa un sistema de búsqueda de información para el sistema de debates,
utilizando la API de Tavily para realizar consultas en tiempo real. Incluye funcionalidades
de caché para optimizar el rendimiento y evitar búsquedas repetidas, así como un manejo
robusto de errores y configuración.

El sistema está diseñado para trabajar exclusivamente con búsquedas reales en internet,
obteniendo información actualizada y relevante para los debates.
"""
import os
import json
import hashlib
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
from dotenv import load_dotenv

# Importar Tavily con manejo de dependencia opcional
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

# Cargar variables de entorno y configurar logger
load_dotenv()
logger = logging.getLogger(__name__)

class SearchResult:
    """
    Clase que estructura y estandariza los resultados de búsqueda.
    
    Encapsula toda la información relevante de un resultado de búsqueda
    incluyendo título, contenido, URL, fuente, fecha y puntuación.
    
    Attributes:
        title (str): Título del resultado de búsqueda.
        content (str): Contenido o extracto del resultado.
        url (str): URL completa del resultado.
        source (str): Nombre de la fuente o dominio.
        date (datetime): Fecha de publicación o recuperación.
        score (float): Puntuación de relevancia (0.0-1.0).
    """
    def __init__(self, title: str, content: str, url: str, source: str, 
                 date: Optional[datetime] = None, score: float = 0.0):
        """
        Inicializa un nuevo resultado de búsqueda.
        
        Args:
            title: Título del resultado.
            content: Contenido o extracto del texto.
            url: URL completa del recurso.
            source: Nombre de la fuente o dominio.
            date: Fecha de publicación o recuperación (opcional).
            score: Puntuación de relevancia entre 0.0 y 1.0.
        """
        self.title = title
        self.content = content
        self.url = url
        self.source = source
        self.date = date or datetime.now()
        self.score = score
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el resultado a un diccionario serializable.
        
        Útil para almacenamiento, caché o transmisión de datos.
        
        Returns:
            Dict[str, Any]: Representación del resultado como diccionario.
        """
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "source": self.source,
            "date": self.date.isoformat() if self.date else None,
            "score": self.score
        }

class SearchError(Exception):
    """
    Excepción personalizada para errores de búsqueda.
    
    Proporciona información específica sobre problemas durante
    las operaciones de búsqueda.
    """
    pass

class SearchSystem:
    """
    Sistema de búsqueda que utiliza Tavily para obtener información en tiempo real.
    
    Implementa funcionalidades para realizar búsquedas web con diferentes enfoques
    (general, académico, económico, noticias), además de manejar caché para optimizar
    rendimiento y evitar búsquedas duplicadas.
    
    Attributes:
        tavily_client: Cliente de la API de Tavily.
        cache: Diccionario que almacena resultados previos.
        is_configured: Indica si el sistema está correctamente configurado.
    """
    
    def __init__(self):
        """
        Inicializa el sistema de búsqueda y verifica la configuración.
        
        Comprueba la disponibilidad de Tavily y la presencia de la API key,
        inicializando el cliente si todas las condiciones son favorables.
        """
        self.tavily_client = None
        self.cache = {}  # Cache para evitar búsquedas repetidas
        self.is_configured = False
        
        # Verificar disponibilidad de Tavily como dependencia
        if not TAVILY_AVAILABLE:
            logger.error("❌ Tavily no está instalado. Ejecuta: pip install tavily-python")
            return
            
        # Verificar presencia y validez de la API key
        tavily_key = os.getenv("TAVILY_API_KEY")
        if not tavily_key or tavily_key == "your_tavily_api_key_here":
            logger.warning("⚠️ TAVILY_API_KEY no configurada en .env")
            logger.warning("   Obtén una en: https://tavily.com/")
            return
            
        # Inicializar cliente de Tavily
        try:
            self.tavily_client = TavilyClient(api_key=tavily_key)
            self.is_configured = True
            logger.info("✅ Sistema de búsqueda Tavily configurado correctamente")
        except Exception as e:
            logger.error(f"❌ Error al inicializar Tavily: {e}")
                
    def search(self, query: str, source_type: str = "general", 
               max_results: int = 5) -> List[SearchResult]:
        """
        Busca información usando la API de Tavily.
        
        Realiza búsquedas en tiempo real según el tipo de fuente especificado,
        adaptando la consulta para obtener resultados más relevantes. Implementa
        caché para optimizar consultas repetidas.
        
        Args:
            query: Consulta o término de búsqueda.
            source_type: Tipo de fuente a priorizar ("general", "academic", "economic", "news").
            max_results: Número máximo de resultados a devolver.
            
        Returns:
            Lista de objetos SearchResult con los resultados encontrados.
            
        Raises:
            SearchError: Si el sistema no está configurado o hay problemas en la búsqueda.
        """
        # Verificar que el sistema está correctamente configurado
        if not self.is_configured:
            raise SearchError(
                "Sistema de búsqueda no configurado. "
                "Necesitas:\n"
                "1. Instalar tavily: pip install tavily-python\n"
                "2. Configurar TAVILY_API_KEY en .env\n"
                "3. Obtener API key gratis en: https://tavily.com/"
            )
        
        # Verificar si la búsqueda ya está en caché
        cache_key = f"{query}_{source_type}_{max_results}"
        if cache_key in self.cache:
            logger.info(f"📦 Usando cache para: {query}")
            return self.cache[cache_key]
        
        # Realizar búsqueda en tiempo real
        try:
            logger.info(f"🔍 Buscando con Tavily: {query}")
            
            # Configurar parámetros según el tipo de búsqueda
            search_params = {
                "query": query,
                "max_results": max_results
            }
            
            # Adaptar la consulta según el tipo de fuente requerido
            if source_type == "academic":
                search_params["query"] = f"scientific study research {query}"
            elif source_type == "economic":
                search_params["query"] = f"economic impact analysis {query}"
            elif source_type == "news":
                search_params["query"] = f"latest news {query}"
                
            # Ejecutar búsqueda a través de la API
            tavily_results = self.tavily_client.search(**search_params)
            
            # Procesar y estructurar los resultados obtenidos
            results = []
            for r in tavily_results.get('results', []):
                # Extraer fecha de publicación si está disponible
                date = None
                if 'published_date' in r:
                    try:
                        date = datetime.fromisoformat(r['published_date'])
                    except:
                        date = datetime.now()
                
                # Crear objeto SearchResult con los datos del resultado
                results.append(SearchResult(
                    title=r.get('title', 'Sin título'),
                    content=r.get('content', r.get('snippet', '')),
                    url=r.get('url', ''),
                    source=self._extract_source_from_url(r.get('url', '')),
                    date=date,
                    score=r.get('score', 0.8)
                ))
            
            # Verificar si se encontraron resultados
            if not results:
                logger.warning(f"⚠️ No se encontraron resultados para: {query}")
                return []
            
            # Guardar resultados en caché para futuras consultas
            self.cache[cache_key] = results
            logger.info(f"✅ Encontrados {len(results)} resultados")
            
            return results
            
        except Exception as e:
            error_msg = f"Error al buscar '{query}': {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise SearchError(error_msg)
    
    def _extract_source_from_url(self, url: str) -> str:
        """
        Extrae el nombre de la fuente desde la URL.
        
        Analiza la URL para obtener el dominio principal y lo formatea
        como nombre de fuente legible.
        
        Args:
            url: URL completa del recurso.
            
        Returns:
            Nombre de la fuente extraído y formateado.
        """
        if not url:
            return "Fuente desconocida"
            
        # Extraer y formatear el dominio
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            # Limpiar www. y extraer dominio principal
            domain = domain.replace('www.', '')
            domain = domain.split('.')[0]
            return domain.capitalize()
        except:
            return "Web"
    
    def test_connection(self) -> bool:
        """
        Prueba si la conexión con Tavily funciona correctamente.
        
        Realiza una búsqueda de prueba simple para verificar la 
        conectividad y configuración del sistema.
        
        Returns:
            True si la conexión funciona, False en caso contrario.
        """
        if not self.is_configured:
            return False
            
        try:
            # Realizar una búsqueda simple de prueba
            results = self.search("test", max_results=1)
            return True
        except:
            return False
    
    def clear_cache(self):
        """
        Limpia el caché de búsquedas.
        
        Elimina todos los resultados almacenados en caché para 
        forzar nuevas búsquedas en tiempo real.
        """
        self.cache.clear()
        logger.info("🧹 Cache limpiado")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Devuelve el estado actual del sistema de búsqueda.
        
        Proporciona información sobre la configuración, disponibilidad
        y capacidades del sistema.
        
        Returns:
            Diccionario con información de estado del sistema.
        """
        return {
            "configured": self.is_configured,          # Si está configurado correctamente
            "tavily_available": TAVILY_AVAILABLE,      # Si la biblioteca está instalada
            "api_key_set": bool(os.getenv("TAVILY_API_KEY")),  # Si hay API key configurada
            "cache_size": len(self.cache),             # Tamaño del caché actual
            "can_search": self.is_configured and TAVILY_AVAILABLE  # Si puede realizar búsquedas
        }

# Función de prueba autónoma
def test_search_system():
    """
    Prueba el sistema de búsqueda con consultas reales.
    
    Esta función ejecuta una serie de búsquedas de prueba para
    verificar el funcionamiento del sistema y mostrar sus capacidades.
    Útil para depuración y demostración del sistema.
    """
    print("="*60)
    print("PRUEBA DEL SISTEMA DE BÚSQUEDA REAL")
    print("="*60)
    
    # Inicializar sistema de búsqueda
    search = SearchSystem()
    
    # Mostrar estado actual del sistema
    status = search.get_status()
    print("\n📊 Estado del sistema:")
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Verificar si el sistema puede realizar búsquedas
    if not status["can_search"]:
        print("\n❌ El sistema no puede realizar búsquedas")
        print("\nPara habilitar las búsquedas:")
        print("1. Obtén una API key gratis en: https://tavily.com/")
        print("2. Agrégala a tu archivo .env:")
        print("   TAVILY_API_KEY=tu_api_key_aqui")
        return
    
    # Consultas de prueba para diferentes dominios
    test_queries = [
        "beneficios cognitivos del café",
        "impacto económico del trabajo remoto",
        "efectos del ejercicio en la salud mental"
    ]
    
    print("\n🔍 Realizando búsquedas de prueba...")
    
    # Ejecutar y mostrar resultados de cada consulta
    for query in test_queries:
        print(f"\n📝 Buscando: '{query}'")
        print("-"*60)
        
        try:
            results = search.search(query, max_results=2)
            
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.title}")
                print(f"   📰 Fuente: {result.source}")
                print(f"   ⭐ Score: {result.score:.2f}")
                print(f"   📝 Contenido: {result.content[:150]}...")
                print(f"   🔗 URL: {result.url}")
                
        except SearchError as e:
            print(f"❌ Error: {e}")
            break
    
    print("\n" + "="*60)
    
# Punto de entrada para ejecución directa del módulo
if __name__ == "__main__":
    test_search_system()