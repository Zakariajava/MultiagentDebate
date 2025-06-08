"""
Sistema de Interfaz Web para Debates Autónomos con Inteligencia Artificial.

Este módulo implementa una interfaz web interactiva utilizando Streamlit que permite
a los usuarios configurar y ejecutar debates automatizados entre equipos de agentes
de IA especializados. La aplicación sigue el patrón MVC (Model-View-Controller) donde
Streamlit actúa como la vista, las funciones como controladores, y el sistema de
debates como el modelo.

Arquitectura del Sistema:
    - Frontend: Streamlit (Reactive Web Framework)
    - Backend: Sistema de debates con LangGraph
    - Patrón: Observer (Streamlit state management)
    - Persistencia: Session State (temporal)

Características Principales:
    - Configuración dinámica de debates mediante formularios reactivos
    - Visualización en tiempo real del progreso de debates
    - Exportación de resultados en múltiples formatos
    - Gestión de estado persistente durante la sesión
    - Interfaz responsive con diseño modular

Referencias Técnicas:
    - PEP 484: Type Hints para mejor documentación de API
    - Clean Architecture: Separación de responsabilidades
    - SOLID Principles: Single Responsibility aplicado a funciones
    - Observer Pattern: Para manejo de estado reactivo

Author: Sistema de Debates IA
Version: 1.0
License: Academic Use
"""

import streamlit as st
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
import json

# Configuración del path del proyecto para importaciones relativas
# Aplicando principio DRY (Don't Repeat Yourself) para path management
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importaciones del sistema de debates - Dependency Injection Pattern
from src.agents.debate_graph import DebateOrchestrator, DebateConfig
from src.config import Config
from system_validator import SystemValidator

# Configuración inicial de Streamlit - Front Controller Pattern
# Establece las propiedades globales de la aplicación web
st.set_page_config(
    page_title="🎭 Sistema de Debates con IA",  # SEO optimized title
    page_icon="🎯",                             # Browser tab icon
    layout="wide",                              # Responsive layout choice
    initial_sidebar_state="expanded"            # UX optimization
)

