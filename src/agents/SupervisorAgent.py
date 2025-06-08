"""
Agentes supervisores que coordinan equipos de investigadores.

Este módulo implementa los supervisores del sistema de debates, que actúan como 
directores de equipo coordinando a múltiples agentes investigadores especializados.
Cada supervisor gestiona un equipo completo (PRO o CONTRA) y es responsable de 
orquestar la investigación, seleccionar la mejor evidencia, construir argumentos 
coherentes, y responder estratégicamente a los argumentos del equipo contrario.

VERSIÓN CORREGIDA: Sin focus_areas, con rate limiting, sin línea x basura
"""
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Imports del proyecto
from ..config import AgentRole, Config, DebatePhase
from ..utils.github_models import get_supervisor_pro_model, get_supervisor_contra_model
from .SlaveAgent import SlaveAgent, Fragment

logger = logging.getLogger(__name__)

@dataclass
class Argument:
    """
    Estructura de datos para un argumento construido por un supervisor.
    
    Encapsula toda la información relacionada con un argumento completo,
    incluyendo el contenido, puntos clave, evidencia de apoyo, nivel de confianza,
    estrategia utilizada y metadatos adicionales.
    
    Attributes:
        content (str): Texto completo del argumento.
        key_points (List[str]): Lista de puntos clave extraídos del argumento.
        supporting_fragments (List[Fragment]): Fragmentos de evidencia que respaldan el argumento.
        confidence_score (float): Nivel de confianza del supervisor en el argumento (0-1).
        strategy (str): Estrategia argumentativa utilizada (ofensiva, defensiva, contraataque).
        timestamp (datetime): Momento de creación del argumento.
        round_number (int): Número de ronda del debate.
        response_to (Optional[str]): Argumento contrario al que responde (si aplica).
    """
    content: str  # El argumento principal
    key_points: List[str]  # Puntos clave del argumento
    supporting_fragments: List[Fragment]  # Fragmentos que lo respaldan
    confidence_score: float  # Confianza del supervisor en el argumento (0-1)
    strategy: str  # Estrategia utilizada (ofensiva, defensiva, contraataque)
    timestamp: datetime
    round_number: int
    response_to: Optional[str] = None  # Si es respuesta a argumento contrario
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el argumento a un diccionario serializable.
        
        Esta función facilita la serialización del argumento para su
        almacenamiento o transmisión entre componentes del sistema.
        
        Returns:
            Dict[str, Any]: Representación del argumento como diccionario.
        """
        return {
            "content": self.content,
            "key_points": self.key_points,
            "supporting_fragments": [f.to_dict() for f in self.supporting_fragments],
            "confidence_score": self.confidence_score,
            "strategy": self.strategy,
            "timestamp": self.timestamp.isoformat(),
            "round_number": self.round_number,
            "response_to": self.response_to
        }

class ArgumentStrategy(Enum):
    """
    Enumeración de estrategias argumentativas disponibles.
    
    Define las diferentes estrategias que puede utilizar un supervisor
    para construir argumentos según la fase del debate y el contexto.
    Cada estrategia tiene un propósito específico y se utiliza en
    diferentes momentos del debate.
    """
    INITIAL_POSITION = "initial_position"  # Ronda inicial - establecer posición
    REINFORCEMENT = "reinforcement"  # Reforzar argumentos propios
    COUNTER_ATTACK = "counter_attack"  # Contraatacar argumentos rivales
    DEFENSIVE = "defensive"  # Defender posición ante ataques
    CLOSING = "closing"  # Argumento de cierre

class SupervisorAgent:
    """
    Supervisor que coordina un equipo de agentes investigadores.
    
    Esta clase implementa el "cerebro" de cada equipo de debate, coordinando
    a múltiples agentes especializados, seleccionando la mejor evidencia,
    construyendo argumentos persuasivos y adaptándose a los argumentos del
    equipo contrario. Cada supervisor gestiona todo el ciclo de vida de la
    argumentación para su equipo (PRO o CONTRA).
    
    Principales funciones:
    1. Coordina la investigación de sus agentes especializados
    2. Selecciona los mejores fragmentos encontrados
    3. Construye argumentos coherentes y persuasivos
    4. Responde estratégicamente a argumentos del equipo contrario
    
    CORRECCIONES:
    - Eliminado focus_areas (redundante con roles)
    - Rate limiting entre agentes
    - Línea x basura eliminada
    - Mejor validación de argumentos
    """
    
    def __init__(self, team: str, position: str, supervisor_id: str = None):
        """
        Inicializa un supervisor de equipo de debate.
        
        Configura el supervisor con su posición argumentativa, crea su equipo
        de agentes especializados y prepara los modelos de lenguaje adecuados
        según el equipo al que pertenece (PRO o CONTRA).
        
        Args:
            team (str): Equipo al que pertenece ("pro" o "contra").
            position (str): Posición argumentativa que defiende el equipo.
            supervisor_id (str, optional): Identificador único del supervisor.
                Si no se proporciona, se genera automáticamente.
        """
        self.team = team.lower()
        self.position = position
        self.supervisor_id = supervisor_id or f"supervisor_{team}"
        
        # Obtener el modelo correcto según el equipo
        if self.team == "pro":
            self.llm = get_supervisor_pro_model(temperature=0.7)
            logger.info(f"🧠 Supervisor PRO usando modelo optimizado para posiciones afirmativas")
        else:
            self.llm = get_supervisor_contra_model(temperature=0.7) 
            logger.info(f"🧠 Supervisor CONTRA usando modelo optimizado para posiciones críticas")
        
        # Crear equipo de agentes especializados
        self.agents = self._create_agent_team()
        
        # Estado del supervisor
        self.arguments_made = []
        self.fragments_bank = []  # Banco de todos los fragmentos recolectados
        self.opponent_arguments = []  # Argumentos del rival para analizar
        self.current_round = 0
        self.debate_context = ""
        
        # Contadores para rate limiting
        self.api_calls_count = 0
        self.last_api_call = None
        
        logger.info(f"🎯 Supervisor {self.supervisor_id} inicializado")
        logger.info(f"   📝 Posición: {self.position}")
        logger.info(f"   👥 Equipo: {len(self.agents)} agentes especializados")
    
    def _create_agent_team(self) -> List[SlaveAgent]:
        """
        Crea el equipo completo de agentes investigadores especializados.
        
        Instancia un agente para cada uno de los roles definidos en AgentRole,
        configurándolos con el equipo y supervisor correspondientes.
        
        Returns:
            List[SlaveAgent]: Lista de agentes investigadores inicializados.
        """
        agents = []
        
        for role in AgentRole:
            agent_id = f"{self.team}_{role.value}_{self.supervisor_id}"
            agent = SlaveAgent(role=role, team=self.team, agent_id=agent_id)
            agents.append(agent)
            logger.info(f"   👤 Agente {role.value} agregado al equipo {self.team}")
        
        return agents
    
    def _wait_for_rate_limit(self):
        """
        Implementa un manejo inteligente de rate limiting para APIs.
        
        Asegura que haya un intervalo mínimo entre llamadas a APIs para
        evitar errores de rate limiting, introduciendo pausas dinámicas
        cuando es necesario.
        """
        current_time = time.time()
        
        if self.last_api_call:
            time_since_last = current_time - self.last_api_call
            min_delay = 2.0  # Mínimo 2 segundos entre llamadas del supervisor
            
            if time_since_last < min_delay:
                wait_time = min_delay - time_since_last
                logger.info(f"⏳ {self.supervisor_id} esperando {wait_time:.1f}s para rate limiting...")
                time.sleep(wait_time)
        
        self.last_api_call = time.time()
        self.api_calls_count += 1
    
    def orchestrate_research(self, task: str, context: str = "") -> List[Fragment]:
        """
        Coordina la investigación de todo el equipo de agentes.
        
        Método principal que orquesta el proceso de investigación, distribuyendo
        tareas especializadas a cada agente, recolectando sus hallazgos, y
        seleccionando los mejores fragmentos para formar la base de evidencia
        del equipo.
        
        Args:
            task (str): Tarea principal de investigación.
            context (str, optional): Contexto adicional del debate.
            
        Returns:
            List[Fragment]: Lista consolidada de los mejores fragmentos seleccionados.
        """
        logger.info(f"🎬 {self.supervisor_id} coordinando investigación de equipo")
        logger.info(f"📋 Tarea: {task}")
        
        self.debate_context = context
        all_fragments = []
        
        # Coordinar cada agente según su especialidad
        for i, agent in enumerate(self.agents):
            logger.info(f"🤖 Coordinando agente {agent.role.value}...")
            
            try:
                # Pausa progresiva entre agentes para evitar rate limiting
                if i > 0:
                    pause_time = 3 + i  # 4s, 5s, 6s, 7s, 8s
                    logger.info(f"⏳ Pausa de {pause_time}s antes del siguiente agente...")
                    time.sleep(pause_time)
                
                # Personalizar la tarea según la especialidad del agente
                specialized_task = self._customize_task_for_agent(task, agent)
                
                # Investigación del agente
                agent_fragments = agent.research(specialized_task, context)
                
                # Agregar metadata del supervisor a los fragmentos
                for fragment in agent_fragments:
                    fragment.supervisor_team = self.team
                    fragment.supervisor_position = self.position
                
                all_fragments.extend(agent_fragments)
                
                logger.info(f"✅ Agente {agent.role.value}: {len(agent_fragments)} fragmentos")
                
            except Exception as e:
                logger.error(f"❌ Error con agente {agent.role.value}: {e}")
                continue
        
        # Consolidar y seleccionar los mejores fragmentos
        best_fragments = self._select_best_fragments(all_fragments, task)
        
        # Agregar al banco de fragmentos
        self.fragments_bank.extend(best_fragments)
        
        logger.info(f"🎯 Investigación completada: {len(best_fragments)} fragmentos seleccionados")
        return best_fragments
    
    def _customize_task_for_agent(self, base_task: str, agent: SlaveAgent) -> str:
        """
        Personaliza la tarea según la especialidad del agente.
        
        Adapta la tarea general para hacerla específica al rol y especialidad
        de cada agente, permitiendo búsquedas más enfocadas y relevantes.
        
        Args:
            base_task (str): Tarea base de investigación.
            agent (SlaveAgent): Agente al que se asignará la tarea.
            
        Returns:
            str: Tarea personalizada según la especialidad del agente.
        """
        role_customizations = {
            AgentRole.CIENTIFICO: f"Estudios científicos sobre: {base_task}",
            AgentRole.ECONOMICO: f"Análisis económico de: {base_task}", 
            AgentRole.HISTORICO: f"Historia y antecedentes de: {base_task}",
            AgentRole.REFUTADOR: f"Críticas y limitaciones de: {base_task}",
            AgentRole.PSICOLOGICO: f"Efectos psicológicos de: {base_task}"
        }
        
        customized = role_customizations.get(agent.role, base_task)

        # Agregar contexto del equipo de manera concisa
        if self.team == "pro":
            customized += f" (busca evidencia a favor)"
        else:
            customized += f" (busca evidencia en contra)"
        
        return customized
    
    def _select_best_fragments(self, all_fragments: List[Fragment], task: str) -> List[Fragment]:
        """
        Selecciona los mejores fragmentos de todos los recolectados.
        
        Utiliza el modelo de lenguaje para evaluar y seleccionar los fragmentos
        más relevantes y útiles para la posición del equipo, asegurando
        diversidad y complementariedad.
        
        Args:
            all_fragments (List[Fragment]): Todos los fragmentos recolectados.
            task (str): Tarea de investigación para contexto.
            
        Returns:
            List[Fragment]: Los mejores fragmentos seleccionados.
        """
        if not all_fragments:
            return []
        
        logger.info(f"🔍 Analizando {len(all_fragments)} fragmentos para seleccionar los mejores")
        
        # Rate limiting antes de llamada LLM
        self._wait_for_rate_limit()
        
        # Crear resumen de fragmentos para el prompt
        fragments_summary = ""
        for i, fragment in enumerate(all_fragments, 1):
            fragments_summary += f"\n{i}. [{fragment.source}] {fragment.title}\n"
            fragments_summary += f"   Score: {fragment.final_score:.2f} | Agente: {fragment.search_query}\n"
            fragments_summary += f"   Contenido: {fragment.content[:200]}...\n"
        
        # Prompt para selección de fragmentos
        selection_prompt = f"""
