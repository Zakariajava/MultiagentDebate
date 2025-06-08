"""
Agentes investigadores especializados para el sistema de debates.

Este módulo implementa los agentes investigadores especializados (SlaveAgents) que
forman parte de los equipos de debate. Cada agente tiene un rol especializado
(científico, económico, histórico, etc.) y trabaja para un equipo (PRO o CONTRA),
buscando información relevante desde su perspectiva específica.

El sistema incluye mecanismos para buscar información en internet, evaluar su
relevancia, credibilidad y sesgo, y seleccionar los mejores fragmentos para
respaldar los argumentos del equipo.

VERSIÓN CORREGIDA con rate limiting y campos faltantes
"""
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Imports de tu proyecto
from ..config import AgentRole, Config
from ..utils.search import SearchSystem, SearchResult, SearchError
from ..utils.github_models import get_agent_model

logger = logging.getLogger(__name__)

@dataclass
class Fragment:
    """
    Fragmento de información evaluado por un agente investigador.
    
    Representa una pieza de información encontrada durante la investigación,
    evaluada según múltiples criterios (relevancia, credibilidad, sesgo).
    Incluye metadatos como la fuente, URL, puntajes de evaluación y
    razonamiento del agente.
    
    Attributes:
        content (str): Contenido textual del fragmento.
        title (str): Título del documento o artículo.
        url (str): URL de la fuente.
        source (str): Nombre de la fuente (sitio web, periódico, etc.).
        relevance_score (float): Puntuación de relevancia (0-1).
        credibility_score (float): Puntuación de credibilidad de la fuente (0-1).
        bias_score (float): Nivel de sesgo (0=neutral, 1=muy sesgado).
        final_score (float): Puntuación final combinada.
        agent_reasoning (str): Justificación del agente para seleccionar este fragmento.
        search_query (str): Consulta que generó este resultado.
        timestamp (datetime): Momento en que se encontró el fragmento.
        supervisor_team (str): Equipo del supervisor (PRO/CONTRA).
        supervisor_position (str): Posición que defiende el equipo.
    """
    content: str
    title: str
    url: str
    source: str
    relevance_score: float  # 0-1: qué tan relevante es para el tema
    credibility_score: float  # 0-1: qué tan creíble es la fuente
    bias_score: float  # 0-1: qué tan sesgado está (0=neutral, 1=muy sesgado)
    final_score: float  # Score final combinado
    agent_reasoning: str  # Por qué el agente eligió este fragmento
    search_query: str  # Query que encontró este fragmento
    timestamp: datetime
    
    # Campos para referencia al supervisor
    supervisor_team: str = ""
    supervisor_position: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el fragmento a un diccionario serializable.
        
        Útil para almacenamiento, transmisión o visualización de datos.
        
        Returns:
            Dict[str, Any]: Representación del fragmento como diccionario.
        """
        return {
            "content": self.content,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "relevance_score": self.relevance_score,
            "credibility_score": self.credibility_score,
            "bias_score": self.bias_score,
            "final_score": self.final_score,
            "agent_reasoning": self.agent_reasoning,
            "search_query": self.search_query,
            "timestamp": self.timestamp.isoformat(),
            "supervisor_team": self.supervisor_team,
            "supervisor_position": self.supervisor_position
        }

class SlaveAgent:
    """
    Agente investigador especializado para el sistema de debates.
    
    Cada agente tiene una especialidad (científico, económico, histórico, etc.)
    y pertenece a un equipo (PRO o CONTRA). Su trabajo principal es buscar
    información relevante desde su perspectiva especializada, evaluarla según
    criterios de calidad, y proporcionar los mejores fragmentos para respaldar
    los argumentos del equipo.
    
    El agente implementa todo el ciclo de investigación:
    1. Generación de consultas especializadas
    2. Búsqueda de información
    3. Evaluación de resultados
    4. Selección de los mejores fragmentos
    
    CORRECCIONES:
    - Rate limiting con pausas entre búsquedas
    - Mejor manejo de timeouts
    - Validación mejorada de argumentos
    """
    
    def __init__(self, role: AgentRole, team: str, agent_id: str = None):
        """
        Inicializa un nuevo agente investigador especializado.
        
        Configura el agente con su rol específico, equipo, sistemas de búsqueda
        y modelo de lenguaje, además de inicializar su estado interno.
        
        Args:
            role (AgentRole): Rol especializado del agente (científico, económico, etc.).
            team (str): Equipo al que pertenece ("pro" o "contra").
            agent_id (str, optional): Identificador único del agente. Si no se proporciona,
                se genera automáticamente a partir del rol y equipo.
        """
        self.role = role
        self.team = team.lower()
        self.agent_id = agent_id or f"{team}_{role.value}"
        
        # Sistemas externos
        self.search_system = SearchSystem()
        self.llm = get_agent_model(temperature=0.3)  # Temperatura baja para consistencia
        
        # Estado interno
        self.fragments_found = []  # Fragmentos encontrados en la investigación
        self.queries_used = []     # Consultas utilizadas previamente
        self.search_history = []   # Historial de búsquedas realizadas
        
        # Configuración de especialidad según el rol
        self.specialty_config = self._configure_specialty()
        
        # Contadores para rate limiting
        self.api_calls_count = 0  # Número total de llamadas a APIs
        self.last_api_call = None # Timestamp de la última llamada a API
        
        logger.info(f"🤖 Agente {self.agent_id} ({self.role.value}) inicializado para equipo {self.team}")
    
    def _configure_specialty(self) -> Dict[str, Any]:
        """
        Configura la especialización del agente según su rol.
        
        Define los tipos de búsqueda, palabras clave, fuentes preferidas,
        indicadores de sesgo y plantillas de consulta específicas para cada
        especialidad.
        
        Returns:
            Dict[str, Any]: Configuración completa de la especialidad.
        """
        specialties = {
            AgentRole.CIENTIFICO: {
                "search_types": ["academic", "general"],
                "keywords": ["estudio", "investigación", "científico", "evidencia", "datos", "análisis"],
                "preferred_sources": ["pubmed", "scholar", "universidad", "instituto", "journal"],
                "bias_indicators": ["promoción", "marketing", "opinión personal", "blog personal"],
                "query_templates": [
                    "estudios científicos {topic}",
                    "investigación médica {topic}",
                    "evidencia científica {topic}",
                    "datos clínicos {topic}",
                    "metaanálisis {topic}"
                ]
            },
            AgentRole.ECONOMICO: {
                "search_types": ["economic", "general"],
                "keywords": ["económico", "financiero", "costo", "beneficio", "impacto", "mercado"],
                "preferred_sources": ["banco", "ministerio", "estadística", "económico", "financiero"],
                "bias_indicators": ["promoción comercial", "publicidad", "venta"],
                "query_templates": [
                    "impacto económico {topic}",
                    "análisis financiero {topic}",
                    "costos beneficios {topic}",
                    "mercado {topic}",
                    "estadísticas económicas {topic}"
                ]
            },
            AgentRole.HISTORICO: {
                "search_types": ["general"],
                "keywords": ["histórico", "historia", "antecedentes", "origen", "evolución", "pasado"],
                "preferred_sources": ["museo", "archivo", "historia", "académico", "universidad"],
                "bias_indicators": ["revisión histórica", "interpretación moderna"],
                "query_templates": [
                    "historia {topic}",
                    "antecedentes históricos {topic}",
                    "evolución {topic}",
                    "origen {topic}",
                    "contexto histórico {topic}"
                ]
            },
            AgentRole.REFUTADOR: {
                "search_types": ["general"],
                "keywords": ["crítica", "problema", "limitación", "contraargumento", "debilidad"],
                "preferred_sources": ["crítica", "análisis", "revisión", "oposición"],
                "bias_indicators": ["defensa absoluta", "sin críticas"],
                "query_templates": [
                    "críticas {topic}",
                    "problemas {topic}",
                    "limitaciones {topic}",
                    "contraargumentos {topic}",
                    "desventajas {topic}"
                ]
            },
            AgentRole.PSICOLOGICO: {
                "search_types": ["general"],
                "keywords": ["psicológico", "mental", "emocional", "comportamiento", "social", "cognitivo"],
                "preferred_sources": ["psicología", "mental", "comportamiento", "social"],
                "bias_indicators": ["autoayuda", "coaching", "opinión personal"],
                "query_templates": [
                    "efectos psicológicos {topic}",
                    "impacto mental {topic}",
                    "comportamiento {topic}",
                    "aspectos sociales {topic}",
                    "efectos cognitivos {topic}"
                ]
            }
        }
        
        return specialties.get(self.role, specialties[AgentRole.CIENTIFICO])
    
    def _wait_for_rate_limit(self):
        """
        Implementa el manejo inteligente de rate limiting para llamadas a APIs.
        
        Introduce pausas dinámicas entre llamadas a APIs para evitar alcanzar
        límites de frecuencia, con base en el tiempo transcurrido desde la última
        llamada y un intervalo mínimo configurado.
        """
        current_time = time.time()
        
        if self.last_api_call:
            time_since_last = current_time - self.last_api_call
            min_delay = 1.5  # Mínimo 1.5 segundos entre llamadas
            
            if time_since_last < min_delay:
                wait_time = min_delay - time_since_last
                logger.info(f"⏳ {self.agent_id} esperando {wait_time:.1f}s para rate limiting...")
                time.sleep(wait_time)
        
        self.last_api_call = time.time()
        self.api_calls_count += 1
    
    def generate_search_queries(self, task: str, context: str = "") -> List[str]:
        """
        Genera consultas de búsqueda especializadas según el rol del agente.
        
        Utiliza el modelo de lenguaje para crear consultas adaptadas a la
        especialidad del agente, enfocadas en encontrar información relevante
        para su equipo y evitando la duplicación con búsquedas previas.
        
        Args:
            task (str): Tarea principal de investigación.
            context (str, optional): Contexto adicional del debate.
            
        Returns:
            List[str]: Lista de consultas de búsqueda especializadas.
        """
        # Esperar para rate limiting antes de llamar al LLM
        self._wait_for_rate_limit()
        
        # Prompt para el LLM que genera las queries
        prompt = f"""
