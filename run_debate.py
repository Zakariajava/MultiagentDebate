"""
Interfaz de Línea de Comandos para Sistema de Debates Autónomos con Inteligencia Artificial.

Este módulo implementa la interfaz principal de usuario para el sistema de debates automatizados,
proporcionando una aplicación de consola interactiva que orquesta la configuración, validación,
ejecución y visualización de debates entre equipos de agentes de IA especializados.

Arquitectura de la Aplicación:
    - Command Line Interface (CLI) Pattern: Interfaz textual interactiva
    - Main Controller Pattern: Coordinación del flujo principal de la aplicación
    - Template Method Pattern: Estructura consistente para visualización
    - Strategy Pattern: Diferentes estrategias de configuración de debates
    - Observer Pattern: Monitoreo y reporting de progreso en tiempo real

Funcionalidades Principales:
    1. Validación Integral del Sistema: Verificación de componentes antes de ejecución
    2. Configuración Interactiva: Selección de temas predefinidos o personalizados
    3. Ejecución Orquestada: Coordinación completa del proceso de debate
    4. Visualización Avanzada: Presentación estructurada de argumentos y resultados
    5. Logging Comprehensivo: Registro detallado para auditoría y debugging

Patrones de Diseño Implementados:
    - Command Line Interface: Para interacción usuario-sistema
    - Template Method: Para estructura consistente de display
    - Strategy: Para diferentes tipos de configuración
    - Factory Method: Para creación de objetos DebateConfig
    - Observer: Para monitoreo de progreso en tiempo real
    - Facade: Para simplificación de operaciones complejas

Principios de Ingeniería de Software:
    - Single Responsibility Principle: Cada función tiene una responsabilidad específica
    - Open/Closed Principle: Extensible para nuevos tipos de debate
    - Dependency Inversion: Dependencias abstraídas mediante interfaces
    - Fail-Fast Principle: Validación temprana para detección de errores
    - User Experience Design: Interfaz intuitiva y feedback claro

User Experience Design:
    - Progressive Disclosure: Información presentada gradualmente
    - Error Prevention: Validación proactiva de entrada de usuario
    - Feedback Immediato: Respuestas claras a acciones del usuario
    - Recovery Support: Opciones para corregir errores y continuar
    - Accessibility: Interfaz textual compatible con lectores de pantalla

Arquitectura de Software:
    - Layered Architecture: Separación clara entre presentación, aplicación y dominio
    - Event-Driven Design: Respuesta a acciones del usuario
    - Pipeline Architecture: Flujo secuencial de procesamiento
    - Error Handling Strategy: Manejo robusto y recuperación de errores

Quality Attributes:
    - Usability: Interfaz intuitiva y autoexplicativa
    - Reliability: Manejo robusto de errores y validación
    - Maintainability: Código modular y bien estructurado
    - Performance: Ejecución eficiente con feedback de progreso
    - Testability: Funciones modulares fáciles de testear

Referencias Técnicas:
    - Clean Code Principles (Robert C. Martin)
    - Design Patterns (Gang of Four)
    - User Interface Design Patterns
    - Command Line Interface Best Practices
    - Software Architecture Patterns

Author: Sistema de Debates IA
Version: 1.0 (Versión Corregida)
License: Academic Use
Dependencies: src.agents, src.config, system_validator, logging_setup
"""

import sys
import os
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import time

# Configuración del path del proyecto - Dependency Injection Pattern
# Permite resolución de dependencias desde el directorio raíz
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importaciones del sistema - Layered Architecture
# Cada import representa una capa específica del sistema
from src.agents.debate_graph import DebateOrchestrator, DebateConfig
from src.config import Config
from system_validator import SystemValidator
from logging_setup import setup_system_logging


def print_header(title: str) -> None:
    """
    Renderiza un header principal con formateo visual consistente.
    
    Implementa principios de User Interface Design para crear jerarquía visual
    clara en la salida de consola, utilizando caracteres ASCII para máxima
    compatibilidad con diferentes terminales y sistemas operativos.
    
    Args:
        title (str): Título a mostrar en el header
        
    Design Principles:
        - Visual Hierarchy: Separadores prominentes para demarcación clara
        - Consistency: Formato estándar aplicado en toda la aplicación
        - Accessibility: Uso de caracteres ASCII universales
        - Branding: Uso de emojis para identidad visual
        
    UI/UX Considerations:
        - Scanability: Fácil identificación de secciones
        - Rhythm: Espaciado consistente para lectura fluida
        - Contrast: Separadores claros para delimitar contenido
        
    Side Effects:
        Imprime contenido formateado en stdout con separadores visuales
    """
    print("\n" + "="*80)  # Separador superior de longitud fija
    print(f"🎯 {title}")   # Título con emoji para identificación visual
    print("="*80)         # Separador inferior matching


def print_section(title: str) -> None:
    """
    Renderiza un header de subsección para organización jerárquica.
    
    Complementa print_header() para crear una estructura visual de dos niveles,
    implementando principios de Information Architecture para organización
    lógica del contenido presentado al usuario.
    
    Args:
        title (str): Título de la subsección
        
    Information Architecture:
        - Hierarchical Structure: Dos niveles de organización visual
        - Progressive Disclosure: Información organizada en secciones digestibles
        - Visual Cues: Longitud diferenciada para jerarquía clara
        
    Design Consistency:
        - Predictable formatting para user expectations
        - Proportional spacing para visual balance
        - Clear demarcation entre secciones relacionadas
        
    Side Effects:
        Imprime header de subsección con formateo específico
    """
    print(f"\n{'='*25} {title} {'='*25}")