Eres el supervisor del equipo {self.team.upper()} defendiendo: "{self.position}"

TAREA: {task}

FRAGMENTOS DISPONIBLES:
{fragments_summary[:3000]}  # Limitar tamaño

Tu trabajo es seleccionar los {Config.MAX_FRAGMENTS_PER_AGENT} MEJORES fragmentos que:
1. Sean más útiles para {self.team.upper()} la posición "{self.position}"
2. Tengan evidencia sólida y creíble
3. Se complementen entre sí para formar un argumento fuerte
4. Cubran diferentes aspectos del tema

Responde SOLO con los números de los fragmentos seleccionados, separados por comas.
Ejemplo: 1, 3, 7, 12, 15

Números seleccionados:
"""
        
        try:
            response = self.llm.invoke(selection_prompt)
            selected_indices = self._parse_selection(response.content, len(all_fragments))
            
            # Obtener fragmentos seleccionados
            selected_fragments = []
            for idx in selected_indices:
                if 0 <= idx < len(all_fragments):
                    selected_fragments.append(all_fragments[idx])
            
            # Fallback: si no se pudieron parsear, usar los de mayor score
            if not selected_fragments:
                selected_fragments = sorted(all_fragments, 
                                          key=lambda f: f.final_score, 
                                          reverse=True)[:Config.MAX_FRAGMENTS_PER_AGENT]
            
            logger.info(f"✅ Seleccionados {len(selected_fragments)} fragmentos de {len(all_fragments)}")
            return selected_fragments
            
        except Exception as e:
            logger.error(f"❌ Error seleccionando fragmentos: {e}")
            # Fallback: usar los mejores por score
            return sorted(all_fragments, key=lambda f: f.final_score, reverse=True)[:Config.MAX_FRAGMENTS_PER_AGENT]
    
    def _parse_selection(self, response: str, max_fragments: int) -> List[int]:
        """
        Parsea la respuesta del LLM extrayendo los índices de fragmentos seleccionados.
        
        Procesa la respuesta textual del modelo para extraer los números de los
        fragmentos seleccionados, validando que estén dentro del rango válido.
        
        Args:
            response (str): Respuesta del modelo de lenguaje.
            max_fragments (int): Número máximo de fragmentos disponibles.
            
        Returns:
            List[int]: Lista de índices de los fragmentos seleccionados.
        """
        try:
            # Extraer números de la respuesta usando expresiones regulares
            import re
            numbers = re.findall(r'\b\d+\b', response)
            indices = []
            
            for num_str in numbers:
                num = int(num_str) - 1  # Convertir a índice 0-based
                if 0 <= num < max_fragments:
                    indices.append(num)
                
                if len(indices) >= Config.MAX_FRAGMENTS_PER_AGENT:
                    break
            
            return indices
            
        except Exception as e:
            logger.warning(f"⚠️ Error parseando selección: {e}")
            return []
    
    def compose_argument(self, fragments: List[Fragment], 
                        strategy: ArgumentStrategy = ArgumentStrategy.INITIAL_POSITION,
                        opponent_argument: str = None) -> Argument:
        """
        Construye un argumento coherente usando los fragmentos seleccionados.
        
        Este método principal genera un argumento persuasivo basado en la estrategia
        seleccionada, utilizando la evidencia disponible y, si corresponde, respondiendo
        al argumento del oponente.
        
        Args:
            fragments (List[Fragment]): Fragmentos de evidencia disponibles.
            strategy (ArgumentStrategy, optional): Estrategia de argumentación a utilizar.
                Por defecto, ArgumentStrategy.INITIAL_POSITION.
            opponent_argument (str, optional): Argumento del oponente a responder.
            
        Returns:
            Argument: Argumento completo construido.
        """
        logger.info(f"✍️ {self.supervisor_id} construyendo argumento con estrategia {strategy.value}")
        
        self.current_round += 1
        
        # Rate limiting antes de construcción
        self._wait_for_rate_limit()
        
        # Preparar contexto de fragmentos para el prompt
        evidence_context = ""
        for i, fragment in enumerate(fragments, 1):
            evidence_context += f"\nEvidencia {i}:\n"
            evidence_context += f"Fuente: {fragment.source}\n"
            evidence_context += f"Contenido: {fragment.content[:300]}...\n"
            evidence_context += f"Credibilidad: {fragment.credibility_score:.2f}\n"
            evidence_context += f"URL: {fragment.url}\n"
        
        # Construir prompt según la estrategia
        argument_prompt = self._build_argument_prompt(
            strategy, evidence_context, opponent_argument
        )
        
        try:
            response = self.llm.invoke(argument_prompt)
            argument_text = response.content.strip()
            
            # Validación de calidad del argumento
            if not self._validate_argument(argument_text):
                logger.warning(f"⚠️ Argumento generado no pasa validación, usando fallback")
                argument_text = self._create_fallback_argument_text(fragments, strategy)
            
            # Extraer puntos clave del argumento
            key_points = self._extract_key_points(argument_text)
            
            # Calcular confianza basada en la calidad de la evidencia
            confidence = self._calculate_confidence(fragments)
            
            argument = Argument(
                content=argument_text,
                key_points=key_points,
                supporting_fragments=fragments,
                confidence_score=confidence,
                strategy=strategy.value,
                timestamp=datetime.now(),
                round_number=self.current_round,
                response_to=opponent_argument if opponent_argument else None
            )
            
            # Guardar en historial
            self.arguments_made.append(argument)
            
            logger.info(f"✅ Argumento construido (confianza: {confidence:.2f})")
            return argument
            
        except Exception as e:
            logger.error(f"❌ Error construyendo argumento: {e}")
            # Fallback argument
            return self._create_fallback_argument(fragments, strategy)
    
    def _validate_argument(self, argument_text: str) -> bool:
        """
        Valida que un argumento generado tenga calidad mínima aceptable.
        
        Aplica criterios de calidad para asegurar que el argumento no sea
        demasiado corto, genérico o carente de sustancia.
        
        Args:
            argument_text (str): Texto del argumento a validar.
            
        Returns:
            bool: True si el argumento cumple los criterios de calidad, False en caso contrario.
        """
        if not argument_text or len(argument_text.strip()) < 100:
            return False
        
        # Verificar que no sea solo texto de plantilla genérico
        template_phrases = [
            "basándose en la evidencia disponible",
            "según los datos mostrados",
            "el equipo sostiene que"
        ]
        
        template_count = sum(1 for phrase in template_phrases if phrase in argument_text.lower())
        if template_count > 2:  # Demasiado contenido genérico
            return False
        
        # Verificar que tenga oraciones sustanciales
        sentences = argument_text.split('.')
        substantial_sentences = [s for s in sentences if len(s.strip()) > 20]
        
        return len(substantial_sentences) >= 3
    
    def _create_fallback_argument_text(self, fragments: List[Fragment], strategy: ArgumentStrategy) -> str:
        """
        Crea un texto de argumento de respaldo en caso de fallo.
        
        Genera un argumento predefinido pero coherente cuando la generación
        del modelo falla o no cumple con los criterios de calidad.
        
        Args:
            fragments (List[Fragment]): Fragmentos de evidencia disponibles.
            strategy (ArgumentStrategy): Estrategia que se intentaba utilizar.
            
        Returns:
            str: Texto del argumento de respaldo.
        """
        if not fragments:
            return f"El equipo {self.team} mantiene que {self.position}. Esta posición se basa en un análisis exhaustivo del tema."
        
        best_fragment = max(fragments, key=lambda f: f.final_score)
        
        return f"""El equipo {self.team} sostiene firmemente que {self.position}. 

