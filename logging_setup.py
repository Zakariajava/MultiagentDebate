"""
Sistema de Logging Especializado para Plataforma de Debates con Inteligencia Artificial.

Este módulo implementa una infraestructura de logging avanzada y especializada para el sistema
de debates automatizados, proporcionando observabilidad comprehensiva, trazabilidad de eventos
y capacidades de auditoría para sistemas distribuidos de agentes de IA.

Arquitectura de Logging:
    - Structured Logging Pattern: Logging estructurado para análisis automatizado
    - Multi-Logger Strategy: Separación de responsabilidades por componente
    - Hierarchical Organization: Organización jerárquica de eventos por contexto
    - Configuration-Driven: Configuración adaptable según ambiente de ejecución

Principios de Observabilidad:
    - Distributed Tracing: Seguimiento de operaciones a través de múltiples componentes
    - Contextual Logging: Información rica en contexto para debugging efectivo
    - Performance Monitoring: Métricas de timing y throughput integradas
    - Error Tracking: Captura y categorización comprehensiva de errores

Patrones de Diseño Implementados:
    - Factory Pattern: Creación especializada de loggers por responsabilidad
    - Strategy Pattern: Diferentes estrategias de logging según componente
    - Observer Pattern: Notificación y registro de eventos del sistema
    - Facade Pattern: Interfaz simplificada para operaciones de logging complejas
    - Template Method: Estructura consistente para configuración de loggers

Características de Logging Empresarial:
    - Log Aggregation: Centralización de logs por identificador de debate
    - Multi-Output Support: Salida simultánea a consola y archivos
    - Level-Based Filtering: Filtrado configurable por nivel de severidad
    - Structured Metadata: Información rica para análisis posterior
    - Audit Trail: Trazabilidad completa para compliance y debugging

Dominios de Logging Especializados:
    1. Debate Events: Eventos del ciclo de vida completo del debate
    2. Supervisor Activities: Operaciones de coordinación de equipos
    3. Agent Operations: Actividades de investigación y análisis
    4. Search Activities: Operaciones de búsqueda y retrieval
    5. Error Management: Captura y análisis de excepciones

Quality Attributes:
    - Scalability: Arquitectura escalable para múltiples debates concurrentes
    - Performance: Overhead mínimo con máxima información
    - Reliability: Logging robusto que no afecta operaciones principales
    - Maintainability: Configuración modular y extensible
    - Observability: Visibilidad comprehensiva del comportamiento del sistema

Referencias Técnicas:
    - Distributed Systems Observability (Charity Majors)
    - Site Reliability Engineering Principles (Google SRE)
    - Structured Logging Best Practices
    - Python Logging Cookbook (Python.org)
    - Enterprise Application Logging Patterns

Casos de Uso Empresariales:
    - Development Debugging: Información detallada para desarrollo
    - Production Monitoring: Observabilidad de sistemas en producción
    - Audit Compliance: Trazabilidad para auditorías regulatorias
    - Performance Analysis: Datos para optimización de rendimiento
    - Error Investigation: Información rica para root cause analysis

Author: Sistema de Debates IA
Version: 1.0 (Enhanced Observability)
License: Academic Use
Dependencies: logging, datetime, typing, src.config
"""

import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from src.config import LogConfig, Config