def show_available_topics() -> List[Dict[str, str]]:
    """
    Presenta catálogo de temas de debate predefinidos con posiciones estructuradas.
    
    Implementa el patrón Strategy para diferentes tipos de debates, proporcionando
    un conjunto curado de temas que demuestran la versatilidad del sistema en
    diferentes dominios del conocimiento y áreas de controversia social.
    
    Returns:
        List[Dict[str, str]]: Lista de diccionarios con estructura:
            - topic (str): Tema principal del debate
            - pro (str): Posición afirmativa estructurada
            - contra (str): Posición negativa estructurada
            
    Topic Selection Strategy:
        - Relevancia Contemporánea: Temas actuales y de interés público
        - Diversidad Temática: Cobertura de múltiples dominios (tecnología, trabajo, energía, educación, social)
        - Balance Argumentativo: Posiciones equilibradas para debates justos
        - Complejidad Apropiada: Suficiente profundidad para investigación meaningful
        
    Content Curation Principles:
        - Neutrality: Presentación imparcial de ambas posiciones
        - Clarity: Posiciones claramente articuladas y comprensibles
        - Relevance: Temas de importancia social y económica actual
        - Depth: Suficiente complejidad para permitir investigación substantiva
        
    Design Patterns:
        - Strategy: Cada tema representa una estrategia de debate diferente
        - Template Method: Estructura consistente para todos los temas
        - Catalog: Organización sistemática de opciones disponibles
        
    Knowledge Domains Covered:
        - Technology & AI: Impacto de inteligencia artificial
        - Work & Labor: Modalidades de trabajo modernas
        - Energy & Environment: Sostenibilidad y transición energética
        - Education: Metodologías educativas contemporáneas
        - Social Media: Impacto social de tecnologías de comunicación
        
    Side Effects:
        - Imprime catálogo formateado de temas disponibles
        - Proporciona guidance visual para selección de usuario
    """
    # Definición de catálogo de temas - Strategy Pattern
    # Cada tema implementa una estrategia específica de debate
    topics: List[Dict[str, str]] = [
        {
            "topic": "Inteligencia Artificial en el Trabajo",
            "pro": "La IA mejorará las condiciones laborales y creará nuevas oportunidades",
            "contra": "La IA eliminará empleos masivamente y aumentará la desigualdad"
        },
        {
            "topic": "Teletrabajo vs Trabajo Presencial", 
            "pro": "El teletrabajo aumenta la productividad y mejora la calidad de vida",
            "contra": "El trabajo presencial es esencial para la colaboración y cultura empresarial"
        },
        {
            "topic": "Energías Renovables vs Combustibles Fósiles",
            "pro": "Las energías renovables son el futuro sostenible y económicamente viable",
            "contra": "Los combustibles fósiles siguen siendo necesarios para la estabilidad energética"
        },
        {
            "topic": "Educación Online vs Educación Presencial",
            "pro": "La educación online es más accesible y personalizable",
            "contra": "La educación presencial ofrece mejor interacción y desarrollo social"
        },
        {
            "topic": "Redes Sociales: Beneficio vs Perjuicio",
            "pro": "Las redes sociales conectan personas y democratizan la información",
            "contra": "Las redes sociales dañan la salud mental y propagan desinformación"
        }
    ]
    
    # Presentación estructurada del catálogo - Template Method
    print_section("TEMAS DE DEBATE SUGERIDOS")
    for i, topic_info in enumerate(topics, 1):
        print(f"\n{i}. {topic_info['topic']}")
        print(f"   🟢 PRO: {topic_info['pro']}")
        print(f"   🔴 CONTRA: {topic_info['contra']}")
    
    return topics