# Definición de estilos CSS personalizados - Separation of Concerns
# Implementa el principio de separación entre presentación y lógica
st.markdown("""
<style>
    /* Tarjeta principal del debate - Gradient design para engagement visual */
    .debate-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    
    /* Estilo para argumentos PRO - Color psychology: azul = confianza */
    .pro-argument {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #00ff00;  /* Indicador visual de posición */
        margin: 10px 0;
    }
    
    /* Estilo para argumentos CONTRA - Color psychology: rosa/naranja = energía */
    .contra-argument {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #ff0000;  /* Indicador visual de oposición */
        margin: 10px 0;
    }
    
    /* Personalización de barra de progreso de Streamlit */
    .stProgress .st-bo {
        background-color: #667eea;
    }
    
    /* Tarjetas de métricas - Material Design inspiration */
    .metric-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state() -> None:
    """
    Inicializa el estado de sesión de Streamlit con valores por defecto.
    
    Implementa el patrón Singleton para el estado de la aplicación, asegurando
    que cada variable de estado se inicialice una sola vez por sesión de usuario.
    
    Estado Gestionado:
        - debate_running (bool): Flag de ejecución de debate activo
        - debate_result (Optional[Dict]): Resultados del último debate ejecutado
        - debate_history (List[Dict]): Historial de debates de la sesión
        - current_debate_id (Optional[str]): Identificador único del debate actual
    
    Design Pattern:
        Lazy Initialization - Los valores solo se establecen si no existen
        
    Complexity:
        Tiempo: O(1) - Operaciones de verificación y asignación constantes
        Espacio: O(1) - Almacenamiento de referencias de estado
        
    Side Effects:
        Modifica st.session_state (estado global de Streamlit)
    """
    # Patrón de inicialización condicional para evitar sobrescritura
    if 'debate_running' not in st.session_state:
        st.session_state.debate_running = False
    
    if 'debate_result' not in st.session_state:
        st.session_state.debate_result = None
    
    if 'debate_history' not in st.session_state:
        st.session_state.debate_history = []
    
    if 'current_debate_id' not in st.session_state:
        st.session_state.current_debate_id = None


def validate_system() -> bool:
    """
    Valida la configuración del sistema antes de permitir debates.
    
    Implementa el patrón Fail-Fast para detectar errores de configuración
    temprano en el ciclo de vida de la aplicación, siguiendo principios
    de programación defensiva.
    
    Returns:
        bool: True si el sistema está correctamente configurado
        
    Raises:
        SystemExit: Termina la aplicación si la validación falla
        
    Design Patterns:
        - Fail-Fast: Detección temprana de errores
        - Guard Clause: Validación de precondiciones
        
    Error Handling:
        Utiliza Streamlit's error display y st.stop() para control de flujo
        
    Side Effects:
        - Puede mostrar mensajes de error en la UI
        - Puede terminar la ejecución de la aplicación
    """
    # Instanciación del validador - Dependency Injection
    validator = SystemValidator()
    
    # Validación rápida del sistema con manejo de excepciones
    try:
        # Asegurar que la configuración esté cargada
        Config.ensure_loaded()
        return True
    except Exception as e:
        # Error handling con feedback inmediato al usuario
        st.error(f"❌ Error en configuración: {e}")
        st.stop()  # Fail-fast: detener ejecución si el sistema no está listo


def sidebar_configuration() -> Dict[str, Union[str, int]]:
    """
    Genera la configuración del debate mediante la barra lateral interactiva.
    
    Implementa el patrón Strategy para diferentes tipos de configuración de debates,
    permitiendo tanto temas predefinidos como configuración personalizada. Utiliza
    el patrón Template Method para la estructura de configuración.
    
    Returns:
        Dict[str, Union[str, int]]: Diccionario con la configuración del debate
            - topic (str): Tema del debate
            - pro_position (str): Posición del equipo PRO
            - contra_position (str): Posición del equipo CONTRA
            - max_rounds (int): Número máximo de rondas
            - timeout_minutes (int): Tiempo límite en minutos
    
    UI/UX Design:
        - Progressive Disclosure: Configuración avanzada colapsada
        - Smart Defaults: Valores predeterminados basados en mejores prácticas
        - Immediate Feedback: Visualización del estado del sistema
        
    Complexity:
        Tiempo: O(1) - Operaciones de UI constantes
        Espacio: O(1) - Almacenamiento de configuración constante
    """
    # Header de la barra lateral con diseño de información jerárquica
    st.sidebar.header("⚙️ Configuración del Debate")
    
    # Definición de temas predefinidos - Strategy Pattern
    # Cada tema implementa una estrategia específica de debate
    predefined_topics: Dict[str, Dict[str, str]] = {
        "Personalizado": {"topic": "", "pro": "", "contra": ""},
        "Inteligencia Artificial": {
            "topic": "Impacto de la IA en el empleo",
            "pro": "La IA creará más empleos de los que destruirá",
            "contra": "La IA causará desempleo masivo y desigualdad"
        },
        "Trabajo Remoto": {
            "topic": "Futuro del trabajo remoto",
            "pro": "El trabajo remoto es más productivo y beneficioso",
            "contra": "El trabajo presencial es esencial para la colaboración"
        },
        "Energía": {
            "topic": "Transición energética",
            "pro": "Las energías renovables son viables económicamente",
            "contra": "Los combustibles fósiles siguen siendo necesarios"
        },
        "Educación": {
            "topic": "Educación online vs presencial",
            "pro": "La educación online es más accesible y efectiva",
            "contra": "La educación presencial ofrece mejor desarrollo integral"
        }
    }
    
    # Selector de tema con patrón de selección estratégica
    selected_topic = st.sidebar.selectbox(
        "🎯 Tema del debate:",
        list(predefined_topics.keys())
    )
    
    # Lógica condicional para configuración personalizada vs predefinida
    # Aplicación del principio Open/Closed - abierto para extensión
    if selected_topic == "Personalizado":
        # Configuración manual - máxima flexibilidad
        topic = st.sidebar.text_input("📝 Tema del debate:")
        pro_position = st.sidebar.text_area("🟢 Posición PRO:")
        contra_position = st.sidebar.text_area("🔴 Posición CONTRA:")
    else:
        # Configuración basada en plantilla - eficiencia y consistencia
        topic_data = predefined_topics[selected_topic]
        topic = st.sidebar.text_input("📝 Tema del debate:", value=topic_data["topic"])
        pro_position = st.sidebar.text_area("🟢 Posición PRO:", value=topic_data["pro"])
        contra_position = st.sidebar.text_area("🔴 Posición CONTRA:", value=topic_data["contra"])
    
    # Configuración avanzada - Progressive Disclosure Pattern
    st.sidebar.subheader("🔧 Configuración Avanzada")
    
    # Controles deslizantes con rangos basados en investigación empírica
    max_rounds = st.sidebar.slider("🔄 Número de rondas:", 1, 5, 3)
    timeout_minutes = st.sidebar.slider("⏱️ Timeout (minutos):", 5, 30, 15)
    
    # Información del estado del sistema - Transparency Principle
    st.sidebar.subheader("📊 Estado del Sistema")
    st.sidebar.info(f"""
    **Configuración actual:**
    - Agentes por equipo: {Config.AGENTS_PER_TEAM()}
    - Fragmentos por agente: {Config.MAX_FRAGMENTS_PER_AGENT}
    - Queries por agente: {Config.MAX_QUERIES_PER_AGENT}
    - Debug mode: {Config.DEBUG_MODE()}
    """)
    
    # Retorno de configuración estructurada - Data Transfer Object Pattern
    return {
        "topic": topic,
        "pro_position": pro_position,
        "contra_position": contra_position,
        "max_rounds": max_rounds,
        "timeout_minutes": timeout_minutes
    }


def display_main_header() -> None:
    """
    Renderiza el header principal de la aplicación con diseño branded.
    
    Implementa principios de Visual Hierarchy y Brand Identity para crear
    una primera impresión profesional. Utiliza HTML embebido para mayor
    control sobre el diseño visual.
    
    Design Principles:
        - Visual Hierarchy: Título prominente seguido de descripción
        - Brand Consistency: Uso de emojis y colores corporativos
        - Accessibility: Contraste adecuado y estructura semántica
        
    Side Effects:
        Renderiza contenido HTML en la interfaz de Streamlit
    """
    # Renderizado de header con HTML personalizado - Template Pattern
    st.markdown("""
    <div class="debate-card">
        <h1>🎭 Sistema de Debates con IA</h1>
        <p>Dos equipos de IA investigan y debaten sobre cualquier tema usando evidencia real</p>
    </div>
    """, unsafe_allow_html=True)


def validate_debate_config(config: Dict[str, Union[str, int]]) -> List[str]:
    """
    Valida la configuración del debate aplicando reglas de negocio.
    
    Implementa el patrón Specification para validación de reglas de negocio,
    asegurando que la configuración cumpla con los requisitos mínimos para
    un debate efectivo.
    
    Args:
        config (Dict[str, Union[str, int]]): Configuración del debate a validar
            Estructura esperada:
            - topic (str): Tema del debate
            - pro_position (str): Posición PRO
            - contra_position (str): Posición CONTRA
            - max_rounds (int): Número de rondas
            - timeout_minutes (int): Timeout en minutos
    
    Returns:
        List[str]: Lista de errores de validación. Lista vacía si es válida.
        
    Validation Rules:
        - Tema: Mínimo 10 caracteres (suficiente contexto)
        - Posición PRO: Mínimo 20 caracteres (argumento substantivo)
        - Posición CONTRA: Mínimo 20 caracteres (argumento substantivo)
        
    Design Pattern:
        Specification Pattern - Cada regla es una especificación independiente
        
    Complexity:
        Tiempo: O(n) donde n es el número de campos a validar
        Espacio: O(e) donde e es el número de errores encontrados
    """
    # Lista de errores - Collector Pattern
    errors: List[str] = []
    
    # Validación del tema - Business Rule: Contexto suficiente
    if not config["topic"] or len(config["topic"].strip()) < 10:
        errors.append("El tema debe tener al menos 10 caracteres")
    
    # Validación de posición PRO - Business Rule: Argumento substantivo
    if not config["pro_position"] or len(config["pro_position"].strip()) < 20:
        errors.append("La posición PRO debe tener al menos 20 caracteres")
    
    # Validación de posición CONTRA - Business Rule: Contra-argumento substantivo
    if not config["contra_position"] or len(config["contra_position"].strip()) < 20:
        errors.append("La posición CONTRA debe tener al menos 20 caracteres")
    
    return errors


def create_debate_preview(config: Dict[str, Union[str, int]]) -> None:
    """
    Genera una vista previa visual del debate configurado.
    
    Implementa el patrón Preview para permitir a los usuarios revisar
    su configuración antes de la ejecución. Utiliza diseño de dos columnas
    para mostrar la naturaleza adversarial del debate.
    
    Args:
        config (Dict[str, Union[str, int]]): Configuración del debate
        
    UI/UX Design:
        - Split Layout: Visualización clara de posiciones opuestas
        - Color Coding: Verde para PRO, Rojo para CONTRA
        - Information Architecture: Jerarquía clara de información
        
    Visual Psychology:
        - Simetría para balance visual
        - Colores contrastantes para distinción clara
        - Tipografía jerárquica para escaneabilidad
        
    Side Effects:
        Renderiza contenido HTML y Markdown en Streamlit
    """
    # Layout en dos columnas para representar la naturaleza dual del debate
    col1, col2 = st.columns(2)
    
    # Columna izquierda - Equipo PRO (color psychology: verde = positivo)
    with col1:
        st.markdown(f"""
        <div class="pro-argument">
            <h4>🟢 Equipo PRO</h4>
            <p><strong>Posición:</strong> {config['pro_position']}</p>
            <small>Defenderá esta posición con evidencia científica, económica, histórica, psicológica y análisis crítico</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Columna derecha - Equipo CONTRA (color psychology: rojo = oposición)
    with col2:
        st.markdown(f"""
        <div class="contra-argument">
            <h4>🔴 Equipo CONTRA</h4>
            <p><strong>Posición:</strong> {config['contra_position']}</p>
            <small>Refutará la posición PRO con evidencia especializada y contraargumentos</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Resumen de configuración - Information Summary Pattern
    st.markdown(f"""
    **📋 Configuración del debate:**
    - **Tema:** {config['topic']}
    - **Rondas:** {config['max_rounds']}
    - **Timeout:** {config['timeout_minutes']} minutos
    - **Agentes por equipo:** 5 (Científico, Económico, Histórico, Refutador, Psicológico)
    """)


def run_debate_with_progress(config: Dict[str, Union[str, int]]) -> Optional[Dict[str, Any]]:
    """
    Ejecuta el debate con visualización de progreso en tiempo real.
    
    Implementa el patrón Observer para mostrar el progreso del debate,
    proporcionando feedback continuo al usuario sobre el estado de la
    ejecución. Utiliza contenedores de Streamlit para organización modular.
    
    Args:
        config (Dict[str, Union[str, int]]): Configuración del debate validada
        
    Returns:
        Optional[Dict[str, Any]]: Estado final del debate o None si falla
        
    Design Patterns:
        - Observer: Para actualización de progreso en tiempo real
        - Template Method: Estructura fija con pasos variables
        - Facade: Simplifica la interacción con el sistema de debates
        
    UI/UX Features:
        - Progress Bar: Feedback visual del progreso
        - Real-time Metrics: Actualización dinámica de estadísticas
        - Status Updates: Mensajes descriptivos del estado actual
        
    Error Handling:
        Captura y maneja excepciones del sistema de debates,
        proporcionando feedback apropiado al usuario
        
    Performance Considerations:
        - Actualización eficiente de métricas
        - Rendering optimizado de componentes UI
        
    Complexity:
        Tiempo: O(n) donde n es la duración del debate
        Espacio: O(1) para UI components, O(m) para resultados del debate
    """
    # Creación de contenedores modulares - Composite Pattern
    progress_container = st.container()
    status_container = st.container()
    live_debate_container = st.container()
    
    # Configuración de la interfaz de progreso
    with progress_container:
        st.subheader("🚀 Ejecutando Debate")
        progress_bar = st.progress(0)  # Inicialización de barra de progreso
        status_text = st.empty()       # Placeholder para texto de estado
        
        # Métricas en tiempo real - Dashboard Pattern
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            fragments_metric = st.empty()   # Métrica de evidencia
        with col2:
            arguments_metric = st.empty()   # Métrica de argumentos
        with col3:
            round_metric = st.empty()       # Métrica de rondas
        with col4:
            confidence_metric = st.empty()  # Métrica de confianza
    
    try:
        # Transformación de configuración UI a configuración de dominio
        # Data Transfer Object Pattern
        debate_config = DebateConfig(
            topic=config["topic"],
            pro_position=config["pro_position"],
            contra_position=config["contra_position"],
            max_rounds=config["max_rounds"],
            timeout_minutes=config["timeout_minutes"]
        )
        
        # Inicialización del orquestador - Factory Pattern
        with status_container:
            st.info("🏗️ Inicializando sistema de debates...")
        
        orchestrator = DebateOrchestrator()
        
        # Actualización de progreso - Observer Pattern
        progress_bar.progress(10)
        status_text.text("✅ Orquestador creado")
        
        # Simulación de progreso visual para mejor UX
        status_text.text("🔍 Equipos investigando evidencia...")
        progress_bar.progress(30)
        
        # Ejecución del debate - Command Pattern
        start_time = time.time()
        final_state = orchestrator.run_debate(debate_config)
        end_time = time.time()
        
        # Actualización de métricas basadas en resultados - Data Binding
        if final_state:
            # Extracción de métricas del estado final
            pro_args = len(final_state.get('pro_arguments', []))
            contra_args = len(final_state.get('contra_arguments', []))
            pro_frags = len(final_state.get('pro_fragments', []))
            contra_frags = len(final_state.get('contra_fragments', []))
            current_round = final_state.get('current_round', 0)
            
            # Actualización reactiva de métricas - Observer Pattern
            with fragments_metric:
                st.metric("📊 Evidencia", f"{pro_frags + contra_frags}", "fragmentos")
            
            with arguments_metric:
                st.metric("💬 Argumentos", f"{pro_args + contra_args}", "generados")
            
            with round_metric:
                st.metric("🔄 Ronda", f"{current_round}/{config['max_rounds']}")
            
            # Cálculo y visualización de confianza promedio
            if final_state.get('final_scores'):
                pro_conf = final_state['final_scores'].get('pro_average', 0)
                contra_conf = final_state['final_scores'].get('contra_average', 0)
                avg_conf = (pro_conf + contra_conf) / 2
                with confidence_metric:
                    st.metric("⭐ Confianza", f"{avg_conf:.2f}", "promedio")
        
        # Finalización de progreso con feedback de completitud
        progress_bar.progress(100)
        status_text.text(f"✅ Debate completado en {end_time - start_time:.1f} segundos")
        
        return final_state
        
    except Exception as e:
        # Error handling con feedback inmediato al usuario
        st.error(f"❌ Error ejecutando debate: {e}")
        return None


def display_live_debate(state: Optional[Dict[str, Any]]) -> None:
    """
    Visualiza la conversación del debate en formato interactivo.
    
    Implementa el patrón Presentation Model para mostrar los argumentos
    del debate de manera estructurada y visualmente atractiva. Utiliza
    diseño responsivo y expandible para manejar contenido variable.
    
    Args:
        state (Optional[Dict[str, Any]]): Estado del debate con argumentos
            Estructura esperada:
            - pro_arguments (List[Dict]): Lista de argumentos PRO
            - contra_arguments (List[Dict]): Lista de argumentos CONTRA
            
    Design Patterns:
        - Template Method: Estructura consistente para cada argumento
        - Composite: Organización jerárquica de argumentos por ronda
        - Strategy: Diferentes estilos visuales por equipo
        
    UI/UX Features:
        - Round-based Organization: Agrupación lógica por ronda
        - Expandable Content: Puntos clave colapsables
        - Visual Distinction: Colores y estilos únicos por equipo
        - Confidence Indicators: Visualización de certeza
        
    Accessibility:
        - Semantic HTML structure
        - Color contrast compliance
        - Keyboard navigation support
        
    Performance:
        - Lazy rendering de contenido expandible
        - Efficient DOM updates
        
    Side Effects:
        Renderiza contenido HTML, Markdown y widgets de Streamlit
    """
    # Guard clause para estado inválido - Defensive Programming
    if not state:
        return
    
    st.subheader("💬 Conversación del Debate")
    
    # Extracción de argumentos con valores por defecto - Null Object Pattern
    pro_arguments = state.get('pro_arguments', [])
    contra_arguments = state.get('contra_arguments', [])
    
    # Validación de contenido con feedback apropiado
    if not pro_arguments and not contra_arguments:
        st.warning("⚠️ No se generaron argumentos en el debate")
        return
    
    # Cálculo del número máximo de rondas para iteración
    max_rounds = max(len(pro_arguments), len(contra_arguments))
    
    # Iteración por ronda - Template Method Pattern
    for round_num in range(max_rounds):
        st.markdown(f"### 🔥 Ronda {round_num + 1}")
        
        # Layout de dos columnas para debate adversarial
        col1, col2 = st.columns(2)
        
        # Renderizado de argumento PRO - Strategy Pattern
        if round_num < len(pro_arguments):
            pro_arg = pro_arguments[round_num]
            with col1:
                # Extracción de metadatos con valores por defecto
                confidence = pro_arg.get('confidence_score', 0)
                strategy = pro_arg.get('strategy', 'unknown')
                
                # Renderizado de argumento con diseño branded
                st.markdown(f"""
                <div class="pro-argument">
                    <h4>🟢 Supervisor PRO (Confianza: {confidence:.2f})</h4>
                    <p><strong>Estrategia:</strong> {strategy.upper()}</p>
                    <p>{pro_arg.get('content', 'Sin contenido')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Puntos clave expandibles - Progressive Disclosure
                if pro_arg.get('key_points'):
                    with st.expander(f"🔑 Puntos clave PRO - Ronda {round_num + 1}"):
                        for i, point in enumerate(pro_arg['key_points'], 1):
                            st.write(f"{i}. {point}")
        
        # Renderizado de argumento CONTRA - Strategy Pattern (variante)
        if round_num < len(contra_arguments):
            contra_arg = contra_arguments[round_num]
            with col2:
                # Extracción de metadatos con valores por defecto
                confidence = contra_arg.get('confidence_score', 0)
                strategy = contra_arg.get('strategy', 'unknown')
                
                # Renderizado de argumento con diseño alternativo
                st.markdown(f"""
                <div class="contra-argument">
                    <h4>🔴 Supervisor CONTRA (Confianza: {confidence:.2f})</h4>
                    <p><strong>Estrategia:</strong> {strategy.upper()}</p>
                    <p>{contra_arg.get('content', 'Sin contenido')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Puntos clave expandibles - Progressive Disclosure
                if contra_arg.get('key_points'):
                    with st.expander(f"🔑 Puntos clave CONTRA - Ronda {round_num + 1}"):
                        for i, point in enumerate(contra_arg['key_points'], 1):
                            st.write(f"{i}. {point}")
        
        # Separador visual entre rondas (excepto la última)
        if round_num < max_rounds - 1:
            st.markdown("---")


def display_results(state: Optional[Dict[str, Any]]) -> None:
    """
    Presenta los resultados finales del debate con análisis completo.
    
    Implementa el patrón Report Generator para crear un resumen comprehensivo
    de los resultados del debate, incluyendo ganador, métricas, evidencia
    y análisis estadístico.
    
    Args:
        state (Optional[Dict[str, Any]]): Estado final del debate
            Estructura esperada:
            - winner (str): Ganador del debate
            - final_scores (Dict): Puntuaciones finales
            - debate_summary (str): Resumen ejecutivo
            - pro_fragments/contra_fragments (List): Evidencia utilizada
            
    Design Patterns:
        - Report Generator: Creación estructurada de informes
        - Template Method: Estructura consistente de resultados
        - Data Visualization: Representación clara de métricas
        
    Analytics Features:
        - Winner Determination: Análisis automático de ganador
        - Score Analysis: Métricas detalladas de rendimiento
        - Evidence Summary: Resumen de fuentes utilizadas
        - Margin Analysis: Análisis de cercanía del debate
        
    UI/UX Design:
        - Information Hierarchy: Organización lógica de información
        - Visual Emphasis: Destacado del ganador
        - Metric Cards: Presentación clara de estadísticas
        - Evidence Browser: Exploración de fuentes
        
    Business Intelligence:
        - Performance metrics calculation
        - Competitive analysis
        - Quality assessment
        
    Side Effects:
        Renderiza múltiples componentes UI de Streamlit con datos
    """
    # Guard clause para estado inválido - Defensive Programming
    if not state:
        return
    
    st.subheader("🏆 Resultados Finales")
    
    # Extracción y normalización del ganador - Null Object Pattern
    winner = state.get('winner', 'No determinado')
    if winner is None:
        winner = 'No determinado'
    
    # Visualización del ganador con códigos de color semánticos
    # Color Psychology: Verde=éxito, Rojo=competencia, Azul=neutralidad
    if winner == 'pro':
        st.success(f"🏆 **GANADOR: EQUIPO PRO**")
    elif winner == 'contra':
        st.error(f"🏆 **GANADOR: EQUIPO CONTRA**")
    elif winner == 'empate':
        st.info(f"⚖️ **RESULTADO: EMPATE**")
    else:
        st.warning(f"❓ **RESULTADO: {winner.upper()}**")
    
    # Dashboard de métricas finales - Dashboard Pattern
    final_scores = state.get('final_scores', {})
    if final_scores:
        # Layout en cuatro columnas para métricas balanceadas
        col1, col2, col3, col4 = st.columns(4)
        
        # Métrica de puntuación PRO
        with col1:
            st.metric(
                "🟢 PRO Score", 
                f"{final_scores.get('pro_average', 0):.3f}",
                delta=None  # Sin delta comparativo
            )
        
        # Métrica de puntuación CONTRA
        with col2:
            st.metric(
                "🔴 CONTRA Score", 
                f"{final_scores.get('contra_average', 0):.3f}",
                delta=None
            )
        
        # Métrica de cantidad de argumentos PRO
        with col3:
            st.metric(
                "📜 Args PRO", 
                final_scores.get('pro_total_arguments', 0)
            )
        
        # Métrica de cantidad de argumentos CONTRA
        with col4:
            st.metric(
                "📜 Args CONTRA", 
                final_scores.get('contra_total_arguments', 0)
            )
        
        # Análisis de margen de victoria - Business Intelligence
        pro_avg = final_scores.get('pro_average', 0)
        contra_avg = final_scores.get('contra_average', 0)
        margin = abs(pro_avg - contra_avg)
        
        # Clasificación de cercanía basada en umbrales empíricos
        if margin < 0.05:
            st.info("⚖️ Debate muy reñido")
        elif margin < 0.15:
            st.info("🎯 Victoria por margen estrecho")
        else:
            st.info("🎯 Victoria clara")
    
    # Visualización del resumen ejecutivo - Document Viewer Pattern
    summary = state.get('debate_summary', '')
    if summary:
        st.subheader("📋 Resumen Ejecutivo")
        st.text_area("", value=summary, height=200, disabled=True)
    
    # Sección de evidencia utilizada - Evidence Browser Pattern
    st.subheader("📊 Evidencia Utilizada")
    
    # Layout dividido para evidencia comparativa
    col1, col2 = st.columns(2)
    
    # Evidencia del equipo PRO
    with col1:
        st.write("**🟢 Evidencia PRO:**")
        pro_fragments = state.get('pro_fragments', [])
        if pro_fragments:
            # Mostrar las 5 mejores fuentes con truncamiento inteligente
            for i, frag in enumerate(pro_fragments[:5], 1):
                st.write(f"{i}. [{frag.get('source', 'N/A')}] {frag.get('title', 'Sin título')[:50]}...")
                st.caption(f"Score: {frag.get('final_score', 0):.2f}")
        else:
            st.write("No se encontró evidencia")
    
    # Evidencia del equipo CONTRA
    with col2:
        st.write("**🔴 Evidencia CONTRA:**")
        contra_fragments = state.get('contra_fragments', [])
        if contra_fragments:
            # Mostrar las 5 mejores fuentes con truncamiento inteligente
            for i, frag in enumerate(contra_fragments[:5], 1):
                st.write(f"{i}. [{frag.get('source', 'N/A')}] {frag.get('title', 'Sin título')[:50]}...")
                st.caption(f"Score: {frag.get('final_score', 0):.2f}")
        else:
            st.write("No se encontró evidencia")


def export_debate_results(state: Optional[Dict[str, Any]], config: Dict[str, Union[str, int]]) -> None:
    """
    Proporciona funcionalidad de exportación de resultados del debate.
    
    Implementa el patrón Exporter para permitir múltiples formatos de
    exportación de datos del debate. Utiliza serialización JSON y
    formateo de texto para diferentes casos de uso.
    
    Args:
        state (Optional[Dict[str, Any]]): Estado final del debate
        config (Dict[str, Union[str, int]]): Configuración original del debate
        
    Export Formats:
        - JSON: Datos estructurados para análisis programático
        - TXT: Resumen legible para documentación
        
    Design Patterns:
        - Exporter: Múltiples estrategias de exportación
        - Serializer: Transformación de datos a formatos externos
        - Template Method: Estructura consistente de exports
        
    Data Processing:
        - Deep object serialization para JSON
        - Text formatting para legibilidad humana
        - Timestamp generation para trazabilidad
        
    File Management:
        - Dynamic filename generation
        - MIME type specification
        - Encoding handling (UTF-8)
        
    Side Effects:
        Genera archivos descargables en la interfaz de Streamlit
    """
    # Guard clause para estado inválido - Defensive Programming
    if not state:
        return
    
    st.subheader("📤 Exportar Resultados")
    
    # Preparación de estructura de datos para exportación - DTO Pattern
    export_data: Dict[str, Any] = {
        "config": config,  # Configuración original del debate
        "results": {
            "winner": state.get('winner'),
            "final_scores": state.get('final_scores'),
            "debate_summary": state.get('debate_summary'),
            "arguments": {
                "pro": state.get('pro_arguments', []),
                "contra": state.get('contra_arguments', [])
            },
            "evidence": {
                "pro_fragments": state.get('pro_fragments', []),
                "contra_fragments": state.get('contra_fragments', [])
            },
            "metadata": {
                "start_time": state.get('start_time'),
                "current_time": state.get('current_time'),
                "errors": state.get('errors', [])
            }
        }
    }
    
    # Serialización JSON con configuración optimizada
    json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
    
    # Layout de botones de descarga en dos columnas
    col1, col2 = st.columns(2)
    
    # Exportación JSON - Formato estructurado para análisis
    with col1:
        st.download_button(
            label="📥 Descargar como JSON",
            data=json_data,
            file_name=f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # Exportación TXT - Formato legible para documentación
    with col2:
        # Generación de resumen textual - Template Method
        text_summary = f"""
DEBATE: {config['topic']}
FECHA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

POSICIONES:
PRO: {config['pro_position']}
CONTRA: {config['contra_position']}

GANADOR: {state.get('winner', 'No determinado')}

ARGUMENTOS PRO:
{chr(10).join([f"Ronda {i+1}: {arg.get('content', '')}" for i, arg in enumerate(state.get('pro_arguments', []))])}

ARGUMENTOS CONTRA:
{chr(10).join([f"Ronda {i+1}: {arg.get('content', '')}" for i, arg in enumerate(state.get('contra_arguments', []))])}
"""
        
        st.download_button(
            label="📄 Descargar como TXT",
            data=text_summary,
            file_name=f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )


def main() -> None:
    """
    Función principal que orquesta el flujo completo de la aplicación web.
    
    Implementa el patrón Main Controller para coordinar todos los componentes
    de la aplicación, manejando el flujo de control, validación, ejecución
    y visualización de resultados.
    
    Application Flow:
        1. Inicialización del estado de sesión
        2. Validación del sistema
        3. Configuración del debate
        4. Validación de configuración
        5. Vista previa
        6. Ejecución del debate
        7. Visualización de resultados
        8. Gestión de historial
        
    Design Patterns:
        - Main Controller: Coordinación central de flujo
        - Pipeline: Procesamiento secuencial de pasos
        - State Machine: Gestión de estados de aplicación
        
    Error Handling:
        - Fail-fast validation
        - Graceful degradation
        - User-friendly error messages
        
    Session Management:
        - Persistent state across interactions
        - History management
        - State transitions
        
    User Experience:
        - Progressive disclosure
        - Immediate feedback
        - Clear navigation flow
        
    Performance:
        - Lazy loading of components
        - Efficient state updates
        - Optimized rendering
        
    Side Effects:
        - Modifies session state
        - Renders UI components
        - Manages application lifecycle
    """
    # Inicialización de la aplicación - Bootstrap Pattern
    initialize_session_state()
    validate_system()
    
    # Renderizado del header principal - Branding
    display_main_header()
    
    # Configuración del debate mediante sidebar - Configuration Pattern
    config = sidebar_configuration()
    
    # Validación de configuración con feedback inmediato - Fail-Fast
    config_errors = validate_debate_config(config)
    
    # Manejo de errores de configuración - Guard Clause Pattern
    if config_errors:
        st.error("❌ Errores en la configuración:")
        for error in config_errors:
            st.write(f"• {error}")
        st.stop()  # Detener ejecución hasta corrección
    
    # Vista previa del debate configurado - Preview Pattern
    st.subheader("👀 Vista Previa del Debate")
    create_debate_preview(config)
    
    # Botón de inicio de debate con layout centrado - Call-to-Action Pattern
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Botón principal con estilo prominente
        if st.button("🚀 INICIAR DEBATE", type="primary", use_container_width=True):
            # Activación de estado de ejecución - State Transition
            st.session_state.debate_running = True
            st.session_state.current_debate_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Ejecución condicional del debate - State-driven Execution
    if st.session_state.debate_running:
        # Contenedor de ejecución con spinner para UX
        with st.spinner("🎭 Equipos de IA debatiendo..."):
            result = run_debate_with_progress(config)
            
            # Procesamiento de resultados exitosos
            if result:
                # Persistencia en estado de sesión - Session Management
                st.session_state.debate_result = result
                st.session_state.debate_history.append({
                    "id": st.session_state.current_debate_id,
                    "config": config,
                    "result": result,
                    "timestamp": datetime.now()
                })
            
            # Transición de estado post-ejecución
            st.session_state.debate_running = False
    
    # Visualización de resultados si están disponibles - Conditional Rendering
    if st.session_state.debate_result:
        st.markdown("---")  # Separador visual
        
        # Interfaz de pestañas para organización de información - Tab Pattern
        tab1, tab2, tab3 = st.tabs(["💬 Debate", "🏆 Resultados", "📤 Exportar"])
        
        # Pestaña de conversación del debate
        with tab1:
            display_live_debate(st.session_state.debate_result)
        
        # Pestaña de resultados y análisis
        with tab2:
            display_results(st.session_state.debate_result)
        
        # Pestaña de exportación de datos
        with tab3:
            export_debate_results(st.session_state.debate_result, config)
    
    # Gestión de historial de debates - History Management
    if st.session_state.debate_history:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📚 Historial de Debates")
        
        # Mostrar últimos 5 debates con navegación
        for debate in st.session_state.debate_history[-5:]:  # Últimos 5
            # Botón de navegación para cada debate histórico
            if st.sidebar.button(f"📄 {debate['config']['topic'][:30]}...", key=debate['id']):
                # Carga de debate histórico - State Loading
                st.session_state.debate_result = debate['result']
                st.rerun()  # Recarga de interfaz con nuevo estado


# Punto de entrada de la aplicación - Entry Point Pattern
if __name__ == "__main__":
    """
    Punto de entrada principal de la aplicación.
    
    Implementa el patrón Entry Point estándar de Python, asegurando
    que la aplicación solo se ejecute cuando se invoca directamente
    y no durante importaciones.
    
    Execution Context:
        - Direct execution: Runs main application
        - Import context: No execution (module import only)
        
    Best Practices:
        - Standard Python idiom for executable modules
        - Clear separation of library vs application code
        - Proper encapsulation of main logic
    """
    main()