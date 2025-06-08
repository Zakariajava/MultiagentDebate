"""
Sistema completo de debates usando LangGraph.

Este módulo implementa el orquestador principal del sistema de debates, utilizando
LangGraph para definir y gestionar el flujo completo del debate desde la configuración
inicial hasta la determinación del ganador. Coordina todos los componentes del sistema,
incluyendo supervisores, agentes, búsquedas, argumentación y evaluación.

El sistema está diseñado como un grafo direccionado donde cada nodo representa una
fase del debate (configuración, investigación, argumentación, evaluación, cierre),
con flujos condicionales para determinar cuándo continuar con nuevas rondas o finalizar.

VERSIÓN CORREGIDA: Sin objetos en estado, sin focus_areas, con rate limiting
"""
import logging
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Project imports
from .SupervisorAgent import SupervisorAgent, ArgumentStrategy, Argument
from .SlaveAgent import Fragment
from ..config import Config, DebatePhase

logger = logging.getLogger(__name__)

class DebateState(TypedDict):
    """
    Estado completo del debate que se pasa entre nodos del grafo.
    
    Define la estructura de datos que mantiene todo el estado del debate,
    incluyendo configuración, argumentos, fragmentos, resultados y metadatos.
    Diseñado para ser serializable y transmisible entre nodos del grafo.
    
    CORREGIDO: Sin objetos complejos para evitar problemas de serialización.
    Los supervisores se mantienen como atributos de clase en el orquestador,
    no en el estado, y los fragmentos y argumentos se serializan como diccionarios.
    """
    
    # Configuración básica del debate
    topic: str                  # Tema del debate
    pro_position: str           # Posición que defiende el equipo PRO
    contra_position: str        # Posición que defiende el equipo CONTRA
    current_round: int          # Ronda actual del debate
    max_rounds: int             # Número máximo de rondas
    debate_phase: str           # Fase actual (investigación, argumentación, etc.)
    
    # Referencias a supervisores (sólo IDs, no objetos)
    pro_supervisor_id: str      # ID del supervisor PRO
    contra_supervisor_id: str   # ID del supervisor CONTRA
    
    # Historial de argumentos (como diccionarios serializables)
    pro_arguments: List[Dict[str, Any]]     # Argumentos del equipo PRO
    contra_arguments: List[Dict[str, Any]]  # Argumentos del equipo CONTRA
    
    # Fragmentos de evidencia recolectados (como diccionarios)
    pro_fragments: List[Dict[str, Any]]     # Fragmentos del equipo PRO
    contra_fragments: List[Dict[str, Any]]  # Fragmentos del equipo CONTRA
    
    # Estado actual de la argumentación
    last_pro_argument: Optional[str]     # Último argumento PRO (contenido)
    last_contra_argument: Optional[str]  # Último argumento CONTRA (contenido)
    
    # Resultados finales del debate
    debate_summary: Optional[str]               # Resumen generado del debate
    winner: Optional[str]                       # Ganador determinado
    final_scores: Optional[Dict[str, float]]    # Puntuaciones finales
    
    # Metadatos
    start_time: str             # Timestamp de inicio del debate
    current_time: str           # Timestamp actual
    errors: List[str]           # Registro de errores ocurridos

@dataclass
class DebateConfig:
    """
    Configuración del debate utilizada para iniciar una nueva sesión.
    
    Contiene los parámetros fundamentales necesarios para configurar
    un debate, como el tema, las posiciones de cada equipo y límites
    de tiempo y rondas.
    
    VERSIÓN SIMPLIFICADA: Eliminado el parámetro focus_areas por ser
    redundante con los roles de los agentes.
    """
    topic: str                 # Tema central del debate
    pro_position: str          # Posición que defenderá el equipo PRO
    contra_position: str       # Posición que defenderá el equipo CONTRA
    max_rounds: int = 3        # Número máximo de rondas de debate
    timeout_minutes: int = 10  # Tiempo máximo para completar el debate
    # focus_areas: List[str] = None  # ❌ ELIMINADO - redundante con roles