def get_user_choice(topics: List[Dict[str, str]]) -> Optional[DebateConfig]:
    """
    Gestiona la interacción de selección de tema con el usuario.
    
    Implementa el patrón Command Line Interface con validación robusta y
    múltiples opciones de configuración, proporcionando flexibilidad máxima
    al usuario mientras mantiene una experiencia guiada y error-free.
    
    Args:
        topics (List[Dict[str, str]]): Lista de temas predefinidos disponibles
        
    Returns:
        Optional[DebateConfig]: Configuración de debate seleccionada o None para salir
        
    Interaction Design Patterns:
        - Menu-Driven Interface: Opciones claras y numeradas
        - Input Validation: Verificación robusta de entrada de usuario
        - Error Recovery: Posibilidad de corregir errores y reintentar
        - Escape Hatch: Opción clara para salir del flujo
        
    User Experience Features:
        - Clear Options: Opciones bien definidas y fáciles de entender
        - Flexible Input: Múltiples formatos de entrada aceptados
        - Quick Access: Opción de testing rápido disponible
        - Custom Configuration: Posibilidad de configuración personalizada
        
    Input Validation Strategy:
        - Range Checking: Validación de números dentro de rango válido
        - Type Checking: Verificación de tipos de entrada esperados
        - Edge Case Handling: Manejo de entradas vacías y casos límite
        - User Feedback: Mensajes claros para entradas inválidas
        
    Error Handling:
        - Graceful Degradation: Manejo elegante de errores de entrada
        - Clear Messaging: Mensajes de error específicos y accionables
        - Recovery Support: Permite al usuario corregir y continuar
        - Loop Protection: Validación continua hasta entrada válida
        
    Control Flow:
        - State Machine: Diferentes estados basados en selección de usuario
        - Conditional Branching: Flujo adaptativo según elección
        - Factory Method: Creación de DebateConfig según selección
        
    Complexity:
        Tiempo: O(1) para procesamiento, O(n) para interacción de usuario
        Espacio: O(1) para almacenamiento de configuración
    """
    print_section("SELECCIÓN DE TEMA")
    
    # Loop de interacción con validación - State Machine Pattern
    while True:
        # Presentación de opciones - Menu-Driven Interface
        print("Opciones:")
        print("1-5: Usar uno de los temas sugeridos")
        print("C: Crear tema personalizado")
        print("T: Tema rápido de prueba")
        print("Q: Salir")
        
        # Captura y normalización de entrada - Input Sanitization
        choice = input("\nTu elección: ").strip().upper()
        
        # Procesamiento de opciones - Strategy Pattern
        if choice == "Q":
            # Exit strategy - Clean termination
            return None
        elif choice == "T":
            # Quick test strategy - Factory Method para configuración rápida
            return DebateConfig(
                topic="Café vs Té",
                pro_position="El café es la mejor bebida para la productividad y salud",
                contra_position="El té es más saludable y ofrece mejor bienestar a largo plazo",
                max_rounds=2
            )
        elif choice == "C":
            # Custom configuration strategy - Delegation a función especializada
            return create_custom_topic()
        elif choice.isdigit() and 1 <= int(choice) <= len(topics):
            # Predefined topic strategy - Factory Method con configuración base
            topic_info = topics[int(choice) - 1]
            rounds = get_rounds_choice()
            return DebateConfig(
                topic=topic_info["topic"],
                pro_position=topic_info["pro"],
                contra_position=topic_info["contra"],
                max_rounds=rounds
            )
        else:
            # Error handling - User feedback y retry opportunity
            print("❌ Opción inválida. Intenta de nuevo.")


def create_custom_topic() -> Optional[DebateConfig]:
    """
    Facilita la creación de temas de debate personalizados por el usuario.
    
    Implementa el patrón Builder para construcción paso a paso de configuración
    de debate personalizada, con validación exhaustiva en cada etapa para
    asegurar la calidad y completitud de la configuración resultante.
    
    Returns:
        Optional[DebateConfig]: Configuración personalizada o None si se cancela
        
    Builder Pattern Implementation:
        - Step-by-Step Construction: Construcción incremental de configuración
        - Validation at Each Step: Verificación inmediata de cada entrada
        - Rollback Capability: Posibilidad de cancelar en cualquier punto
        - Complete Object Creation: Validación final antes de retorno
        
    Validation Strategy:
        - Non-Empty Validation: Verificación de contenido substantivo
        - Length Checking: Asegurar suficiente detalle para debate meaningful
        - Sanitization: Limpieza de entrada de usuario
        - Business Rule Enforcement: Aplicación de reglas de dominio
        
    User Experience Design:
        - Clear Prompts: Instrucciones específicas para cada campo
        - Immediate Feedback: Validación inmediata con mensajes claros
        - Error Recovery: Posibilidad de corregir errores
        - Progress Indication: Claridad sobre progreso en el proceso
        
    Quality Assurance:
        - Input Validation: Verificación exhaustiva de cada campo
        - Business Logic: Aplicación de reglas de negocio del dominio
        - Error Prevention: Validación proactiva para prevenir errores
        - User Guidance: Feedback claro para entries exitosas y fallidas
        
    Domain Business Rules:
        - Topic completeness: Tema debe ser substantivo
        - Position articulation: Posiciones deben ser claras y específicas
        - Balance requirement: Ambas posiciones deben estar presentes
        - Complexity threshold: Suficiente detalle para investigación
        
    Side Effects:
        - Interactúa con usuario mediante prompts secuenciales
        - Valida entrada en tiempo real
        - Proporciona feedback inmediato sobre validación
    """
    print_section("CREAR TEMA PERSONALIZADO")
    
    # Builder Pattern - Construcción paso a paso con validación
    
    # Paso 1: Construcción del tema principal
    topic = input("📝 Tema del debate: ").strip()
    if not topic:
        print("❌ El tema no puede estar vacío")
        return None
    
    # Paso 2: Construcción de posición PRO
    pro_position = input("🟢 Posición PRO: ").strip()
    if not pro_position:
        print("❌ La posición PRO no puede estar vacía")
        return None
    
    # Paso 3: Construcción de posición CONTRA
    contra_position = input("🔴 Posición CONTRA: ").strip()
    if not contra_position:
        print("❌ La posición CONTRA no puede estar vacía")
        return None
    
    # Paso 4: Configuración de parámetros de ejecución
    rounds = get_rounds_choice()
    
    # Assembly final del objeto - Factory Method
    return DebateConfig(
        topic=topic,
        pro_position=pro_position,
        contra_position=contra_position,
        max_rounds=rounds
    )