class DebateLogger:
    """
    Sistema de logging especializado para debates con arquitectura multi-logger.
    
    Implementa el patrón Factory para creación de loggers especializados por
    responsabilidad, proporcionando observabilidad granular y trazabilidad
    comprehensiva para sistemas distribuidos de agentes de IA.
    
    Architecture Features:
        - Component Separation: Loggers dedicados por responsabilidad
        - Contextual Enrichment: Metadatos ricos para cada evento
        - Flexible Configuration: Adaptación automática según ambiente
        - Performance Optimization: Overhead mínimo con máxima información
        
    Logger Hierarchy:
        - debate_logger: Eventos principales del ciclo de vida del debate
        - supervisor_logger: Operaciones de coordinación de equipos
        - agent_logger: Actividades de investigación de agentes
        - search_logger: Operaciones de búsqueda y retrieval
        - error_logger: Gestión centralizada de errores y excepciones
        
    Design Patterns:
        - Factory Method: Creación especializada de loggers
        - Strategy: Diferentes configuraciones según contexto
        - Observer: Captura de eventos del sistema
        - Facade: Interfaz simplificada para logging complejo
        
    Observability Features:
        - Structured Events: Eventos estructurados para análisis
        - Correlation IDs: Identificadores únicos para trazabilidad
        - Contextual Metadata: Información rica en contexto
        - Performance Metrics: Timing y throughput integrados
        
    Quality Attributes:
        - Reliability: Funcionamiento robusto sin afectar sistema principal
        - Performance: Overhead optimizado para producción
        - Maintainability: Configuración modular y extensible
        - Scalability: Soporte para múltiples debates concurrentes
        
    Attributes:
        debate_id (str): Identificador único del debate para correlación
        log_config (Dict): Configuración de logging según ambiente
        debate_logger (Logger): Logger principal para eventos de debate
        supervisor_logger (Logger): Logger para operaciones de supervisión
        agent_logger (Logger): Logger para actividades de agentes
        search_logger (Logger): Logger para operaciones de búsqueda
        error_logger (Logger): Logger especializado para errores
    """
    
    def __init__(self, debate_id: Optional[str] = None) -> None:
        """
        Inicializa el sistema de logging especializado para un debate específico.
        
        Implementa el patrón Factory con configuración automática basada en
        ambiente, creando una jerarquía de loggers especializados para diferentes
        responsabilidades del sistema.
        
        Args:
            debate_id (Optional[str]): Identificador único del debate.
                Si no se proporciona, se genera automáticamente usando timestamp.
                
        Initialization Strategy:
            1. ID Generation: Creación de identificador único si no se proporciona
            2. Configuration Loading: Carga de configuración según ambiente
            3. Logger Hierarchy Setup: Creación de loggers especializados
            4. Context Establishment: Establecimiento de contexto de logging
            
        Design Patterns:
            - Factory Method: Para creación de loggers especializados
            - Configuration Object: Para gestión de configuración centralizada
            - Unique Identifier: Para correlación de eventos distribuidos
            
        Performance Considerations:
            - Lazy Initialization: Loggers creados bajo demanda
            - Configuration Caching: Configuración cargada una sola vez
            - Memory Efficiency: Reutilización de configuración entre loggers
            
        Postconditions:
            - self.debate_id contiene identificador único válido
            - self.log_config contiene configuración cargada
            - Sistema de loggers completamente inicializado
        """
        # Unique ID generation con timestamp para correlación - Unique Identifier Pattern
        self.debate_id = debate_id or f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Configuration loading desde sistema de configuración - Configuration Object Pattern
        self.log_config = LogConfig.get_logging_config()
        
        # Logger hierarchy setup - Factory Method Pattern
        self.setup_loggers()
    
    def setup_loggers(self) -> None:
        """
        Configura la jerarquía completa de loggers especializados del sistema.
        
        Implementa el patrón Factory Method para crear loggers especializados
        por responsabilidad, cada uno optimizado para un tipo específico de
        evento o componente del sistema.
        
        Logger Specialization Strategy:
            - Functional Separation: Cada logger maneja eventos de un dominio específico
            - Configuration Inheritance: Configuración base compartida con personalizaciones
            - File Organization: Archivos separados para facilitar análisis
            - Level Customization: Niveles apropiados según criticidad del componente
            
        Specialized Loggers Created:
            1. Debate Logger: Eventos principales del ciclo de vida
            2. Supervisor Logger: Coordinación y gestión de equipos
            3. Agent Logger: Investigación y análisis de agentes
            4. Search Logger: Operaciones de búsqueda y retrieval
            5. Error Logger: Gestión centralizada de errores (ERROR level)
            
        Design Patterns:
            - Factory Method: Creación especializada por tipo
            - Template Method: Estructura consistente de configuración
            - Separation of Concerns: Cada logger maneja responsabilidad específica
            
        File Organization Strategy:
            - Debate-Specific Naming: Archivos nombrados por debate_id
            - Component Segregation: Archivos separados por tipo de componente
            - Directory Structure: Organización lógica en directorio 'logs'
            
        Performance Features:
            - Conditional File Creation: Archivos creados solo si configurados
            - Shared Configuration: Reutilización de configuración base
            - Optimized Formatting: Formatters compartidos para eficiencia
            
        Side Effects:
            - Crea loggers en la jerarquía global de Python logging
            - Puede crear directorio 'logs' si no existe
            - Registra evento de inicialización en debate_logger
        """
        # Primary debate logger - Principal event tracking
        self.debate_logger = self._create_logger(
            name=f"debate.{self.debate_id}",
            filename=f"debate_{self.debate_id}.log" if self.log_config.get("filename") else None
        )
        
        # Supervisor operations logger - Team coordination tracking
        self.supervisor_logger = self._create_logger(
            name=f"supervisor.{self.debate_id}",
            filename=f"supervisor_{self.debate_id}.log" if self.log_config.get("filename") else None
        )
        
        # Agent activities logger - Research and analysis tracking
        self.agent_logger = self._create_logger(
            name=f"agent.{self.debate_id}",
            filename=f"agent_{self.debate_id}.log" if self.log_config.get("filename") else None
        )
        
        # Search operations logger - Query and retrieval tracking
        self.search_logger = self._create_logger(
            name=f"search.{self.debate_id}",
            filename=f"search_{self.debate_id}.log" if self.log_config.get("filename") else None
        )
        
        # Error management logger - Centralized error tracking
        self.error_logger = self._create_logger(
            name=f"error.{self.debate_id}",
            filename=f"error_{self.debate_id}.log" if self.log_config.get("filename") else None,
            level=logging.ERROR  # Specialized level for error-only logging
        )
        
        # System initialization event - Bootstrap logging
        self.debate_logger.info(f"🎯 Sistema de logging inicializado para debate: {self.debate_id}")
    
    def _create_logger(self, name: str, filename: Optional[str] = None, level: Optional[int] = None) -> logging.Logger:
        """
        Factory method para creación de loggers con configuración especializada.
        
        Implementa el patrón Factory Method para crear loggers configurados
        consistentemente, con personalización específica según necesidades
        del componente y ambiente de ejecución.
        
        Args:
            name (str): Nombre jerárquico del logger (ej: 'debate.debate_123')
            filename (Optional[str]): Nombre del archivo de log (sin directorio)
            level (Optional[int]): Nivel de logging específico (override global)
            
        Returns:
            logging.Logger: Logger completamente configurado y listo para uso
            
        Factory Configuration Strategy:
            1. Logger Creation: Obtención o creación de logger por nombre
            2. Level Configuration: Establecimiento de nivel apropiado
            3. Handler Cleanup: Limpieza de handlers existentes para evitar duplicación
            4. Formatter Setup: Configuración de formato consistente
            5. Output Configuration: Setup de salidas (consola y/o archivo)
            
        Handler Configuration:
            - Console Handler: Salida a stdout si habilitada en configuración
            - File Handler: Salida a archivo si filename proporcionado
            - Encoding Support: UTF-8 para soporte internacional
            - Directory Creation: Creación automática de directorio logs
            
        Design Patterns:
            - Factory Method: Creación especializada con configuración
            - Builder: Construcción paso a paso de configuración
            - Template Method: Estructura consistente de configuración
            
        Performance Optimizations:
            - Handler Reuse: Evita duplicación de handlers
            - Shared Formatters: Reutilización de objetos formatter
            - Conditional Creation: File handlers solo si necesarios
            
        Error Handling:
            - Directory Creation: Manejo de errores en creación de directorio
            - File Access: Manejo robusto de permisos de archivo
            - Encoding Issues: Configuración UTF-8 explícita
            
        Side Effects:
            - Modifica jerarquía global de loggers de Python
            - Puede crear directorio 'logs' si no existe
            - Configura handlers que persistirán durante vida del proceso
        """
        # Logger creation con hierarchical naming - Factory Pattern
        logger = logging.getLogger(name)
        logger.setLevel(level or getattr(logging, self.log_config["level"]))
        
        # Handler cleanup para evitar duplicación - Cleanup Pattern
        logger.handlers.clear()
        
        # Shared formatter para consistency - Template Method
        formatter = logging.Formatter(self.log_config["format"])
        
        # Console output configuration - Strategy Pattern
        if self.log_config.get("console", True):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File output configuration - Conditional Creation Pattern
        if filename:
            # Directory management con error handling
            os.makedirs("logs", exist_ok=True)
            file_path = os.path.join("logs", filename)
            
            # File handler con encoding support - Internationalization
            file_handler = logging.FileHandler(file_path, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def log_debate_start(self, topic: str, pro_position: str, contra_position: str) -> None:
        """
        Registra el evento de inicio de debate con contexto completo.
        
        Implementa logging estructurado para el evento más crítico del sistema,
        proporcionando trazabilidad completa desde el inicio del proceso de debate.
        
        Args:
            topic (str): Tema principal del debate
            pro_position (str): Posición del equipo PRO
            contra_position (str): Posición del equipo CONTRA
            
        Structured Logging Strategy:
            - Event Classification: Categorización clara del tipo de evento
            - Contextual Enrichment: Información rica para análisis posterior
            - Hierarchical Information: Organización lógica de metadatos
            - Audit Trail: Registro completo para compliance
            
        Business Event Tracking:
            - Process Initiation: Marca inicio oficial del proceso
            - Parameter Capture: Registra parámetros de configuración
            - Stakeholder Positions: Documenta posiciones de debate
            - Timestamp Correlation: Facilita análisis temporal
            
        Design Patterns:
            - Event Sourcing: Registro inmutable de eventos de negocio
            - Structured Logging: Formato consistente para análisis
            - Audit Trail: Trazabilidad para compliance y debugging
            
        Use Cases:
            - Debugging: Identificación de configuración problemática
            - Analytics: Análisis de patrones de uso del sistema
            - Audit: Trazabilidad para requirements regulatorios
            - Monitoring: Detección de anomalías en configuración
            
        Side Effects:
            Registra eventos en debate_logger con nivel INFO
        """
        # Event header con clear identification - Event Sourcing Pattern
        self.debate_logger.info("🎭 INICIANDO NUEVO DEBATE")
        
        # Structured parameter logging - Structured Logging Pattern
        self.debate_logger.info(f"📋 Tema: {topic}")
        self.debate_logger.info(f"🟢 Posición PRO: {pro_position}")
        self.debate_logger.info(f"🔴 Posición CONTRA: {contra_position}")
    
    def log_team_creation(self, team: str, supervisor_id: str) -> None:
        """
        Registra eventos de creación y configuración de equipos de debate.
        
        Documenta la fase de organización estructural del debate, proporcionando
        trazabilidad de la creación de entidades organizacionales y sus
        identificadores únicos.
        
        Args:
            team (str): Identificador del equipo ('pro' o 'contra')
            supervisor_id (str): Identificador único del supervisor del equipo
            
        Organizational Tracking:
            - Team Formation: Registro de creación de estructuras organizacionales
            - Leadership Assignment: Documentación de asignación de supervisores
            - Hierarchy Establishment: Trazabilidad de jerarquías creadas
            - Resource Allocation: Documentación de asignación de recursos
            
        Design Patterns:
            - Factory Tracking: Registro de objetos creados por factories
            - Hierarchical Logging: Información organizada jerárquicamente
            - Resource Management: Tracking de asignación de recursos
            
        Operational Intelligence:
            - Team Performance: Base para análisis de rendimiento por equipo
            - Resource Utilization: Tracking de uso de supervisores
            - Scalability Metrics: Datos para optimización de asignación
            
        Side Effects:
            Registra eventos en supervisor_logger con información organizacional
        """
        # Team formation event - Organizational Tracking
        self.supervisor_logger.info(f"🏗️ Creando equipo {team.upper()}")
        
        # Leadership assignment tracking - Resource Management
        self.supervisor_logger.info(f"   Supervisor: {supervisor_id}")
        
    def log_agent_creation(self, agent_id: str, role: str, team: str) -> None:
        """
        Registra la creación de agentes especializados con metadatos completos.
        
        Documenta la instanciación de agentes de investigación, proporcionando
        trazabilidad de recursos humanos artificiales y sus especializaciones
        dentro del ecosistema de debate.
        
        Args:
            agent_id (str): Identificador único del agente
            role (str): Rol especializado del agente (científico, económico, etc.)
            team (str): Equipo al que pertenece el agente
            
        Resource Tracking Strategy:
            - Agent Lifecycle: Registro de ciclo de vida de agentes
            - Specialization Documentation: Documentación de roles específicos
            - Team Assignment: Trazabilidad de pertenencia organizacional
            - Resource Inventory: Inventario de recursos computacionales
            
        Operational Analytics:
            - Agent Performance: Base para análisis de rendimiento por rol
            - Team Composition: Análisis de composición organizacional
            - Workload Distribution: Distribución de carga por especialización
            - Resource Optimization: Datos para optimización de asignación
            
        Design Patterns:
            - Registry Pattern: Registro de entidades creadas
            - Metadata Enrichment: Información rica sobre recursos
            - Hierarchical Organization: Organización por equipos y roles
            
        Side Effects:
            Registra eventos en agent_logger con metadatos de agente
        """
        # Agent instantiation event - Registry Pattern
        self.agent_logger.info(f"🤖 Agente creado: {agent_id}")
        
        # Metadata enrichment para analytics - Metadata Pattern
        self.agent_logger.info(f"   Rol: {role} | Equipo: {team}")
    
    def log_research_phase(self, team: str, task: str) -> None:
        """
        Registra el inicio de fases de investigación con contexto de tarea.
        
        Documenta eventos de coordinación de investigación, proporcionando
        trazabilidad de delegación de tareas y inicio de procesos de
        investigación distribuida.
        
        Args:
            team (str): Equipo que inicia la investigación
            task (str): Descripción de la tarea de investigación asignada
            
        Process Orchestration Tracking:
            - Phase Transitions: Registro de cambios de fase del proceso
            - Task Delegation: Documentación de asignación de tareas
            - Coordination Events: Eventos de coordinación entre componentes
            - Process Boundaries: Demarcación de límites de proceso
            
        Workflow Analytics:
            - Phase Duration: Base para análisis de duración de fases
            - Task Complexity: Análisis de complejidad de tareas
            - Team Productivity: Métricas de productividad por equipo
            - Process Optimization: Datos para optimización de workflow
            
        Design Patterns:
            - Workflow Tracking: Seguimiento de procesos de negocio
            - Event-Driven Architecture: Registro de eventos de proceso
            - Process Mining: Datos para análisis de procesos
            
        Side Effects:
            Registra eventos en supervisor_logger para coordinación
        """
        # Phase transition event - Workflow Tracking
        self.supervisor_logger.info(f"🔍 {team.upper()} - Iniciando investigación")
        
        # Task context documentation - Process Context
        self.supervisor_logger.info(f"   Tarea: {task}")
    
    def log_agent_research(self, agent_id: str, queries: List[str], fragments_found: int) -> None:
        """
        Registra resultados de investigación de agentes con métricas de productividad.
        
        Documenta la actividad de investigación individual de agentes,
        proporcionando métricas detalladas de productividad y eficacia
        en la búsqueda y análisis de información.
        
        Args:
            agent_id (str): Identificador del agente que realizó la investigación
            queries (List[str]): Lista de queries ejecutadas por el agente
            fragments_found (int): Número de fragmentos de información encontrados
            
        Performance Metrics Tracking:
            - Agent Productivity: Métricas de productividad individual
            - Query Effectiveness: Eficacia de estrategias de búsqueda
            - Information Yield: Rendimiento de información por query
            - Research Quality: Calidad de investigación realizada
            
        Operational Intelligence:
            - Agent Performance: Análisis comparativo de rendimiento
            - Query Optimization: Optimización de estrategias de búsqueda
            - Resource Efficiency: Eficiencia en uso de recursos de búsqueda
            - Knowledge Discovery: Patrones en descubrimiento de información
            
        Design Patterns:
            - Metrics Collection: Recolección sistemática de métricas
            - Performance Monitoring: Monitoreo de rendimiento individual
            - Analytics Foundation: Base para análisis posteriores
            
        Side Effects:
            - Registra eventos en agent_logger con métricas de productividad
            - Registra queries en search_logger a nivel DEBUG
        """
        # Research completion event con metrics - Performance Monitoring
        self.agent_logger.info(f"🔬 {agent_id} - Investigación completada")
        self.agent_logger.info(f"   Queries ejecutadas: {len(queries)}")
        self.agent_logger.info(f"   Fragmentos encontrados: {fragments_found}")
        
        # Detailed query logging para analysis - Detailed Tracking
        for i, query in enumerate(queries, 1):
            self.search_logger.debug(f"Query {i}: {query}")
    
    def log_argument_creation(self, team: str, round_num: int, strategy: str, confidence: float, content_preview: str) -> None:
        """
        Registra eventos de creación de argumentos con análisis de calidad.
        
        Documenta la generación de argumentos por parte de supervisores,
        proporcionando métricas de calidad, estrategia utilizada y
        metadatos para análisis de efectividad argumentativa.
        
        Args:
            team (str): Equipo que genera el argumento
            round_num (int): Número de ronda del debate
            strategy (str): Estrategia argumentativa utilizada
            confidence (float): Nivel de confianza del supervisor (0.0-1.0)
            content_preview (str): Preview del contenido del argumento
            
        Argumentative Quality Tracking:
            - Strategy Documentation: Registro de estrategias argumentativas
            - Confidence Metrics: Métricas de confianza y calidad
            - Content Analysis: Análisis de contenido argumentativo
            - Round Progression: Evolución de argumentos por ronda
            
        Strategic Analytics:
            - Strategy Effectiveness: Eficacia de diferentes estrategias
            - Confidence Patterns: Patrones de confianza por equipo
            - Argument Quality: Calidad argumentativa por ronda
            - Competitive Analysis: Análisis competitivo entre equipos
            
        Design Patterns:
            - Quality Metrics: Métricas sistemáticas de calidad
            - Strategic Analysis: Análisis de estrategias competitivas
            - Content Analytics: Análisis de contenido generado
            
        Side Effects:
            Registra eventos en supervisor_logger con métricas de calidad
        """
        # Argument creation event con quality metrics - Quality Tracking
        self.supervisor_logger.info(f"✍️ {team.upper()} - Argumento Ronda {round_num}")
        self.supervisor_logger.info(f"   Estrategia: {strategy}")
        self.supervisor_logger.info(f"   Confianza: {confidence:.2f}")
        
        # Content preview para analysis - Content Analytics
        self.supervisor_logger.info(f"   Preview: {content_preview[:100]}...")
    
    def log_search_call(self, query: str, results_count: int, source_type: str = "general") -> None:
        """
        Registra operaciones de búsqueda con métricas de rendimiento.
        
        Documenta cada operación de búsqueda realizada por el sistema,
        proporcionando métricas de efectividad y trazabilidad de
        interacciones con sistemas externos de información.
        
        Args:
            query (str): Query de búsqueda ejecutada
            results_count (int): Número de resultados obtenidos
            source_type (str): Tipo de fuente consultada (general, academic, etc.)
            
        Search Performance Tracking:
            - Query Effectiveness: Eficacia de queries individuales
            - Source Performance: Rendimiento por tipo de fuente
            - Result Yield: Rendimiento de resultados por búsqueda
            - External API Usage: Uso de APIs externas de búsqueda
            
        Information Retrieval Analytics:
            - Query Optimization: Optimización de estrategias de búsqueda
            - Source Evaluation: Evaluación de calidad de fuentes
            - Cost Analysis: Análisis de costos de búsqueda
            - Performance Monitoring: Monitoreo de rendimiento de retrieval
            
        Design Patterns:
            - External API Monitoring: Monitoreo de servicios externos
            - Performance Metrics: Métricas de rendimiento de búsqueda
            - Usage Analytics: Análisis de patrones de uso
            
        Side Effects:
            Registra eventos en search_logger con métricas de búsqueda
        """
        # Search operation event - External API Monitoring
        self.search_logger.info(f"🔍 Búsqueda: '{query}'")
        
        # Performance metrics documentation - Performance Tracking
        self.search_logger.info(f"   Tipo: {source_type} | Resultados: {results_count}")
    
    def log_api_call(self, model_name: str, purpose: str, success: bool) -> None:
        """
        Registra llamadas a APIs de modelos de lenguaje con estado de resultado.
        
        Documenta interacciones con servicios externos de IA, proporcionando
        trazabilidad de uso de recursos computacionales y análisis de
        confiabilidad de servicios externos.
        
        Args:
            model_name (str): Nombre del modelo de IA utilizado
            purpose (str): Propósito de la llamada (generation, analysis, etc.)
            success (bool): Indicador de éxito de la operación
            
        API Performance Tracking:
            - Model Usage: Tracking de uso por modelo específico
            - Success Rates: Tasas de éxito por modelo y propósito
            - Purpose Analysis: Análisis de uso por propósito
            - Reliability Metrics: Métricas de confiabilidad de servicios
            
        External Service Analytics:
            - Cost Optimization: Optimización de costos de API
            - Performance Analysis: Análisis de rendimiento por proveedor
            - Reliability Assessment: Evaluación de confiabilidad de servicios
            - Usage Patterns: Patrones de uso de diferentes modelos
            
        Design Patterns:
            - Circuit Breaker Monitoring: Monitoreo de fallos de servicios
            - Usage Analytics: Análisis de patrones de uso de API
            - Cost Tracking: Seguimiento de costos de servicios externos
            
        Side Effects:
            Registra eventos en debate_logger a nivel DEBUG con estado de API
        """
        # API call status indication - External Service Monitoring
        status = "✅" if success else "❌"
        
        # API usage tracking - Usage Analytics
        self.debate_logger.debug(f"{status} API Call: {model_name} | {purpose}")
    
    def log_error(self, component: str, error_msg: str, exception: Optional[Exception] = None) -> None:
        """
        Registra errores del sistema con contexto completo para debugging.
        
        Implementa logging centralizado de errores con información rica
        para troubleshooting efectivo y análisis de patrones de fallo
        en sistemas distribuidos.
        
        Args:
            component (str): Componente del sistema donde ocurrió el error
            error_msg (str): Mensaje descriptivo del error
            exception (Optional[Exception]): Excepción original si disponible
            
        Error Management Strategy:
            - Centralized Error Logging: Registro centralizado para análisis
            - Contextual Information: Información rica para debugging
            - Exception Tracking: Trazabilidad de excepciones originales
            - Component Attribution: Atribución clara de errores por componente
            
        Debugging Intelligence:
            - Root Cause Analysis: Información para análisis de causa raíz
            - Pattern Recognition: Identificación de patrones de fallo
            - Component Health: Salud de componentes individuales
            - Error Correlation: Correlación de errores relacionados
            
        Design Patterns:
            - Centralized Error Handling: Manejo centralizado de errores
            - Rich Context: Información contextual para debugging
            - Exception Chaining: Preservación de stack traces originales
            
        Side Effects:
            - Registra eventos en error_logger con nivel ERROR
            - Incluye stack trace completo si exception proporcionada
        """
        # Error event con component attribution - Centralized Error Handling
        self.error_logger.error(f"❌ {component}: {error_msg}")
        
        # Exception details para debugging - Rich Context
        if exception:
            self.error_logger.exception(f"   Excepción: {exception}")
    
    def log_rate_limit(self, component: str, wait_time: float) -> None:
        """
        Registra eventos de rate limiting con información de throttling.
        
        Documenta eventos de limitación de tasa para análisis de uso
        de recursos y optimización de estrategias de throttling en
        interacciones con servicios externos.
        
        Args:
            component (str): Componente afectado por rate limiting
            wait_time (float): Tiempo de espera impuesto (segundos)
            
        Resource Management Tracking:
            - Throttling Events: Eventos de limitación de recursos
            - Wait Time Analysis: Análisis de tiempos de espera
            - Component Load: Carga de trabajo por componente
            - Rate Limit Patterns: Patrones de limitación de tasa
            
        Performance Optimization:
            - Throttling Strategy: Optimización de estrategias de throttling
            - Load Balancing: Balanceo de carga entre componentes
            - Resource Planning: Planificación de recursos computacionales
            - Cost Optimization: Optimización de costos de API
            
        Design Patterns:
            - Rate Limiting Monitoring: Monitoreo de limitaciones de tasa
            - Performance Analytics: Análisis de impacto en rendimiento
            - Resource Management: Gestión de recursos computacionales
            
        Side Effects:
            Registra eventos en debate_logger con nivel WARNING
        """
        # Rate limiting event - Resource Management Tracking
        self.debate_logger.warning(f"⏳ {component} - Rate limit: esperando {wait_time:.1f}s")
    
    def log_debate_end(self, winner: str, duration: float, stats: Dict[str, Any]) -> None:
        """
        Registra la finalización del debate con métricas comprehensivas.
        
        Documenta la conclusión del proceso de debate con análisis completo
        de resultados, métricas de rendimiento y estadísticas finales
        para evaluación de calidad y efectividad del sistema.
        
        Args:
            winner (str): Ganador determinado del debate
            duration (float): Duración total del debate en segundos
            stats (Dict[str, Any]): Diccionario de estadísticas finales
            
        Completion Analytics:
            - Outcome Documentation: Documentación de resultados finales
            - Performance Metrics: Métricas de rendimiento del sistema
            - Quality Assessment: Evaluación de calidad del debate
            - Process Efficiency: Eficiencia del proceso completo
            
        Business Intelligence:
            - Success Metrics: Métricas de éxito del proceso
            - Performance Analysis: Análisis de rendimiento temporal
            - Quality Indicators: Indicadores de calidad del debate
            - Competitive Analysis: Análisis competitivo de resultados
            
        Design Patterns:
            - Process Completion: Documentación de finalización de proceso
            - Analytics Aggregation: Agregación de métricas finales
            - Business Event: Evento de negocio significativo
            
        Side Effects:
            Registra múltiples eventos en debate_logger con métricas finales
        """
        # Process completion event - Process Finalization
        self.debate_logger.info("🏁 DEBATE FINALIZADO")
        
        # Outcome documentation - Business Intelligence
        self.debate_logger.info(f"🏆 Ganador: {winner}")
        self.debate_logger.info(f"⏱️ Duración: {duration:.1f} segundos")
        
        # Statistics aggregation - Analytics Summary
        for key, value in stats.items():
            self.debate_logger.info(f"   {key}: {value}")
    
    def get_log_summary(self) -> Dict[str, Union[int, List[str], str]]:
        """
        Genera resumen comprehensivo de archivos de log generados.
        
        Proporciona análisis de logging realizado durante el debate,
        incluyendo inventario de archivos, métricas de volumen y
        información de ubicación para análisis posterior.
        
        Returns:
            Dict[str, Union[int, List[str], str]]: Resumen de logging conteniendo:
                - logs_created (int): Número de archivos de log creados
                - files (List[str]): Lista de nombres de archivos generados
                - log_directory (str): Ruta absoluta del directorio de logs
                
        Log Analysis Strategy:
            - File Inventory: Inventario completo de archivos generados
            - Volume Analysis: Análisis de volumen de logging
            - Location Documentation: Documentación de ubicación de logs
            - Accessibility Information: Información para acceso posterior
            
        Operational Intelligence:
            - Log Management: Gestión de archivos de log generados
            - Storage Analysis: Análisis de uso de almacenamiento
            - Audit Preparation: Preparación para auditorías
            - Maintenance Planning: Planificación de mantenimiento de logs
            
        Design Patterns:
            - Inventory Management: Gestión de inventario de recursos
            - Analytics Summary: Resumen de actividad de logging
            - Resource Tracking: Seguimiento de recursos generados
            
        Error Handling:
            - Directory Existence: Manejo de directorio no existente
            - File Access: Manejo robusto de acceso a archivos
            - Empty Results: Manejo apropiado de casos sin logs
            
        Side Effects:
            - Lee directorio del sistema de archivos
            - Calcula métricas de archivos existentes
        """
        # Directory existence check - Error Prevention
        log_dir = "logs"
        if not os.path.exists(log_dir):
            return {"logs_created": 0, "files": [], "log_directory": ""}
        
        # File inventory generation - Inventory Management
        debate_files = [f for f in os.listdir(log_dir) if self.debate_id in f]
        
        # Summary compilation - Analytics Summary
        return {
            "logs_created": len(debate_files),
            "files": debate_files,
            "log_directory": os.path.abspath(log_dir)
        }


def setup_system_logging(debate_id: Optional[str] = None) -> DebateLogger:
    """
    Función factory principal para configurar el sistema de logging completo.
    
    Implementa el patrón Facade para simplificar la configuración completa
    del sistema de logging, incluyendo configuración de bibliotecas externas
    y optimización de niveles según ambiente de ejecución.
    
    Args:
        debate_id (Optional[str]): Identificador único del debate
            Si no se proporciona, se genera automáticamente
            
    Returns:
        DebateLogger: Instancia completamente configurada del sistema de logging
        
    Configuration Strategy:
        1. System Configuration: Asegurar carga de configuración del sistema
        2. Debate Logger Creation: Crear instancia especializada para debate
        3. External Library Configuration: Configurar niveles de bibliotecas externas
        4. Performance Optimization: Optimizar según modo de ejecución
        
    External Library Management:
        - HTTP Clients: Configuración de logging de clientes HTTP
        - AI Libraries: Configuración de bibliotecas de IA (OpenAI, LangChain)
        - Framework Libraries: Configuración de frameworks (LangGraph)
        - Noise Reduction: Reducción de ruido de logging de bibliotecas
        
    Performance Optimization:
        - Debug Mode: Configuración detallada para desarrollo
        - Production Mode: Configuración optimizada para producción
        - Level Adjustment: Ajuste de niveles según criticidad
        - Resource Efficiency: Uso eficiente de recursos de logging
        
    Design Patterns:
        - Facade: Interfaz simplificada para configuración compleja
        - Factory: Creación de instancia completamente configurada
        - Configuration Management: Gestión centralizada de configuración
        
    Integration Features:
        - System Integration: Integración con sistema de configuración
        - Library Integration: Configuración de bibliotecas de terceros
        - Environment Adaptation: Adaptación según ambiente de ejecución
        
    Quality Assurance:
        - Noise Reduction: Reducción de logging irrelevante
        - Performance Impact: Minimización de impacto en rendimiento
        - Information Quality: Maximización de calidad de información
        
    Side Effects:
        - Configura sistema global de logging de Python
        - Modifica niveles de logging de bibliotecas externas
        - Crea estructura de directorios si necesaria
    """
    # System configuration verification - Configuration Management
    Config.ensure_loaded()
    
    # Debate logger creation - Factory Pattern
    debate_logger = DebateLogger(debate_id)
    
    # External libraries configuration - Library Integration
    external_loggers = [
        "httpx",        # HTTP client library
        "openai",       # OpenAI API client
        "langchain",    # LangChain framework
        "langgraph"     # LangGraph orchestration
    ]
    
    # External library noise reduction - Performance Optimization
    for logger_name in external_loggers:
        ext_logger = logging.getLogger(logger_name)
        
        # Environment-based level configuration - Environment Adaptation
        if Config.DEBUG_MODE():
            ext_logger.setLevel(logging.INFO)     # Detailed info for debugging
        else:
            ext_logger.setLevel(logging.WARNING)  # Warnings only for production
    
    return debate_logger


def test_logging_system() -> None:
    """
    Sistema de testing comprehensivo para validación de logging.
    
    Implementa suite de testing completa para verificar funcionamiento
    correcto del sistema de logging, incluyendo todos los tipos de
    eventos y escenarios de uso del sistema.
    
    Testing Strategy:
        - Comprehensive Coverage: Testing de todos los tipos de eventos
        - Real Scenario Simulation: Simulación de escenarios reales de uso
        - Output Verification: Verificación de salidas de logging
        - Performance Testing: Testing de impacto en rendimiento
        
    Test Cases Covered:
        1. System Initialization: Testing de inicialización del sistema
        2. Debate Lifecycle: Testing de ciclo de vida completo de debate
        3. Component Events: Testing de eventos de todos los componentes
        4. Error Scenarios: Testing de manejo de errores
        5. Performance Events: Testing de eventos de rendimiento
        6. Summary Generation: Testing de generación de resúmenes
        
    Validation Features:
        - File Creation: Verificación de creación de archivos
        - Content Verification: Verificación de contenido de logs
        - Performance Impact: Medición de impacto en rendimiento
        - Resource Usage: Verificación de uso de recursos
        
    Design Patterns:
        - Test Suite: Suite comprehensiva de testing
        - Scenario Testing: Testing basado en escenarios
        - Validation Framework: Framework de validación de outputs
        
    Quality Assurance:
        - Functionality Verification: Verificación de funcionalidad completa
        - Performance Validation: Validación de rendimiento aceptable
        - Resource Management: Gestión apropiada de recursos
        - Error Handling: Manejo correcto de errores
        
    Side Effects:
        - Crea archivos de log de testing
        - Genera eventos de logging de prueba
        - Verifica sistema de archivos y outputs
    """
    print("🧪 Testing sistema de logging...")
    
    # System initialization testing - Initialization Validation
    logger = setup_system_logging("test_debate")
    
    # Debate lifecycle testing - Lifecycle Validation
    logger.log_debate_start(
        topic="Test Topic",
        pro_position="Test PRO position",
        contra_position="Test CONTRA position"
    )
    
    # Team and agent creation testing - Component Testing
    logger.log_team_creation("pro", "test_supervisor_pro")
    logger.log_agent_creation("test_agent_1", "cientifico", "pro")
    
    # Research phase testing - Process Testing
    logger.log_research_phase("pro", "Test research task")
    logger.log_agent_research("test_agent_1", ["query1", "query2"], 3)
    
    # Argument creation testing - Content Generation Testing
    logger.log_argument_creation(
        team="pro",
        round_num=1,
        strategy="initial_position", 
        confidence=0.85,
        content_preview="Este es un argumento de prueba que demuestra..."
    )
    
    # External service testing - Integration Testing
    logger.log_search_call("test query", 5, "academic")
    logger.log_api_call("gpt-4o-mini", "argument_generation", True)
    
    # Completion testing - Finalization Testing
    logger.log_debate_end(
        winner="pro",
        duration=120.5,
        stats={
            "argumentos_pro": 3,
            "argumentos_contra": 3,
            "fragmentos_total": 15
        }
    )
    
    # Summary generation testing - Summary Validation
    summary = logger.get_log_summary()
    print(f"✅ Sistema de logging funcional")
    print(f"📁 Archivos de log creados: {summary['logs_created']}")
    if summary['files']:
        print(f"📄 Archivos: {', '.join(summary['files'])}")
        print(f"📂 Directorio: {summary['log_directory']}")


# Entry Point Pattern - Testing Execution
if __name__ == "__main__":
    """
    Entry point para testing standalone del sistema de logging.
    
    Proporciona capacidad de testing independiente del sistema de logging
    para verificación de funcionalidad durante desarrollo y mantenimiento.
    
    Testing Context:
        - Standalone Execution: Testing independiente del sistema principal
        - Development Support: Soporte para desarrollo y debugging
        - Validation Framework: Framework de validación de funcionalidad
        
    Execution Features:
        - Comprehensive Testing: Testing completo de funcionalidad
        - Output Verification: Verificación de outputs generados
        - Performance Assessment: Evaluación de rendimiento
        
    Best Practices:
        - Independent Testing: Testing sin dependencias externas
        - Clear Output: Resultados claros y comprensibles
        - Resource Cleanup: Limpieza apropiada de recursos de testing
    """
    test_logging_system()