Eres un agente investigador especializado en {self.role.value} del equipo {self.team}.

TAREA: {task}
CONTEXTO: {context}

Tu especialidad se enfoca en: {', '.join(self.specialty_config['keywords'])}

Genera {Config.MAX_QUERIES_PER_AGENT} queries de búsqueda específicas que:
1. Se enfoquen en tu especialidad ({self.role.value})
2. Busquen evidencia para el equipo {self.team}
3. Sean específicas y técnicas
4. Usen términos relevantes a tu campo
5. Eviten duplicados con queries anteriores

QUERIES ANTERIORES (no repetir):
{self.queries_used[-10:]}  # Últimas 10 queries para evitar repetir

Formato de respuesta:
1. query específica aquí
2. otra query específica aquí
3. etc.

Solo responde con las queries numeradas, sin explicaciones adicionales.
"""
        
        try:
            response = self.llm.invoke(prompt)
            queries = []
            
            # Procesar respuesta para extraer las consultas
            for line in response.content.strip().split('\n'):
                if line.strip() and any(char.isdigit() for char in line[:3]):
                    query = line.split('.', 1)[1].strip() if '.' in line else line.strip()
                    if query and len(query) > 10:  # Filtrar queries muy cortas
                        queries.append(query)
            
            # Fallback si el LLM no generó queries válidas
            if not queries:
                queries = self._generate_fallback_queries(task)
            
            # Guardar queries usadas
            self.queries_used.extend(queries)
            
            logger.info(f"🔍 Agente {self.agent_id} generó {len(queries)} queries")
            return queries[:Config.MAX_QUERIES_PER_AGENT]
            
        except Exception as e:
            logger.error(f"❌ Error generando queries para {self.agent_id}: {e}")
            return self._generate_fallback_queries(task)
    
    def _generate_fallback_queries(self, task: str) -> List[str]:
        """
        Genera consultas de respaldo usando plantillas predefinidas.
        
        Utiliza plantillas específicas del rol para crear consultas de búsqueda
        cuando el modelo de lenguaje falla en generarlas.
        
        Args:
            task (str): Tarea de investigación.
            
        Returns:
            List[str]: Lista de consultas de búsqueda generadas a partir de plantillas.
        """
        topic = task.lower()
        queries = []
        
        for template in self.specialty_config["query_templates"]:
            query = template.format(topic=topic)
            queries.append(query)
        
        return queries[:Config.MAX_QUERIES_PER_AGENT]
    
    def search_and_evaluate(self, queries: List[str]) -> List[Fragment]:
        """
        Realiza búsquedas y evalúa cada resultado para convertirlo en fragmentos.
        
        Ejecuta las consultas de búsqueda, procesa los resultados obtenidos,
        evalúa su calidad mediante el modelo de lenguaje, y selecciona los
        mejores fragmentos, implementando pausas entre operaciones para evitar
        rate limiting.
        
        Args:
            queries (List[str]): Lista de consultas de búsqueda a ejecutar.
            
        Returns:
            List[Fragment]: Lista de fragmentos evaluados y filtrados por calidad.
        """
        all_fragments = []
        
        for i, query in enumerate(queries):
            try:
                logger.info(f"🔍 {self.agent_id} buscando: '{query}'")
                
                # Pausa entre búsquedas (excepto la primera) para evitar rate limiting
                if i > 0:
                    pause_time = 2 + (i * 0.5)  # Pausa progresiva: 2s, 2.5s, 3s...
                    logger.info(f"⏳ Pausa de {pause_time}s antes de siguiente búsqueda...")
                    time.sleep(pause_time)
                
                # Determinar tipo de búsqueda según la especialidad
                search_type = self.specialty_config["search_types"][0]
                
                # Realizar búsqueda
                results = self.search_system.search(
                    query=query,
                    source_type=search_type,
                    max_results=Config.MAX_RESULTS_PER_QUERY
                )
                
                # Procesar y evaluar cada resultado con pausas entre evaluaciones
                for j, result in enumerate(results):
                    if j > 0:
                        time.sleep(1)  # 1 segundo entre evaluaciones LLM
                    
                    fragment = self._evaluate_result(result, query)
                    if fragment and fragment.final_score >= Config.MIN_FRAGMENT_SCORE:
                        all_fragments.append(fragment)
                
                # Guardar historial de búsqueda
                self.search_history.append({
                    "query": query,
                    "results_count": len(results),
                    "timestamp": datetime.now()
                })
                
            except SearchError as e:
                logger.warning(f"⚠️ Error en búsqueda '{query}': {e}")
                continue
            except Exception as e:
                logger.error(f"❌ Error inesperado en búsqueda '{query}': {e}")
                continue
        
        # Procesar los fragmentos: eliminar duplicados y ordenar por score
        unique_fragments = self._remove_duplicates(all_fragments)
        best_fragments = sorted(unique_fragments, key=lambda f: f.final_score, reverse=True)
        
        logger.info(f"✅ {self.agent_id} encontró {len(best_fragments)} fragmentos válidos")
        return best_fragments[:Config.MAX_FRAGMENTS_PER_AGENT]
    
    def _evaluate_result(self, result: SearchResult, query: str) -> Optional[Fragment]:
        """
        Evalúa un resultado de búsqueda y lo convierte en fragmento evaluado.
        
        Analiza la calidad del resultado según criterios de relevancia,
        credibilidad y sesgo, utilizando el modelo de lenguaje para obtener
        una evaluación experta desde la perspectiva del rol especializado.
        
        Args:
            result (SearchResult): Resultado de búsqueda a evaluar.
            query (str): Consulta que generó este resultado.
            
        Returns:
            Optional[Fragment]: Fragmento evaluado si supera los criterios de calidad,
                None en caso contrario.
        """
        try:
            # Validación básica del resultado
            if not result.content or len(result.content.strip()) < 50:
                logger.warning(f"⚠️ Resultado muy corto o vacío: {result.title}")
                return None
            
            # Rate limiting para evaluación
            self._wait_for_rate_limit()
            
            # Prompt para evaluación del fragmento
            evaluation_prompt = f"""