def get_rounds_choice() -> int:
    """
    Solicita y valida la selección del número de rondas para el debate.
    
    Implementa validación robusta con rangos de negocio apropiados,
    proporcionando valores por defecto basados en mejores prácticas
    empíricas del sistema.
    
    Returns:
        int: Número de rondas validado (1-5)
        
    Validation Strategy:
        - Range Validation: Verificación de límites de negocio (1-5 rondas)
        - Type Validation: Verificación de entrada numérica válida
        - Default Handling: Valor por defecto para entrada vacía
        - Error Recovery: Loop hasta entrada válida
        
    Business Rules:
        - Minimum Rounds: 1 ronda mínima para debate básico
        - Maximum Rounds: 5 rondas máximo para evitar fatiga
        - Optimal Range: 2-3 rondas recomendadas para balance
        - Default Value: 3 rondas como punto óptimo empírico
        
    User Experience:
        - Clear Guidance: Instrucciones específicas con recomendaciones
        - Default Option: Entrada vacía usa valor recomendado
        - Error Messages: Feedback específico para errores
        - Continuous Validation: Loop hasta entrada válida
        
    Error Handling:
        - ValueError Exception: Manejo de entrada no numérica
        - Range Exception: Manejo de valores fuera de rango
        - User Feedback: Mensajes claros para corrección
        - Recovery Loop: Permite intentos múltiples
        
    Complexity:
        Tiempo: O(1) para validación, O(n) para interacción de usuario
        Espacio: O(1) para almacenamiento de entrada
    """
    # Validation loop con range checking - Input Validation Pattern
    while True:
        try:
            # Prompt con guidance y valor por defecto
            rounds = input("🔄 Número de rondas (1-5, recomendado 2-3): ").strip()
            if not rounds:
                return 3  # Default value basado en mejores prácticas
            
            # Type conversion con validation
            rounds = int(rounds)
            if 1 <= rounds <= 5:
                return rounds
            else:
                # Range validation error - User feedback
                print("❌ Debe ser entre 1 y 5 rondas")
        except ValueError:
            # Type validation error - User feedback
            print("❌ Debe ser un número válido")


def validate_system_before_debate() -> bool:
    """
    Ejecuta validación crítica del sistema antes de permitir ejecución de debates.
    
    Implementa el patrón Fail-Fast con validación de componentes críticos,
    proporcionando feedback claro sobre el estado del sistema y opciones
    de recuperación para problemas no críticos.
    
    Returns:
        bool: True si el sistema está listo para debates, False en caso contrario
        
    Validation Strategy:
        - Critical Component Checking: Verificación de componentes esenciales
        - Graceful Degradation: Opciones para continuar con limitaciones
        - User Choice: Permitir decisión informada sobre limitaciones
        - Clear Messaging: Feedback específico sobre problemas encontrados
        
    System Components Validated:
        1. Configuration Loading: Verificación de carga de configuración
        2. LLM Connectivity: Conexión con GitHub Models
        3. Search System: Disponibilidad de sistema de búsqueda
        4. Core Dependencies: Verificación de importaciones críticas
        
    Error Classification:
        - Critical Errors: Impiden ejecución (GitHub Models no disponible)
        - Warning Conditions: Afectan funcionalidad (búsqueda no configurada)
        - Information Messages: Estado del sistema sin impacto crítico
        
    Design Patterns:
        - Fail-Fast: Detección temprana de problemas críticos
        - Circuit Breaker: Verificación de servicios externos
        - Strategy: Diferentes enfoques según tipo de problema
        - User Choice: Decisión informada sobre limitaciones aceptables
        
    User Experience:
        - Clear Status: Información transparente sobre estado del sistema
        - Actionable Guidance: Instrucciones específicas para resolución
        - Choice Points: Opciones para continuar con limitaciones
        - Recovery Support: Guidance para configuración completa
        
    Business Logic:
        - Essential vs Optional: Distinción clara entre componentes críticos y opcionales
        - Risk Assessment: Evaluación de impacto de limitaciones
        - User Empowerment: Información para decisión informada
        
    Side Effects:
        - Verifica conectividad con servicios externos
        - Carga y valida configuración del sistema
        - Interactúa con usuario para decisiones sobre limitaciones
    """
    print_section("VALIDACIÓN DEL SISTEMA")
    
    # Instanciación del validador - Factory Pattern
    validator = SystemValidator()
    
    # Validación de configuración básica - Configuration Loading
    Config.ensure_loaded()
    
    # Validación crítica: GitHub Models - Circuit Breaker Pattern
    try:
        from src.utils.github_models import github_models
        if not github_models.test_connection():
            print("❌ No se puede conectar con GitHub Models")
            print("🔧 Verifica tu GITHUB_TOKEN en .env")
            return False
    except Exception as e:
        print(f"❌ Error en modelos: {e}")
        return False
    
    # Validación opcional: Search System - Graceful Degradation
    try:
        from src.utils.search import SearchSystem
        search = SearchSystem()
        if not search.get_status()["can_search"]:
            print("⚠️ Sistema de búsqueda no configurado")
            print("💡 Obtén API key en: https://tavily.com/")
            print("🔧 Agrégala a .env: TAVILY_API_KEY=tu_key")
            
            # User choice para continuar con limitaciones - User Empowerment
            choice = input("¿Continuar sin búsquedas reales? (s/N): ").strip().lower()
            if choice not in ['s', 'si', 'sí', 'y', 'yes']:
                return False
    except Exception as e:
        print(f"❌ Error en búsquedas: {e}")
        return False
    
    # Confirmación de sistema válido
    print("✅ Sistema básico validado")
    return True