La evidencia recopilada respalda esta posición. Particularmente destacamos información de {best_fragment.source}: {best_fragment.content[:200]}...

Con base en {len(fragments)} fuentes especializadas, consideramos que nuestros argumentos tienen fundamento sólido."""
    
    def _build_argument_prompt(self, strategy: ArgumentStrategy, 
                             evidence_context: str, opponent_argument: str = None) -> str:
        """
        Construye el prompt para generar argumentos según la estrategia seleccionada.
        
        Crea un prompt especializado para el modelo de lenguaje, adaptado a
        la estrategia de argumentación específica y al contexto actual del debate.
        
        Args:
            strategy (ArgumentStrategy): Estrategia de argumentación a utilizar.
            evidence_context (str): Contexto con la evidencia disponible.
            opponent_argument (str, optional): Argumento del oponente a responder.
            
        Returns:
            str: Prompt completo para el modelo de lenguaje.
        """
        base_context = f"""
Eres un experto debatiente del equipo {self.team.upper()}.

POSICIÓN DEL EQUIPO: {self.position}

EVIDENCIA DISPONIBLE:
{evidence_context[:2000]}  # Limitar tamaño

RONDA: {self.current_round}
ESTRATEGIA: {strategy.value}
"""
        
        if strategy == ArgumentStrategy.INITIAL_POSITION:
            return base_context + f"""