Eres un experto en {self.role.value} evaluando información para el equipo {self.team}.

FRAGMENTO A EVALUAR:
Título: {result.title}
Fuente: {result.source}
Contenido: {result.content[:500]}...
URL: {result.url}

Evalúa este fragmento en 3 aspectos (responde solo con números 0.0-1.0):

1. RELEVANCIA (0.0-1.0): ¿Qué tan relevante es para {self.role.value} y útil para el equipo {self.team}?
2. CREDIBILIDAD (0.0-1.0): ¿Qué tan confiable es la fuente? (académico=1.0, blog personal=0.3)
3. SESGO (0.0-1.0): ¿Qué tan sesgado está? (0.0=neutral, 1.0=muy sesgado hacia una posición)

Después explica brevemente por qué elegiste estos scores.

Formato:
RELEVANCIA: 0.X
CREDIBILIDAD: 0.X
SESGO: 0.X
RAZONAMIENTO: explicación breve
"""
            
            response = self.llm.invoke(evaluation_prompt)
            scores = self._parse_evaluation(response.content)
            
            if not scores:
                logger.warning(f"⚠️ No se pudieron parsear scores para: {result.title}")
                return None
            
            # Calcular score final
            final_score = self._calculate_final_score(
                scores["relevancia"],
                scores["credibilidad"], 
                scores["sesgo"]
            )
            
            # Validación de score mínimo
            if final_score < Config.MIN_FRAGMENT_SCORE:
                logger.debug(f"📉 Fragment descartado por score bajo: {final_score:.2f}")
                return None
            
            # Crear fragmento evaluado
            return Fragment(
                content=result.content,
                title=result.title,
                url=result.url,
                source=result.source,
                relevance_score=scores["relevancia"],
                credibility_score=scores["credibilidad"],
                bias_score=scores["sesgo"],
                final_score=final_score,
                agent_reasoning=scores.get("razonamiento", ""),
                search_query=query,
                timestamp=datetime.now(),
                supervisor_team="",  # Se asigna después por el supervisor
                supervisor_position=""  # Se asigna después por el supervisor
            )
            
        except Exception as e:
            logger.error(f"❌ Error evaluando fragmento: {e}")
            return None
    
    def _parse_evaluation(self, evaluation_text: str) -> Optional[Dict[str, Any]]:
        """
        Parsea la respuesta de evaluación del modelo de lenguaje.
        
        Extrae las puntuaciones y el razonamiento del texto de evaluación
        generado por el modelo, validando que los valores estén dentro del
        rango esperado.
        
        Args:
            evaluation_text (str): Texto de evaluación del modelo.
            
        Returns:
            Optional[Dict[str, Any]]: Diccionario con puntuaciones y razonamiento,
                o None si no se pueden extraer los datos necesarios.
        """
        try:
            scores = {}
            lines = evaluation_text.strip().split('\n')
            
            # Extraer puntuaciones y razonamiento del texto
            for line in lines:
                line = line.strip()
                if 'RELEVANCIA:' in line:
                    value = line.split(':')[1].strip()
                    scores["relevancia"] = float(value)
                elif 'CREDIBILIDAD:' in line:
                    value = line.split(':')[1].strip()
                    scores["credibilidad"] = float(value)
                elif 'SESGO:' in line:
                    value = line.split(':')[1].strip()
                    scores["sesgo"] = float(value)
                elif 'RAZONAMIENTO:' in line:
                    scores["razonamiento"] = line.split(':', 1)[1].strip()
            
            # Validar que estén todas las puntuaciones requeridas
            required_keys = ["relevancia", "credibilidad", "sesgo"]
            if all(key in scores for key in required_keys):
                # Validar que las puntuaciones estén en el rango correcto
                for key in required_keys:
                    if not (0.0 <= scores[key] <= 1.0):
                        logger.warning(f"⚠️ Score fuera de rango para {key}: {scores[key]}")
                        return None
                return scores
            
            logger.warning(f"⚠️ Faltan scores requeridos. Encontrados: {list(scores.keys())}")
            return None
            
        except (ValueError, IndexError) as e:
            logger.warning(f"⚠️ Error parseando evaluación: {e}")
            return None
    
    def _calculate_final_score(self, relevance: float, credibility: float, bias: float) -> float:
        """
        Calcula la puntuación final combinada del fragmento.
        
        Aplica una fórmula ponderada que combina relevancia, credibilidad y sesgo,
        donde relevancia y credibilidad tienen mayor peso, y el sesgo se invierte
        (menor sesgo = mejor puntuación).
        
        Formula: (relevancia * 0.4) + (credibilidad * 0.4) + ((1-sesgo) * 0.2)
        
        Args:
            relevance (float): Puntuación de relevancia (0-1).
            credibility (float): Puntuación de credibilidad (0-1).
            bias (float): Puntuación de sesgo (0-1, donde 0=neutral).
            
        Returns:
            float: Puntuación final entre 0.0 y 1.0.
        """
        final = (relevance * 0.4) + (credibility * 0.4) + ((1 - bias) * 0.2)
        return min(max(final, 0.0), 1.0)  # Asegurar que esté entre 0-1
    
    def _remove_duplicates(self, fragments: List[Fragment]) -> List[Fragment]:
        """
        Elimina fragmentos duplicados o muy similares de la lista.
        
        Identifica duplicados tanto por URL como por similitud de contenido,
        manteniendo siempre el fragmento de mayor puntuación cuando hay duplicados.
        
        Args:
            fragments (List[Fragment]): Lista de fragmentos a procesar.
            
        Returns:
            List[Fragment]: Lista de fragmentos sin duplicados.
        """
        unique_fragments = []
        seen_urls = set()
        
        for fragment in fragments:
            # Omitir si ya vimos esta URL
            if fragment.url in seen_urls:
                continue
            
            # Verificar similitud de contenido con fragmentos existentes
            is_duplicate = False
            for existing in unique_fragments:
                if self._content_similarity(fragment.content, existing.content) > Config.SIMILARITY_THRESHOLD:
                    # Mantener el fragmento de mayor puntuación
                    if fragment.final_score > existing.final_score:
                        unique_fragments.remove(existing)
                        break
                    else:
                        is_duplicate = True
                        break
            
            # Agregar el fragmento si no es duplicado o si es mejor que el existente
            if not is_duplicate:
                unique_fragments.append(fragment)
                seen_urls.add(fragment.url)
        
        return unique_fragments
    
    def _content_similarity(self, content1: str, content2: str) -> float:
        """
        Calcula el índice de similitud entre dos textos.
        
        Utiliza el coeficiente de Jaccard (intersección/unión de conjuntos de palabras)
        para determinar la similitud entre los contenidos.
        
        Args:
            content1 (str): Primer texto a comparar.
            content2 (str): Segundo texto a comparar.
            
        Returns:
            float: Índice de similitud entre 0.0 (totalmente diferentes) y 
                1.0 (idénticos en términos de palabras).
        """
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def research(self, task: str, context: str = "") -> List[Fragment]:
        """
        Método principal que realiza el proceso completo de investigación.
        
        Ejecuta la secuencia completa de investigación: generación de consultas,
        búsqueda de información, evaluación de resultados y selección de los
        mejores fragmentos, con manejo de errores robusto.
        
        Args:
            task (str): Tarea principal de investigación.
            context (str, optional): Contexto adicional del debate.
            
        Returns:
            List[Fragment]: Lista de los mejores fragmentos encontrados y evaluados.
        """
        logger.info(f"🚀 {self.agent_id} iniciando investigación: {task}")
        
        try:
            # Validación de entrada
            if not task or len(task.strip()) < 10:
                logger.warning(f"⚠️ Tarea muy corta para {self.agent_id}: '{task}'")
                return []
            
            # 1. Generar queries especializadas
            queries = self.generate_search_queries(task, context)
            
            if not queries:
                logger.warning(f"⚠️ No se generaron queries para {self.agent_id}")
                return []
            
            # 2. Buscar y evaluar resultados
            fragments = self.search_and_evaluate(queries)
            
            # 3. Guardar resultados en el estado interno
            self.fragments_found = fragments
            
            logger.info(f"✅ {self.agent_id} completó investigación: {len(fragments)} fragmentos")
            return fragments
            
        except Exception as e:
            logger.error(f"❌ Error en investigación de {self.agent_id}: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """
        Devuelve el estado actual detallado del agente.
        
        Proporciona información completa sobre el agente, sus actividades,
        estadísticas y resultados para monitoreo y depuración.
        
        Returns:
            Dict[str, Any]: Diccionario con el estado completo del agente.
        """
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "team": self.team,
            "queries_used": len(self.queries_used),
            "fragments_found": len(self.fragments_found),
            "searches_performed": len(self.search_history),
            "api_calls_made": self.api_calls_count,
            "avg_fragment_score": sum(f.final_score for f in self.fragments_found) / len(self.fragments_found) if self.fragments_found else 0,
            "specialty_keywords": self.specialty_config["keywords"],
            "last_search_time": self.search_history[-1]["timestamp"].isoformat() if self.search_history else None
        }