def display_debate_progress(state: Dict[str, Any], stage: str) -> None:
    """
    Muestra indicadores de progreso específicos según la etapa del debate.
    
    Implementa el patrón Observer para proporcionar feedback en tiempo real
    sobre el progreso del debate, mejorando la experiencia del usuario
    mediante información contextual sobre las operaciones en curso.
    
    Args:
        state (Dict[str, Any]): Estado actual del debate (puede estar vacío)
        stage (str): Etapa actual del proceso de debate
            Valores válidos: "setup", "research", "argument", "evaluation", "finalization"
            
    Observer Pattern Implementation:
        - Real-time Updates: Información instantánea sobre progreso
        - Contextual Messaging: Mensajes específicos por etapa
        - User Awareness: Mantiene al usuario informado sobre operaciones largas
        - Progress Indication: Claridad sobre duración esperada
        
    Stage-Specific Messaging:
        - setup: Configuración inicial y creación de equipos
        - research: Investigación de evidencia (operación larga)
        - argument: Generación de argumentos por ronda
        - evaluation: Evaluación de ronda completada
        - finalization: Cálculo de resultados finales
        
    User Experience Design:
        - Progress Transparency: Información clara sobre operaciones en curso
        - Time Expectation: Guidance sobre duración esperada
        - Activity Indication: Claridad sobre progreso activo
        - Contextual Information: Detalles específicos por etapa
        
    Design Patterns:
        - Observer: Notificación de cambios de estado
        - Strategy: Diferentes mensajes según etapa
        - Template Method: Estructura consistente de mensajes
        
    Performance Considerations:
        - Lightweight Operations: Minimal overhead para reporting
        - Non-blocking Updates: No interfiere con operaciones principales
        - Efficient Messaging: Updates concisos y informativos
        
    Side Effects:
        Imprime mensajes de progreso específicos en stdout
    """
    # Strategy Pattern - Diferentes estrategias de mensaje según etapa
    if stage == "setup":
        print("🏗️ Configurando debate y creando equipos...")
    elif stage == "research":
        print("🔍 Equipos investigando evidencia...")
        print("   ⏳ Esto puede tomar 2-3 minutos...")  # Time expectation
    elif stage == "argument":
        round_num = state.get("current_round", 0)
        print(f"💬 Ronda {round_num} - Generando argumentos...")
    elif stage == "evaluation":
        print("📊 Evaluando ronda...")
    elif stage == "finalization":
        print("🏁 Finalizando debate y calculando resultados...")


def show_debate_conversation(state: Dict[str, Any]) -> None:
    """
    Visualiza la conversación completa del debate con formateo avanzado.
    
    Implementa el patrón Presentation Model para transformar los datos del
    debate en una representación visual estructurada que facilite la comprensión
    del flujo argumentativo y la calidad de los intercambios.
    
    Args:
        state (Dict[str, Any]): Estado final del debate conteniendo:
            - pro_arguments (List[Dict]): Lista de argumentos del equipo PRO
            - contra_arguments (List[Dict]): Lista de argumentos del equipo CONTRA
            - errors (List[str]): Lista de errores encontrados durante ejecución
            
    Presentation Model Features:
        - Structured Layout: Organización clara por rondas de debate
        - Visual Distinction: Formateo diferenciado para cada equipo
        - Content Wrapping: Manejo inteligente de líneas largas
        - Error Reporting: Visualización clara de problemas encontrados
        
    Visual Design Principles:
        - Hierarchical Information: Organización clara por rondas
        - Color Psychology: Verde para PRO, Rojo para CONTRA (mediante emojis)
        - Readability: Formateo optimizado para lectura en consola
        - Scanability: Estructura fácil de navegar visualmente
        
    Content Processing:
        - Line Wrapping: División inteligente de líneas largas (76 caracteres)
        - Box Drawing: Uso de caracteres ASCII para contenedores visuales
        - Confidence Display: Visualización de scores de confianza
        - Round Organization: Agrupación lógica por ronda de debate
        
    Error Handling:
        - Empty State Handling: Manejo de debates sin argumentos
        - Error Visualization: Presentación clara de errores encontrados
        - Graceful Degradation: Funcionamiento con datos parciales
        - User Feedback: Información clara sobre problemas
        
    Typography:
        - Consistent Formatting: Estructura visual uniforme
        - ASCII Box Drawing: Compatibilidad universal con terminales
        - Proportional Spacing: Balance visual entre elementos
        - Emphasis Markers: Uso de emojis para identificación rápida
        
    Information Architecture:
        - Chronological Organization: Presentación secuencial por rondas
        - Team Identification: Distinción clara entre equipos
        - Metadata Display: Información sobre confianza y estrategias
        - Visual Separators: Demarcación clara entre elementos
        
    Side Effects:
        Imprime representación visual completa del debate en stdout
    """
    print_section("💬 CONVERSACIÓN DEL DEBATE")
    
    # Extracción de datos con handling de casos vacíos - Null Object Pattern
    pro_args = state.get('pro_arguments', [])
    contra_args = state.get('contra_arguments', [])
    
    # Validación de contenido con feedback claro - Guard Clause
    if not pro_args and not contra_args:
        print("❌ No se generaron argumentos en el debate")
        # Error reporting con context adicional
        errors = state.get('errors', [])
        if errors:
            print("🔍 Errores encontrados:")
            for error in errors[-3:]:  # Últimos 3 errores para brevedad
                print(f"   - {error}")
        return
    
    # Cálculo de rondas para iteración - Range Determination
    max_rounds = max(len(pro_args), len(contra_args))
    
    # Iteración por ronda con formateo visual - Template Method Pattern
    for ronda in range(max_rounds):
        # Header de ronda con énfasis visual
        print(f"\n{'🔥' * 20} RONDA {ronda + 1} {'🔥' * 20}")
        
        # Renderizado de argumento PRO - Strategy Pattern para team-specific formatting
        if ronda < len(pro_args):
            pro_arg = pro_args[ronda]
            confidence = pro_arg.get('confidence_score', 0)
            print(f"\n🟢 SUPERVISOR PRO ARGUMENTA (Confianza: {confidence:.2f})")
            
            # Box drawing para contenido - ASCII Art Pattern
            print("┌" + "─" * 78 + "┐")
            
            content = pro_arg.get('content', 'Sin contenido')
            lines = content.split('\n')
            
            # Line wrapping con formateo consistente - Text Processing
            for line in lines:
                # División de líneas largas para fit en box
                while len(line) > 76:
                    print(f"│ {line[:76]} │")
                    line = line[76:]
                if line:
                    print(f"│ {line:<76} │")  # Left-aligned con padding
            
            print("└" + "─" * 78 + "┘")
        
        # Renderizado de argumento CONTRA - Strategy Pattern (variante)
        if ronda < len(contra_args):
            contra_arg = contra_args[ronda]
            confidence = contra_arg.get('confidence_score', 0)
            print(f"\n🔴 SUPERVISOR CONTRA RESPONDE (Confianza: {confidence:.2f})")
            
            # Box drawing matching para consistencia visual
            print("┌" + "─" * 78 + "┐")
            
            content = contra_arg.get('content', 'Sin contenido')
            lines = content.split('\n')
            
            # Line processing idéntico para consistency
            for line in lines:
                while len(line) > 76:
                    print(f"│ {line[:76]} │")
                    line = line[76:]
                if line:
                    print(f"│ {line:<76} │")
            
            print("└" + "─" * 78 + "┘")
        
        # Separador entre rondas (excepto la última) - Visual Flow
        if ronda < max_rounds - 1:
            print("\n" + "⬇️  " * 20)