Construye un argumento inicial SÓLIDO que establezca claramente la posición del equipo {self.team.upper()}.

El argumento debe:
1. Presentar la posición de manera clara y convincente
2. Usar la evidencia disponible de manera estratégica
3. Ser persuasivo y bien estructurado
4. Tener entre 200-400 palabras
5. Incluir datos específicos y fuentes cuando sea posible

Escribe un argumento poderoso:
"""
        
        elif strategy == ArgumentStrategy.COUNTER_ATTACK:
            return base_context + f"""
ARGUMENTO DEL OPONENTE A REFUTAR:
{opponent_argument}

Construye un CONTRAATAQUE devastador que:
1. Identifique las debilidades del argumento oponente
2. Use tu evidencia para refutarlo directamente
3. Fortalezca tu propia posición
4. Sea incisivo pero profesional
5. Tenga entre 200-400 palabras

Refuta y contraataca:
"""
        
        elif strategy == ArgumentStrategy.DEFENSIVE:
            return base_context + f"""
ATAQUE RECIBIDO:
{opponent_argument}

Construye una DEFENSA sólida que:
1. Mantenga firme tu posición original
2. Responda a las críticas específicas
3. Use nueva evidencia para reforzar tu postura
4. Muestre por qué las objeciones no son válidas
5. Tenga entre 200-400 palabras