class DebateOrchestrator:
    """
    Orquestador principal del debate usando LangGraph.
    
    Esta clase implementa el sistema central que coordina todo el flujo del debate,
    desde la configuración inicial hasta la determinación del ganador. Utiliza
    LangGraph para definir un grafo de estados que representa las diferentes
    fases del debate y las transiciones entre ellas.
    
    Maneja el flujo completo:
    1. Configuración inicial de supervisores y estado
    2. Investigación por equipos PRO y CONTRA
    3. Rondas de argumentación y respuestas
    4. Evaluación continua y determinación de continuidad
    5. Finalización y resumen del debate
    
    CORRECCIONES:
    - Supervisores como atributos de clase, NO en el estado (para serialización)
    - Sin focus_areas (redundante con roles de agentes)
    - Rate limiting mejorado (pausas estratégicas)
    - Mejor manejo de errores (fallbacks y valores por defecto)
    """
    
    def __init__(self):
        """
        Inicializa el orquestador creando el grafo de LangGraph.
        
        Configura todos los nodos, aristas y flujos condicionales que definen
        el proceso completo del debate, además de inicializar el sistema de
        almacenamiento para checkpoints del estado.
        """
        self.graph = None
        self.memory = MemorySaver()  # Para checkpoint del estado
        
        # Mantener supervisores como atributos de clase, NO en el estado
        # para evitar problemas de serialización
        self.supervisor_pro = None
        self.supervisor_contra = None
        
        # Construir el grafo de flujo
        self._build_graph()
        
        logger.info("🎯 DebateOrchestrator inicializado con LangGraph")
    
    def _build_graph(self):
        """
        Construye el grafo de LangGraph con todos los nodos y flujos.
        
        Define la estructura completa del grafo, incluyendo:
        - Nodos para cada fase del debate
        - Aristas que conectan las fases en secuencia
        - Condiciones para bifurcaciones (continuar o finalizar)
        - Puntos de entrada y salida
        """
        # Crear el grafo con el tipo de estado definido
        builder = StateGraph(DebateState)
        
        # === NODOS DEL GRAFO ===
        
        # Nodo de inicio - configura el debate
        builder.add_node("setup_debate", self._setup_debate_node)
        
        # Nodos de investigación inicial
        builder.add_node("research_pro", self._research_pro_node)
        builder.add_node("research_contra", self._research_contra_node)
        
        # Nodos de argumentación
        builder.add_node("pro_argument", self._pro_argument_node)
        builder.add_node("contra_argument", self._contra_argument_node)
        
        # Nodos de control de flujo
        builder.add_node("evaluate_round", self._evaluate_round_node)
        
        # Nodo de cierre
        builder.add_node("finalize_debate", self._finalize_debate_node)
        
        # === FLUJO DEL GRAFO ===
        
        # Punto de entrada
        builder.set_entry_point("setup_debate")
        
        # Desde setup, ir a investigación secuencial (evitar concurrencia)
        builder.add_edge("setup_debate", "research_pro")
        builder.add_edge("research_pro", "research_contra")
        
        # Desde investigación, al primer argumento PRO
        builder.add_edge("research_contra", "pro_argument")
        
        # Flujo de argumentación: PRO → CONTRA → evaluación
        builder.add_edge("pro_argument", "contra_argument")
        builder.add_edge("contra_argument", "evaluate_round")
        
        # Desde evaluación, decidir continuar o finalizar
        builder.add_conditional_edges(
            "evaluate_round",
            self._should_continue,
            {
                "continue": "pro_argument",  # Otra ronda
                "finish": "finalize_debate"  # Terminar debate
            }
        )
        
        # Finalización
        builder.add_edge("finalize_debate", END)
        
        # Compilar el grafo con soporte para checkpoints
        self.graph = builder.compile(checkpointer=self.memory)
        
        logger.info("🏗️ Grafo de debate construido con éxito")
    
    def _setup_debate_node(self, state: DebateState) -> DebateState:
        """
        Nodo inicial: configura supervisores y estado del debate.
        
        Inicializa los supervisores de ambos equipos y establece
        el estado inicial del debate. Este es el primer nodo ejecutado
        en el flujo del grafo.
        
        Args:
            state: Estado inicial del debate.
            
        Returns:
            Estado actualizado con la configuración inicial.
        """
        logger.info("🚀 Iniciando configuración del debate")
        
        try:
            # Crear supervisores como atributos de la clase, NO en el estado
            # para evitar problemas de serialización
            self.supervisor_pro = SupervisorAgent(
                team="pro",
                position=state["pro_position"],
                supervisor_id="debate_pro"
            )
            
            self.supervisor_contra = SupervisorAgent(
                team="contra", 
                position=state["contra_position"],
                supervisor_id="debate_contra"
            )
            
            # Actualizar estado SIN objetos complejos
            state.update({
                "pro_supervisor_id": "debate_pro",
                "contra_supervisor_id": "debate_contra",
                "current_round": 0,
                "debate_phase": DebatePhase.INVESTIGACION_INICIAL.value,
                "pro_arguments": [],
                "contra_arguments": [],
                "pro_fragments": [],
                "contra_fragments": [],
                "start_time": datetime.now().isoformat(),
                "current_time": datetime.now().isoformat(),
                "errors": []
            })
            
            logger.info(f"✅ Debate configurado: {state['topic']}")
            logger.info(f"   🟢 PRO: {state['pro_position']}")
            logger.info(f"   🔴 CONTRA: {state['contra_position']}")
            
        except Exception as e:
            logger.error(f"❌ Error en setup_debate: {e}")
            state["errors"].append(f"Setup error: {str(e)}")
        
        return state
    
    def _research_pro_node(self, state: DebateState) -> DebateState:
        """
        Nodo de investigación del equipo PRO.
        
        Coordina al supervisor PRO para que orqueste la investigación
        de su equipo de agentes y recopile evidencia para apoyar su posición.
        
        Args:
            state: Estado actual del debate.
            
        Returns:
            Estado actualizado con los fragmentos de evidencia del equipo PRO.
        """
        logger.info("🔍 Equipo PRO iniciando investigación")
        
        try:
            # Verificar que el supervisor esté inicializado
            if not self.supervisor_pro:
                raise ValueError("Supervisor PRO no inicializado")
            
            # Definir tarea de investigación
            research_task = f"Investiga evidencia que apoye: {state['pro_position']}"
            
            # Pausa estratégica antes de investigación masiva
            import time
            time.sleep(3)
            
            # Coordinar investigación del equipo PRO
            fragments = self.supervisor_pro.orchestrate_research(
                task=research_task,
                context=f"Debate sobre: {state['topic']}"
            )
            
            # Convertir fragmentos a diccionarios para almacenarlos en el estado
            fragments_dict = [fragment.to_dict() for fragment in fragments]
            
            # Actualizar estado
            state["pro_fragments"] = fragments_dict
            state["current_time"] = datetime.now().isoformat()
            
            logger.info(f"✅ Investigación PRO completada: {len(fragments)} fragmentos")
            
        except Exception as e:
            logger.error(f"❌ Error en research_pro: {e}")
            state["errors"].append(f"Research PRO error: {str(e)}")
            state["pro_fragments"] = []  # Garantizar que existe la lista aunque sea vacía
        
        return state
    
    def _research_contra_node(self, state: DebateState) -> DebateState:
        """
        Nodo de investigación del equipo CONTRA.
        
        Coordina al supervisor CONTRA para que orqueste la investigación
        de su equipo de agentes y recopile evidencia para apoyar su posición.
        
        Args:
            state: Estado actual del debate.
            
        Returns:
            Estado actualizado con los fragmentos de evidencia del equipo CONTRA.
        """
        logger.info("🔍 Equipo CONTRA iniciando investigación")
        
        try:
            # Verificar que el supervisor esté inicializado
            if not self.supervisor_contra:
                raise ValueError("Supervisor CONTRA no inicializado")
            
            # Definir tarea de investigación
            research_task = f"Investiga evidencia que refute: {state['pro_position']}"
            
            # Pausa estratégica antes de investigación masiva
            import time
            time.sleep(3)
            
            # Coordinar investigación del equipo CONTRA
            fragments = self.supervisor_contra.orchestrate_research(
                task=research_task,
                context=f"Debate sobre: {state['topic']}"
            )
            
            # Convertir fragmentos a diccionarios para almacenarlos en el estado
            fragments_dict = [fragment.to_dict() for fragment in fragments]
            
            # Actualizar estado
            state["contra_fragments"] = fragments_dict
            state["current_time"] = datetime.now().isoformat()
            
            logger.info(f"✅ Investigación CONTRA completada: {len(fragments)} fragmentos")
            
        except Exception as e:
            logger.error(f"❌ Error en research_contra: {e}")
            state["errors"].append(f"Research CONTRA error: {str(e)}")
            state["contra_fragments"] = []  # Garantizar que existe la lista aunque sea vacía
        
        return state
    
    def _pro_argument_node(self, state: DebateState) -> DebateState:
        """
        Nodo de argumentación del equipo PRO.
        
        Genera un argumento para el equipo PRO utilizando los fragmentos recopilados
        y la estrategia apropiada según la ronda actual. En rondas posteriores a la
        primera, responde al último argumento del equipo CONTRA.
        
        Args:
            state: Estado actual del debate.
            
        Returns:
            Estado actualizado con el nuevo argumento del equipo PRO.
        """
        # Incrementar contador de rondas
        state["current_round"] += 1
        logger.info(f"💬 Equipo PRO argumentando (Ronda {state['current_round']})")
        
        try:
            # Verificar que el supervisor esté inicializado
            if not self.supervisor_pro:
                raise ValueError("Supervisor PRO no inicializado")
            
            # Reconstruir objetos Fragment desde los diccionarios en el estado
            fragments = self._rebuild_fragments_from_dicts(state["pro_fragments"])
            
            # Determinar estrategia según la ronda
            if state["current_round"] == 1:
                strategy = ArgumentStrategy.INITIAL_POSITION  # Primera posición
                opponent_arg = None
            else:
                strategy = ArgumentStrategy.COUNTER_ATTACK    # Contraataque
                opponent_arg = state.get("last_contra_argument")
            
            # Generar argumento
            argument = self.supervisor_pro.compose_argument(
                fragments=fragments,
                strategy=strategy,
                opponent_argument=opponent_arg
            )
            
            # Guardar en estado como diccionario
            argument_dict = argument.to_dict()
            state["pro_arguments"].append(argument_dict)
            state["last_pro_argument"] = argument.content
            state["current_time"] = datetime.now().isoformat()
            
            logger.info(f"✅ Argumento PRO completado (confianza: {argument.confidence_score:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Error en pro_argument: {e}")
            state["errors"].append(f"PRO argument error: {str(e)}")
            
            # Argumento fallback para evitar que se interrumpa el debate
            fallback_arg = {
                "content": f"El equipo PRO mantiene que {state['pro_position']}",
                "confidence_score": 0.6,
                "strategy": "fallback",
                "round_number": state["current_round"],
                "key_points": [],
                "supporting_fragments": [],
                "timestamp": datetime.now().isoformat()
            }
            state["pro_arguments"].append(fallback_arg)
            state["last_pro_argument"] = fallback_arg["content"]
        
        return state
    
    def _contra_argument_node(self, state: DebateState) -> DebateState:
        """
        Nodo de argumentación del equipo CONTRA.
        
        Genera un argumento para el equipo CONTRA utilizando los fragmentos 
        recopilados y respondiendo al último argumento del equipo PRO.
        
        Args:
            state: Estado actual del debate.
            
        Returns:
            Estado actualizado con el nuevo argumento del equipo CONTRA.
        """
        logger.info(f"💬 Equipo CONTRA argumentando (Ronda {state['current_round']})")
        
        try:
            # Verificar que el supervisor esté inicializado
            if not self.supervisor_contra:
                raise ValueError("Supervisor CONTRA no inicializado")
            
            # Reconstruir objetos Fragment desde los diccionarios en el estado
            fragments = self._rebuild_fragments_from_dicts(state["contra_fragments"])
            
            # Determinar estrategia
            strategy = ArgumentStrategy.COUNTER_ATTACK if state["current_round"] > 1 else ArgumentStrategy.INITIAL_POSITION
            opponent_arg = state.get("last_pro_argument")  # Siempre responde al último argumento PRO
            
            # Generar argumento
            argument = self.supervisor_contra.compose_argument(
                fragments=fragments,
                strategy=strategy, 
                opponent_argument=opponent_arg
            )
            
            # Guardar en estado como diccionario
            argument_dict = argument.to_dict()
            state["contra_arguments"].append(argument_dict)
            state["last_contra_argument"] = argument.content
            state["current_time"] = datetime.now().isoformat()
            
            logger.info(f"✅ Argumento CONTRA completado (confianza: {argument.confidence_score:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Error en contra_argument: {e}")
            state["errors"].append(f"CONTRA argument error: {str(e)}")
            
            # Argumento fallback para evitar que se interrumpa el debate
            fallback_arg = {
                "content": f"El equipo CONTRA sostiene que {state['contra_position']}",
                "confidence_score": 0.6,
                "strategy": "fallback",
                "round_number": state["current_round"],
                "key_points": [],
                "supporting_fragments": [],
                "timestamp": datetime.now().isoformat()
            }
            state["contra_arguments"].append(fallback_arg)
            state["last_contra_argument"] = fallback_arg["content"]
        
        return state
    
    def _evaluate_round_node(self, state: DebateState) -> DebateState:
        """
        Nodo de evaluación de ronda.
        
        Evalúa el estado actual del debate, actualiza la fase según el progreso,
        y registra las métricas de los argumentos generados. Este nodo prepara
        el estado para la decisión de continuar o finalizar.
        
        Args:
            state: Estado actual del debate.
            
        Returns:
            Estado actualizado con la evaluación de la ronda.
        """
        logger.info(f"📊 Evaluando ronda {state['current_round']}")
        
        try:
            # Actualizar fase del debate según el progreso
            if state["current_round"] >= state["max_rounds"]:
                state["debate_phase"] = DebatePhase.CIERRE.value
            elif state["current_round"] >= state["max_rounds"] - 1:
                state["debate_phase"] = DebatePhase.PROFUNDIZACION.value
            else:
                state["debate_phase"] = DebatePhase.ARGUMENTACION.value
            
            # Registrar métricas de confianza de los argumentos
            pro_confidence = 0
            contra_confidence = 0
            
            if state["pro_arguments"]:
                pro_confidence = state["pro_arguments"][-1]["confidence_score"]
            if state["contra_arguments"]:
                contra_confidence = state["contra_arguments"][-1]["confidence_score"]
            
            logger.info(f"📈 Confianzas actuales - PRO: {pro_confidence:.2f}, CONTRA: {contra_confidence:.2f}")
            
            # Actualizar timestamp
            state["current_time"] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"❌ Error en evaluate_round: {e}")
            state["errors"].append(f"Evaluation error: {str(e)}")
        
        return state
    
    def _should_continue(self, state: DebateState) -> str:
        """
        Decide si continuar el debate con otra ronda o finalizarlo.
        
        Evalúa múltiples criterios para determinar si el debate debe
        continuar a otra ronda o terminar, incluyendo límite de rondas,
        errores acumulados, calidad de argumentos y disponibilidad de evidencia.
        
        Args:
            state: Estado actual del debate.
            
        Returns:
            "continue" si se debe continuar con otra ronda,
            "finish" si se debe finalizar el debate.
        """
        # Verificar límite de rondas configurado
        if state["current_round"] >= state["max_rounds"]:
            logger.info(f"🏁 Límite de rondas alcanzado ({state['max_rounds']})")
            return "finish"
        
        # Verificar acumulación de errores críticos
        if len(state["errors"]) > 5:
            logger.warning("⚠️ Demasiados errores, finalizando debate")
            return "finish"
        
        # Verificar que se estén generando argumentos válidos
        if state["current_round"] > 1:
            if not state["pro_arguments"] or not state["contra_arguments"]:
                logger.warning("⚠️ No se están generando argumentos, finalizando")
                return "finish"
        
        # Verificar si hay evidencia suficiente para continuar
        if len(state["pro_fragments"]) < 2 and len(state["contra_fragments"]) < 2:
            logger.warning("⚠️ Evidencia insuficiente, finalizando debate")
            return "finish"
        
        # Si pasa todas las verificaciones, continuar
        logger.info(f"🔄 Continuando a ronda {state['current_round'] + 1}")
        return "continue"
    
    def _finalize_debate_node(self, state: DebateState) -> DebateState:
        """
        Nodo final: evalúa ganador y genera resumen del debate.
        
        Calcula las puntuaciones finales de cada equipo, determina
        el ganador según las métricas de confianza, y genera un
        resumen completo del debate.
        
        Args:
            state: Estado actual del debate.
            
        Returns:
            Estado finalizado con resultados y resumen.
        """
        logger.info("🏁 Finalizando debate y evaluando resultados")
        
        try:
            # Calcular puntuaciones finales de cada equipo
            pro_scores = [arg["confidence_score"] for arg in state["pro_arguments"]]
            contra_scores = [arg["confidence_score"] for arg in state["contra_arguments"]]
            
            # Calcular promedios (con manejo de listas vacías)
            pro_avg = sum(pro_scores) / len(pro_scores) if pro_scores else 0
            contra_avg = sum(contra_scores) / len(contra_scores) if contra_scores else 0
            
            # Determinar ganador según diferencia de puntuaciones
            if abs(pro_avg - contra_avg) < 0.1:
                winner = "empate"  # Diferencia mínima
            elif pro_avg > contra_avg:
                winner = "pro"     # PRO tiene mayor puntuación
            else:
                winner = "contra"  # CONTRA tiene mayor puntuación
            
            # Garantizar que winner no sea None (para serialización)
            if winner is None:
                winner = "no_determinado"
            
            # Generar resumen completo del debate
            summary = self._generate_debate_summary(state, pro_avg, contra_avg)
            
            # Actualizar estado final con resultados
            state.update({
                "winner": winner,  # Garantizado no None
                "final_scores": {
                    "pro_average": pro_avg,
                    "contra_average": contra_avg,
                    "pro_total_arguments": len(state["pro_arguments"]),
                    "contra_total_arguments": len(state["contra_arguments"])
                },
                "debate_summary": summary,
                "debate_phase": DebatePhase.CIERRE.value,
                "current_time": datetime.now().isoformat()
            })
            
            logger.info(f"🏆 Debate finalizado - Ganador: {winner}")
            logger.info(f"📊 Scores finales - PRO: {pro_avg:.2f}, CONTRA: {contra_avg:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Error finalizando debate: {e}")
            state["errors"].append(f"Finalization error: {str(e)}")
            
            # Valores por defecto seguros en caso de error
            state.update({
                "winner": "error",  # No None
                "final_scores": {"pro_average": 0, "contra_average": 0},
                "debate_summary": "Error en finalización del debate"
            })
        
        return state
    
    def _rebuild_fragments_from_dicts(self, fragments_dicts: List[Dict]) -> List[Fragment]:
        """
        Reconstruye objetos Fragment desde sus representaciones como diccionarios.
        
        Convierte los diccionarios almacenados en el estado del debate a
        objetos Fragment completos que pueden ser utilizados por los supervisores.
        
        Args:
            fragments_dicts: Lista de diccionarios con datos de fragmentos.
            
        Returns:
            Lista de objetos Fragment reconstruidos.
        """
        fragments = []
        for frag_dict in fragments_dicts:
            try:
                # Crear objeto Fragment con todos sus atributos
                fragment = Fragment(
                    content=frag_dict["content"],
                    title=frag_dict["title"],
                    url=frag_dict["url"],
                    source=frag_dict["source"],
                    relevance_score=frag_dict["relevance_score"],
                    credibility_score=frag_dict["credibility_score"],
                    bias_score=frag_dict["bias_score"],
                    final_score=frag_dict["final_score"],
                    agent_reasoning=frag_dict["agent_reasoning"],
                    search_query=frag_dict["search_query"],
                    timestamp=datetime.fromisoformat(frag_dict["timestamp"]),
                    supervisor_team=frag_dict.get("supervisor_team", ""),
                    supervisor_position=frag_dict.get("supervisor_position", "")
                )
                fragments.append(fragment)
            except Exception as e:
                logger.warning(f"⚠️ Error reconstruyendo fragmento: {e}")
                continue
        
        return fragments
    
    def _generate_debate_summary(self, state: DebateState, pro_avg: float, contra_avg: float) -> str:
        """
        Genera un resumen completo del debate.
        
        Crea un texto estructurado que resume el tema, posiciones,
        estadísticas, resultados y desarrollo del debate.
        
        Args:
            state: Estado completo del debate.
            pro_avg: Puntuación promedio del equipo PRO.
            contra_avg: Puntuación promedio del equipo CONTRA.
            
        Returns:
            Texto con el resumen completo del debate.
        """
        # Construir resumen estructurado
        summary = f"""
RESUMEN DEL DEBATE: {state['topic']}

POSICIONES:
🟢 PRO: {state['pro_position']}
🔴 CONTRA: {state['contra_position']}

ESTADÍSTICAS:
- Rondas completadas: {state['current_round']}
- Argumentos PRO: {len(state['pro_arguments'])}
- Argumentos CONTRA: {len(state['contra_arguments'])}
- Fragmentos PRO: {len(state['pro_fragments'])}
- Fragmentos CONTRA: {len(state['contra_fragments'])}

PUNTUACIONES:
- PRO promedio: {pro_avg:.2f}
- CONTRA promedio: {contra_avg:.2f}
- Ganador: {state.get('winner', 'No determinado')}

DURACIÓN:
- Inicio: {state['start_time']}
- Fin: {state['current_time']}
"""
        
        # Agregar información sobre errores si existen
        if state["errors"]:
            summary += f"\nERRORES ENCONTRADOS: {len(state['errors'])}"
        
        return summary.strip()
    
    def run_debate(self, config: DebateConfig) -> Dict[str, Any]:
        """
        Ejecuta un debate completo usando el grafo definido.
        
        Método principal para iniciar y ejecutar un debate completo,
        desde la configuración inicial hasta la determinación del ganador.
        
        Args:
            config: Configuración del debate a ejecutar.
            
        Returns:
            Estado final del debate con todos los resultados.
        """
        logger.info(f"🎯 Iniciando debate: {config.topic}")
        
        # Crear estado inicial sin objetos complejos
        initial_state = DebateState(
            topic=config.topic,
            pro_position=config.pro_position,
            contra_position=config.contra_position,
            current_round=0,
            max_rounds=config.max_rounds,
            debate_phase=DebatePhase.INVESTIGACION_INICIAL.value,
            pro_supervisor_id="",  # Se asignará en setup
            contra_supervisor_id="",  # Se asignará en setup
            pro_arguments=[],
            contra_arguments=[],
            pro_fragments=[],
            contra_fragments=[],
            last_pro_argument=None,
            last_contra_argument=None,
            debate_summary=None,
            winner=None,
            final_scores=None,
            start_time=datetime.now().isoformat(),
            current_time=datetime.now().isoformat(),
            errors=[]
        )
        
        try:
            # Ejecutar el grafo completo con el estado inicial
            final_state = self.graph.invoke(
                initial_state,
                config={"configurable": {"thread_id": f"debate_{datetime.now().timestamp()}"}}
            )
            
            logger.info("🎉 Debate completado exitosamente")
            return final_state
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando debate: {e}")
            initial_state["errors"].append(f"Execution error: {str(e)}")
            initial_state["winner"] = "error"  # Valor seguro
            return initial_state
    
    def get_graph_visualization(self) -> str:
        """
        Devuelve una representación visual del grafo como texto.
        
        Genera una visualización ASCII del grafo de debate,
        mostrando nodos y conexiones para fines didácticos.
        
        Returns:
            Representación visual del grafo como texto ASCII.
        """
        return """
🎯 GRAFO DEL SISTEMA DE DEBATES
                    
    [setup_debate]
           ↓
    [research_pro] → [research_contra]  
           ↓
    [pro_argument]
           ↓
    [contra_argument]
           ↓
    [evaluate_round]
           ↓
    ¿Continuar? ──→ [pro_argument] (bucle)
           ↓ No
    [finalize_debate]
           ↓
        [END]
"""