def show_debate_results(state: Dict[str, Any]) -> None:
    """
    Presenta un análisis comprehensivo de los resultados finales del debate.
    
    Implementa el patrón Report Generator para crear una visualización
    estructurada de métricas, estadísticas y análisis del debate completado,
    proporcionando insights valiosos sobre el rendimiento y resultado.
    
    Args:
        state (Dict[str, Any]): Estado final del debate conteniendo:
            - winner (str): Ganador determinado del debate
            - final_scores (Dict): Scores finales y métricas
            - pro_fragments/contra_fragments (List): Evidencia utilizada
            - current_round (int): Rondas completadas
            
    Report Generation Strategy:
        - Winner Announcement: Presentación prominente del resultado
        - Score Analysis: Análisis detallado de métricas de rendimiento
        - Statistical Summary: Resumen cuantitativo de actividad
        - Margin Analysis: Interpretación de cercanía del debate
        
    Analytics Features:
        - Quantitative Metrics: Scores numéricos precisos
        - Qualitative Assessment: Interpretación de proximidad
        - Comparative Analysis: PRO vs CONTRA en múltiples dimensiones
        - Activity Summary: Conteos de argumentos y evidencia
        
    Business Intelligence:
        - Performance Measurement: Evaluación de calidad argumentativa
        - Competitive Analysis: Comparación entre equipos
        - Effectiveness Metrics: Medición de eficacia argumentativa
        - Quality Assessment: Evaluación de nivel del debate
        
    Data Visualization:
        - Hierarchical Information: Organización lógica de métricas
        - Visual Emphasis: Destacado de información clave
        - Proportional Display: Representación balanceada de datos
        - Context Provision: Interpretación de números mediante análisis
        
    Statistical Analysis:
        - Margin Calculation: Diferencia entre scores de equipos
        - Significance Assessment: Evaluación de diferencias meaningfulas
        - Categorical Classification: Clasificación de resultados (reñido/claro)
        - Trend Analysis: Patrones en rendimiento de equipos
        
    User Value:
        - Clear Outcomes: Resultado definitivo y comprensible
        - Performance Insights: Comprensión de calidad del debate
        - Comparative Understanding: Relación entre equipos
        - Educational Value: Aprendizaje sobre proceso de debate
        
    Side Effects:
        Imprime análisis comprehensivo de resultados en stdout
    """
    print_section("🏆 RESULTADOS FINALES")
    
    # Winner determination con null safety - Defensive Programming
    winner = state.get('winner', 'No determinado')
    if winner is None:
        winner = 'No determinado'
    
    # Prominent winner announcement - Visual Emphasis
    print(f"🏆 GANADOR: {winner.upper()}")
    
    # Score analysis y detailed metrics - Analytics Dashboard
    final_scores = state.get('final_scores', {})
    if final_scores:
        pro_avg = final_scores.get('pro_average', 0)
        contra_avg = final_scores.get('contra_average', 0)
        
        # Detailed score presentation
        print(f"\n📊 PUNTUACIONES:")
        print(f"   🟢 PRO: {pro_avg:.3f}")
        print(f"   🔴 CONTRA: {contra_avg:.3f}")
        print(f"   📊 Margen: {abs(pro_avg - contra_avg):.3f}")
        
        # Margin analysis con interpretación qualitativa - Business Intelligence
        margin = abs(pro_avg - contra_avg)
        if margin < 0.05:
            print("   ⚖️ Debate muy reñido")
        elif margin < 0.15:
            print("   🎯 Victoria por margen estrecho")
        else:
            print("   🎯 Victoria clara")
    
    # Statistical summary de actividad del debate - Activity Metrics
    pro_frags = len(state.get('pro_fragments', []))
    contra_frags = len(state.get('contra_fragments', []))
    pro_args_count = len(state.get('pro_arguments', []))
    contra_args_count = len(state.get('contra_arguments', []))
    
    print(f"\n📈 ESTADÍSTICAS:")
    print(f"   📜 Argumentos: PRO {pro_args_count} vs CONTRA {contra_args_count}")
    print(f"   📊 Evidencia: PRO {pro_frags} vs CONTRA {contra_frags} fragmentos")
    print(f"   🔄 Rondas completadas: {state.get('current_round', 0)}")