Defiende tu posición:
"""
        
        elif strategy == ArgumentStrategy.REINFORCEMENT:
            return base_context + f"""
Construye un argumento de REFUERZO que:
1. Amplíe y profundice tu posición anterior
2. Agregue nueva evidencia y perspectivas
3. Fortalezca los puntos más débiles
4. Anticipe posibles contraataques
5. Tenga entre 200-400 palabras

Refuerza tu posición:
"""
        
        else:  # CLOSING
            return base_context + f"""
Construye un argumento de CIERRE que:
1. Resuma los puntos más fuertes de tu posición
2. Muestre por qué tu equipo ha ganado el debate
3. Deje una impresión final poderosa
4. Sea conciso pero impactante
5. Tenga entre 150-300 palabras

Cierra con fuerza:
"""
    
    def _extract_key_points(self, argument_text: str) -> List[str]:
        """
        Extrae automáticamente los puntos clave de un argumento.
        
        Utiliza patrones de expresiones regulares para identificar puntos
        importantes en el texto, como enumeraciones, frases clave o 
        estructuras argumentativas comunes.
        
        Args:
            argument_text (str): Texto completo del argumento.
            
        Returns:
            List[str]: Lista de puntos clave extraídos (máximo 5).
        """
        # Usar expresiones regulares para buscar patrones estructurados
        import re
        
        # Patrones para identificar puntos clave en diferentes formatos
        patterns = [
            r'(?:^|\n)\s*(?:\d+\.|\•|\-)\s*([^.\n]+[.\n])',  # Enumeraciones y bullets
            r'(?:Primero|Segundo|Tercero|Además|Por último|Finalmente)[,:]?\s*([^.\n]+)',  # Conectores secuenciales
            r'(?:Es importante|Cabe destacar|Debemos considerar)[^.]*([^.\n]+)'  # Frases enfáticas
        ]
        
        key_points = []
        for pattern in patterns:
            matches = re.findall(pattern, argument_text, re.MULTILINE | re.IGNORECASE)
            key_points.extend([match.strip() for match in matches if len(match.strip()) > 20])
        
        # Si no encuentra patrones, usar las primeras oraciones relevantes
        if not key_points:
            sentences = argument_text.split('.')
            key_points = [s.strip() for s in sentences[:3] if len(s.strip()) > 20]
        
        return key_points[:5]  # Limitar a máximo 5 puntos clave
    
    def _calculate_confidence(self, fragments: List[Fragment]) -> float:
        """
        Calcula el nivel de confianza del supervisor en un argumento.
        
        Evalúa la calidad del argumento basándose en la calidad y cantidad
        de la evidencia disponible, así como en la diversidad de fuentes.
        
        Args:
            fragments (List[Fragment]): Fragmentos que apoyan el argumento.
            
        Returns:
            float: Puntuación de confianza entre 0.0 y 1.0.
        """
        if not fragments:
            return 0.5  # Confianza neutral si no hay evidencia
        
        # Promedio de scores de fragmentos (calidad)
        avg_score = sum(f.final_score for f in fragments) / len(fragments)
        
        # Factor por número de fragmentos (cantidad)
        quantity_factor = min(len(fragments) / Config.MAX_FRAGMENTS_PER_AGENT, 1.0)
        
        # Factor por diversidad de fuentes
        sources = set(f.source for f in fragments)
        diversity_factor = min(len(sources) / 3, 1.0)  # Máximo 3 fuentes diferentes
        
        # Ponderación: calidad (60%), cantidad (20%), diversidad (20%)
        confidence = (avg_score * 0.6) + (quantity_factor * 0.2) + (diversity_factor * 0.2)
        return min(max(confidence, 0.0), 1.0)  # Asegurar que esté entre 0 y 1
    
    def _create_fallback_argument(self, fragments: List[Fragment], 
                                strategy: ArgumentStrategy) -> Argument:
        """
        Crea un argumento completo de respaldo en caso de fallo.
        
        Construye un objeto Argument completo cuando la generación
        mediante el modelo de lenguaje ha fallado.
        
        Args:
            fragments (List[Fragment]): Fragmentos de evidencia disponibles.
            strategy (ArgumentStrategy): Estrategia que se intentaba utilizar.
            
        Returns:
            Argument: Argumento de respaldo completamente formado.
        """
        fallback_content = self._create_fallback_argument_text(fragments, strategy)
        
        return Argument(
            content=fallback_content,
            key_points=["Evidencia de fuentes especializadas", "Posición basada en datos"],
            supporting_fragments=fragments,
            confidence_score=0.6,
            strategy=strategy.value,
            timestamp=datetime.now(),
            round_number=self.current_round
        )
    
    def respond_to_opponent(self, opponent_argument: str, 
                          available_fragments: List[Fragment] = None) -> Argument:
        """
        Genera una respuesta argumentativa al argumento del oponente.
        
        Este método de alto nivel determina la mejor estrategia para
        responder, selecciona los fragmentos apropiados y construye
        un argumento que responda efectivamente al oponente.
        
        Args:
            opponent_argument (str): Argumento del equipo contrario.
            available_fragments (List[Fragment], optional): Fragmentos adicionales disponibles.
                Si no se proporcionan, se utilizan los del banco de fragmentos.
            
        Returns:
            Argument: Argumento de respuesta completo.
        """
        logger.info(f"🥊 {self.supervisor_id} respondiendo a argumento oponente")
        
        # Guardar argumento oponente para análisis futuro
        self.opponent_arguments.append({
            "content": opponent_argument,
            "round": self.current_round,
            "timestamp": datetime.now()
        })
        
        # Decidir estrategia de respuesta según análisis del argumento
        strategy = self._choose_response_strategy(opponent_argument)
        
        # Usar fragmentos disponibles o del banco
        fragments_to_use = available_fragments or self.fragments_bank[-Config.MAX_FRAGMENTS_PER_AGENT:]
        
        # Construir respuesta utilizando la estrategia elegida
        response = self.compose_argument(
            fragments=fragments_to_use,
            strategy=strategy,
            opponent_argument=opponent_argument
        )
        
        logger.info(f"✅ Respuesta construida con estrategia {strategy.value}")
        return response
    
    def _choose_response_strategy(self, opponent_argument: str) -> ArgumentStrategy:
        """
        Elige la mejor estrategia para responder al argumento del oponente.
        
        Analiza el contenido y tono del argumento oponente, así como el
        contexto actual del debate, para determinar la estrategia más eficaz.
        
        Args:
            opponent_argument (str): Argumento del oponente a analizar.
            
        Returns:
            ArgumentStrategy: Estrategia recomendada para la respuesta.
        """
        # Análisis simple del contenido del argumento
        argument_lower = opponent_argument.lower()
        
        # Si el oponente ataca directamente, contraatacar
        if any(word in argument_lower for word in ["falso", "incorrecto", "error", "refutar"]):
            return ArgumentStrategy.COUNTER_ATTACK
        
        # Si es el primer argumento del oponente, reforzar posición
        if len(self.opponent_arguments) <= 1:
            return ArgumentStrategy.REINFORCEMENT
        
        # Si estamos en rondas tardías, defender
        if self.current_round >= Config.MAX_ROUNDS() - 1:
            return ArgumentStrategy.DEFENSIVE
        
        # Por defecto, contraatacar
        return ArgumentStrategy.COUNTER_ATTACK
    
    def get_team_status(self) -> Dict[str, Any]:
        """
        Devuelve un informe completo del estado actual del equipo.
        
        Recopila estadísticas y métricas sobre el supervisor, agentes,
        argumentos, fragmentos y estado general para monitoreo y depuración.
        
        Returns:
            Dict[str, Any]: Diccionario con información detallada del estado del equipo.
        """
        return {
            "supervisor_id": self.supervisor_id,
            "team": self.team,
            "position": self.position,
            "current_round": self.current_round,
            "arguments_made": len(self.arguments_made),
            "fragments_in_bank": len(self.fragments_bank),
            "opponent_arguments_seen": len(self.opponent_arguments),
            "api_calls_made": self.api_calls_count,
            "agents_status": [
                {
                    "role": agent.role.value,
                    "fragments_found": len(agent.fragments_found),
                    "searches_performed": len(agent.search_history)
                } for agent in self.agents
            ],
            "last_confidence": self.arguments_made[-1].confidence_score if self.arguments_made else 0,
            "avg_fragment_score": sum(f.final_score for f in self.fragments_bank) / len(self.fragments_bank) if self.fragments_bank else 0
        }