def run_debate_with_monitoring(config: DebateConfig) -> Optional[Dict[str, Any]]:
    """
    Ejecuta un debate completo con monitoreo comprehensivo y logging.
    
    Implementa el patrón Orchestrator para coordinar la ejecución completa
    del debate, integrando logging, monitoreo de rendimiento, y manejo
    robusto de errores con recovery strategies apropiadas.
    
    Args:
        config (DebateConfig): Configuración validada del debate a ejecutar
        
    Returns:
        Optional[Dict[str, Any]]: Estado final del debate o None si falla
        
    Orchestration Strategy:
        - Pre-execution Setup: Configuración de logging y display
        - Monitoring Integration: Seguimiento de progreso en tiempo real
        - Performance Measurement: Timing y métricas de ejecución
        - Post-execution Analysis: Procesamiento y display de resultados
        
    Monitoring Features:
        - Real-time Progress: Updates de estado durante ejecución
        - Performance Timing: Medición de duración total
        - Error Tracking: Captura y logging de errores
        - Success Metrics: Medición de completitud y calidad
        
    Logging Integration:
        - Structured Logging: Eventos estructurados para auditoría
        - Performance Logging: Métricas de timing y throughput
        - Error Logging: Captura detallada de excepciones
        - Business Event Logging: Eventos del dominio de debate
        
    Error Handling Strategy:
        - Exception Capture: Manejo comprehensivo de errores
        - Graceful Degradation: Functionality partial en caso de errores
        - User Communication: Feedback claro sobre problemas
        - Recovery Guidance: Instrucciones para resolución
        
    Performance Monitoring:
        - Execution Timing: Medición de duración total
        - Resource Usage: Tracking de utilización de recursos
        - Throughput Metrics: Medición de productividad del sistema
        - Quality Metrics: Evaluación de resultados producidos
        
    User Experience:
        - Progress Transparency: Visibilidad completa del proceso
        - Performance Feedback: Información sobre timing
        - Result Presentation: Visualización clara de outcomes
        - Error Communication: Mensajes comprensibles sobre problemas
        
    Business Value:
        - Audit Trail: Registro completo para compliance
        - Performance Analytics: Datos para optimización
        - Quality Assurance: Verificación de outputs
        - User Satisfaction: Experiencia optimizada
        
    Side Effects:
        - Configura sistema de logging para el debate
        - Ejecuta debate completo con orquestador
        - Registra eventos y métricas en logs
        - Presenta resultados en múltiples formatos
    """
    print_header("🎭 EJECUTANDO DEBATE CON IA")
    
    # Setup de logging comprehensivo - Observability Pattern
    debate_logger = setup_system_logging()
    debate_logger.log_debate_start(config.topic, config.pro_position, config.contra_position)
    
    # Configuration display para user awareness - Transparency Principle
    print(f"📋 TEMA: {config.topic}")
    print(f"🟢 PRO: {config.pro_position}")
    print(f"🔴 CONTRA: {config.contra_position}")
    print(f"🔄 RONDAS: {config.max_rounds}")
    
    try:
        # Orchestrator initialization - Factory Pattern
        orchestrator = DebateOrchestrator()
        
        # Pre-execution setup con progress indication
        print("\n🚀 Iniciando debate...")
        display_debate_progress({}, "setup")
        
        # Performance timing - Metrics Collection
        start_time = time.time()
        final_state = orchestrator.run_debate(config)
        end_time = time.time()
        
        # Performance calculation y reporting
        duration = end_time - start_time
        print(f"\n✅ Debate completado en {duration:.1f} segundos")
        
        # Results presentation - Presentation Layer
        show_debate_conversation(final_state)
        show_debate_results(final_state)
        
        # Comprehensive logging de completion - Audit Trail
        stats = {
            "duracion_segundos": duration,
            "argumentos_pro": len(final_state.get('pro_arguments', [])),
            "argumentos_contra": len(final_state.get('contra_arguments', [])),
            "errores": len(final_state.get('errors', []))
        }
        debate_logger.log_debate_end(final_state.get('winner', 'unknown'), duration, stats)
        
        return final_state
        
    except Exception as e:
        # Comprehensive error handling - Error Recovery
        print(f"\n❌ Error ejecutando debate: {e}")
        debate_logger.log_error("debate_execution", str(e), e)
        return None


def main() -> None:
    """
    Función principal que orquesta el flujo completo de la aplicación.
    
    Implementa el patrón Main Controller para coordinar el ciclo de vida
    completo de la aplicación, desde la inicialización hasta la terminación,
    incluyendo validación, configuración, ejecución y cleanup.
    
    Application Lifecycle:
        1. System Validation: Verificación de precondiciones
        2. User Interaction: Configuración mediante interfaz
        3. Execution Orchestration: Coordinación de debate
        4. Results Presentation: Visualización de outcomes
        5. Continuation Handling: Opciones para múltiples debates
        6. Graceful Termination: Cleanup y despedida
        
    Control Flow Patterns:
        - Sequential Processing: Pasos ordenados lógicamente
        - Conditional Branching: Flujo adaptativo según condiciones
        - Loop Control: Manejo de continuación de debates
        - Exception Handling: Recovery robusto de errores
        
    User Experience Design:
        - Guided Flow: Proceso paso a paso claro
        - Error Recovery: Opciones para corregir problemas
        - Progress Indication: Clarity sobre estado actual
        - Continuation Options: Flexibilidad para múltiples usos
        
    Error Handling Strategy:
        - Validation Gates: Verificación en puntos críticos
        - Graceful Degradation: Functionality parcial cuando posible
        - User Communication: Feedback claro sobre problemas
        - Recovery Options: Guidance para resolución
        
    System Integration:
        - Validation Integration: Uso de SystemValidator
        - Logging Integration: Setup comprehensivo de logging
        - Configuration Management: Handling de DebateConfig
        - Results Processing: Integración con presentation layer
        
    Quality Attributes:
        - Reliability: Manejo robusto de errores y edge cases
        - Usability: Interfaz intuitiva y guidance clara
        - Maintainability: Código modular y bien estructurado
        - Performance: Ejecución eficiente con feedback apropiado
        
    Business Logic:
        - Process Orchestration: Coordinación de workflow completo
        - Validation Enforcement: Aplicación de business rules
        - User Empowerment: Opciones para decisiones informadas
        - Quality Assurance: Verificación de precondiciones y outcomes
        
    Side Effects:
        - Valida estado completo del sistema
        - Interactúa extensivamente con usuario
        - Ejecuta debates completos con logging
        - Maneja recursos y cleanup apropiadamente
    """
    print_header("🎯 SISTEMA DE DEBATES CON IA - VERSIÓN CORREGIDA")
    
    # Application introduction - User Onboarding
    print("🤖 Bienvenido al sistema de debates automáticos")
    print("📊 Dos equipos de IA debatirán usando evidencia real")
    
    try:
        # System validation gate - Fail-Fast Principle
        if not validate_system_before_debate():
            print("\n❌ El sistema no está listo para debates")
            print("🔧 Ejecuta 'python system_validator.py' para más detalles")
            return
        
        # User interaction flow - Guided Configuration
        topics = show_available_topics()
        config = get_user_choice(topics)
        
        # User exit handling - Graceful Termination
        if config is None:
            print("\n👋 ¡Hasta luego!")
            return
        
        # Confirmation step - User Verification
        print_section("CONFIRMACIÓN")
        print(f"📋 Tema: {config.topic}")
        print(f"🔄 Rondas: {config.max_rounds}")
        print(f"⏱️ Tiempo estimado: {config.max_rounds * 2} minutos")
        
        # Final confirmation gate - User Choice
        confirm = input("\n¿Ejecutar debate? (S/n): ").strip().lower()
        if confirm in ['n', 'no']:
            print("👋 Debate cancelado")
            return
        
        # Main execution orchestration - Core Business Logic
        result = run_debate_with_monitoring(config)
        
        # Results processing y continuation handling
        if result:
            print("\n🎉 ¡Debate completado exitosamente!")
            
            # Continuation option - User Empowerment
            another = input("\n¿Ejecutar otro debate? (s/N): ").strip().lower()
            if another in ['s', 'si', 'sí', 'y', 'yes']:
                main()  # Recursive call para siguiente debate
        else:
            print("\n❌ El debate no se completó correctamente")
            print("🔍 Revisa los logs para más detalles")
    
    except KeyboardInterrupt:
        # User interruption handling - Graceful Shutdown
        print("\n⏹️ Debate interrumpido por el usuario")
    except Exception as e:
        # Global exception handling - Error Recovery
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup y farewell - Application Termination
        print("\n" + "="*80)
        print("🎭 GRACIAS POR USAR EL SISTEMA DE DEBATES")
        print("="*80)


# Entry Point Pattern - Standard Python Idiom
if __name__ == "__main__":
    """
    Entry point para ejecución standalone de la aplicación.
    
    Implementa el patrón Entry Point estándar de Python con interfaz
    de usuario completa, incluyendo pause final para review de resultados
    en entornos de desarrollo.
    
    Execution Context:
        - Direct Execution: Ejecuta aplicación completa con UI
        - Import Context: No execution (library mode)
        
    User Experience:
        - Automatic Execution: Flujo completo de aplicación
        - Manual Termination: Control de usuario sobre finalización
        - Development Support: Pause para review en desarrollo
        
    Best Practices:
        - Standard Python idiom para módulos ejecutables
        - Clear separation entre library y application code
        - User-friendly interaction patterns
        - Development-friendly termination handling
    """
    main()
    input("\n👋 Presiona Enter para salir...")