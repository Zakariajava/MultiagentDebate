"""
Sistema de Validación Integral para Plataforma de Debates con Inteligencia Artificial.

Este módulo implementa un validador comprehensivo que verifica la correcta configuración
y funcionamiento de todos los componentes del sistema de debates automatizados. Aplica
el patrón Health Check y Strategy Pattern para realizar validaciones modulares y
escalables de diferentes subsistemas.

Arquitectura de Validación:
    - Health Check Pattern: Verificación sistemática de componentes
    - Strategy Pattern: Diferentes estrategias de validación por subsistema
    - Collector Pattern: Acumulación estructurada de resultados
    - Fail-Fast Principle: Detección temprana de errores críticos

Subsistemas Validados:
    1. Dependencias e Importaciones (Import System)
    2. Variables de Entorno (Environment Configuration)
    3. Modelos de Lenguaje (LLM Connectivity)
    4. Sistema de Búsqueda (Search Engine Integration)
    5. Componentes de Debate (Domain Logic Components)

Patrones de Diseño Implementados:
    - Health Check: Para verificación de estado de componentes
    - Strategy: Para diferentes tipos de validación
    - Template Method: Estructura consistente de tests
    - Collector: Para agregación de resultados
    - Observer: Para reporting de progreso

Principios de Calidad de Software:
    - Defensive Programming: Validación exhaustiva de precondiciones
    - Fail-Fast: Detección temprana de errores de configuración
    - Separation of Concerns: Validación modular por responsabilidad
    - Single Responsibility: Cada método valida un aspecto específico

Referencias Técnicas:
    - Clean Architecture: Validación de capas de infraestructura
    - SOLID Principles: Aplicación de SRP y OCP
    - Test-Driven Development: Principios de testing aplicados a validación
    - Domain-Driven Design: Validación centrada en el dominio de debates

Métricas de Calidad:
    - Code Coverage: Validación de todos los componentes críticos
    - Error Detection: Categorización de errores, warnings y éxitos
    - Performance Monitoring: Medición de tiempos de validación
    - Usability: Feedback claro y accionable para el usuario

Author: Sistema de Debates IA
Version: 1.0
License: Academic Use
Dependencies: src.config, src.utils, logging, datetime
"""

import sys
import os
from typing import List, Dict, Any, Tuple, Optional, Union
from datetime import datetime
import logging

# Configuración del path del proyecto - Dependency Injection Pattern
# Permite importaciones relativas desde el directorio raíz del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importaciones del sistema - Layered Architecture
# Cada importación representa una capa específica del sistema
from src.config import Config, ConfigValidator, LogConfig
from src.utils.github_models import github_models
from src.utils.search import SearchSystem


class SystemValidator:
    """
    Validador integral del sistema de debates con arquitectura modular.
    
    Implementa el patrón Health Check para verificar sistemáticamente el estado
    de todos los componentes del sistema antes de la ejecución de debates.
    Utiliza el patrón Collector para agregar resultados de validación de manera
    estructurada y escalable.
    
    Attributes:
        errors (List[str]): Colección de errores críticos encontrados
        warnings (List[str]): Colección de advertencias no críticas
        successes (List[str]): Colección de validaciones exitosas
        
    Design Patterns:
        - Health Check: Verificación sistemática de componentes
        - Collector: Agregación estructurada de resultados
        - Strategy: Diferentes enfoques de validación por subsistema
        - Template Method: Estructura consistente de validación
        
    Architecture Benefits:
        - Modular Validation: Cada subsistema se valida independientemente
        - Scalable Design: Fácil adición de nuevos tipos de validación
        - Clear Reporting: Categorización clara de resultados
        - User-Friendly: Feedback accionable y específico
        
    Quality Attributes:
        - Reliability: Detección consistente de problemas
        - Maintainability: Código modular y bien estructurado
        - Usability: Mensajes claros y soluciones sugeridas
        - Performance: Validación eficiente y rápida
    """
    
    def __init__(self) -> None:
        """
        Inicializa el validador con colectores vacíos para resultados.
        
        Implementa el patrón Constructor con inicialización de estado limpio,
        siguiendo el principio de Separation of Concerns donde cada instancia
        mantiene su propio estado de validación.
        
        Postconditions:
            - self.errors está inicializado como lista vacía
            - self.warnings está inicializado como lista vacía  
            - self.successes está inicializado como lista vacía
            
        Complexity:
            Tiempo: O(1) - Inicialización constante
            Espacio: O(1) - Almacenamiento de tres listas vacías
        """
        # Inicialización de colectores - Collector Pattern
        self.errors: List[str] = []      # Errores críticos que impiden ejecución
        self.warnings: List[str] = []    # Advertencias que afectan rendimiento
        self.successes: List[str] = []   # Validaciones exitosas para confirmación
        
    def print_header(self, title: str) -> None:
        """
        Renderiza un header visual para secciones de validación.
        
        Implementa principios de User Interface Design para mejorar la legibilidad
        del output de validación, aplicando Visual Hierarchy mediante separadores
        y formateo consistente.
        
        Args:
            title (str): Título de la sección a mostrar
            
        Design Principles:
            - Visual Hierarchy: Separación clara de secciones
            - Consistency: Formato estándar para todos los headers
            - Readability: Uso de caracteres ASCII para compatibilidad
            
        Side Effects:
            Imprime contenido formateado en stdout
        """
        print("\n" + "="*60)  # Separador superior con longitud fija
        print(f"🔍 {title}")   # Título con emoji para identificación visual
        print("="*60)         # Separador inferior matching

    def print_section(self, title: str) -> None:
        """
        Renderiza un subsection header para organización jerárquica.
        
        Complementa print_header() para crear una jerarquía visual de dos niveles,
        facilitando la navegación y comprensión del output de validación.
        
        Args:
            title (str): Título de la subsección
            
        Visual Design:
            - Shorter separators para jerarquía visual
            - Consistent spacing para ritmo de lectura
            - Clear demarcation entre subsecciones
            
        Side Effects:
            Imprime contenido formateado en stdout
        """
        print(f"\n{'='*20} {title} {'='*20}")

    def validate_environment(self) -> None:
        """
        Valida la configuración de variables de entorno del sistema.
        
        Implementa el patrón Specification para verificar que todas las variables
        de entorno requeridas estén configuradas correctamente. Utiliza el
        ConfigValidator existente para delegar la lógica de validación específica.
        
        Validation Strategy:
            1. Delegación a ConfigValidator para reglas de negocio
            2. Categorización de errores vs warnings
            3. Reporting estructurado de resultados
            4. Feedback accionable para corrección
            
        Business Rules Validated:
            - Variables de entorno requeridas presentes
            - Valores de configuración dentro de límites válidos
            - Tokens de API con formato correcto
            - Configuración de modelos disponible
            
        Design Patterns:
            - Delegation: Uso de ConfigValidator para lógica específica
            - Specification: Validación de reglas de negocio
            - Observer: Reporting de progreso y resultados
            
        Side Effects:
            - Imprime resultados de validación
            - Actualiza self.errors, self.warnings, self.successes
        """
        self.print_section("VARIABLES DE ENTORNO")
        
        # Delegación a ConfigValidator - Delegation Pattern
        validation_report = ConfigValidator.get_validation_report()
        
        # Procesamiento de errores de entorno - Error Handling
        env_errors = validation_report["environment_errors"]
        if env_errors:
            print("❌ ERRORES EN CONFIGURACIÓN:")
            for error in env_errors:
                print(f"   - {error}")
                self.errors.append(f"Environment: {error}")
        else:
            print("✅ Todas las variables de entorno están configuradas")
            self.successes.append("Variables de entorno configuradas")
        
        # Procesamiento de advertencias de límites - Warning Handling
        limits_warnings = validation_report["limits_warnings"]
        if limits_warnings:
            print("\n⚠️ ADVERTENCIAS DE LÍMITES:")
            for warning in limits_warnings:
                print(f"   - {warning}")
                self.warnings.append(f"Limits: {warning}")
        else:
            print("✅ Límites de configuración son razonables")
            self.successes.append("Límites apropiados")

    def validate_models(self) -> None:
        """
        Valida la conectividad y funcionalidad de modelos de lenguaje.
        
        Implementa el patrón Circuit Breaker para testing de conexiones externas,
        verificando tanto la conectividad general como la funcionalidad específica
        de cada tipo de modelo utilizado en el sistema.
        
        Model Testing Strategy:
            1. Conectividad general con GitHub Models
            2. Test funcional de Supervisor PRO model
            3. Test funcional de Supervisor CONTRA model  
            4. Test funcional de Agent models
            5. Validation de respuestas esperadas
            
        Design Patterns:
            - Circuit Breaker: Para manejo de servicios externos
            - Template Method: Estructura consistente de tests
            - Strategy: Diferentes enfoques por tipo de modelo
            
        Error Handling:
            - Graceful degradation en caso de fallas
            - Categorización de errores por tipo de modelo
            - Feedback específico para troubleshooting
            
        Performance Considerations:
            - Tests ligeros para minimizar latencia
            - Timeouts apropiados para servicios externos
            - Retry logic implícito en github_models
            
        Side Effects:
            - Realiza llamadas a APIs externas
            - Actualiza colectores de resultados
            - Imprime progreso y resultados
        """
        self.print_section("MODELOS LLM")
        
        try:
            # Test de conectividad general - Circuit Breaker Pattern
            if github_models.test_connection():
                print("✅ Conexión con GitHub Models exitosa")
                self.successes.append("GitHub Models conectado")
                
                # Importación de factory functions - Factory Pattern
                from src.utils.github_models import get_supervisor_pro_model, get_supervisor_contra_model, get_agent_model
                
                # Validation de Supervisor PRO - Template Method
                try:
                    model_pro = get_supervisor_pro_model(temperature=0.1)
                    response = model_pro.invoke("Di solo 'OK' si funcionas")
                    # Validation de respuesta esperada - Specification Pattern
                    if "OK" in response.content.upper():
                        print("✅ Modelo Supervisor PRO funcionando")
                        self.successes.append("Supervisor PRO operativo")
                    else:
                        print("⚠️ Supervisor PRO responde pero de manera inesperada")
                        self.warnings.append("Supervisor PRO respuesta inesperada")
                except Exception as e:
                    print(f"❌ Error en Supervisor PRO: {e}")
                    self.errors.append(f"Supervisor PRO: {e}")
                
                # Validation de Supervisor CONTRA - Template Method (variante)
                try:
                    model_contra = get_supervisor_contra_model(temperature=0.1)
                    response = model_contra.invoke("Di solo 'OK' si funcionas")
                    # Validation de respuesta esperada - Specification Pattern
                    if "OK" in response.content.upper():
                        print("✅ Modelo Supervisor CONTRA funcionando")
                        self.successes.append("Supervisor CONTRA operativo")
                    else:
                        print("⚠️ Supervisor CONTRA responde pero de manera inesperada")
                        self.warnings.append("Supervisor CONTRA respuesta inesperada")
                except Exception as e:
                    print(f"❌ Error en Supervisor CONTRA: {e}")
                    self.errors.append(f"Supervisor CONTRA: {e}")
                
                # Validation de modelos de Agentes - Template Method (variante)
                try:
                    agent_model = get_agent_model(temperature=0.1)
                    response = agent_model.invoke("Di solo 'OK' si funcionas")
                    # Validation de respuesta esperada - Specification Pattern
                    if "OK" in response.content.upper():
                        print("✅ Modelo de Agentes funcionando")
                        self.successes.append("Modelo de Agentes operativo")
                    else:
                        print("⚠️ Modelo de Agentes responde pero de manera inesperada")
                        self.warnings.append("Modelo de Agentes respuesta inesperada")
                except Exception as e:
                    print(f"❌ Error en Modelo de Agentes: {e}")
                    self.errors.append(f"Modelo de Agentes: {e}")
                    
            else:
                print("❌ No se puede conectar con GitHub Models")
                self.errors.append("GitHub Models no disponible")
                
        except Exception as e:
            # Global exception handling - Defensive Programming
            print(f"❌ Error general en modelos: {e}")
            self.errors.append(f"Modelos generales: {e}")

    def validate_search_system(self) -> None:
        """
        Valida la configuración y funcionalidad del sistema de búsqueda.
        
        Implementa validation estratégica del sistema de búsqueda, verificando
        tanto la configuración como la funcionalidad operativa. Proporciona
        guidance específico para resolución de problemas de configuración.
        
        Search System Validation Strategy:
            1. Verificación de estado de configuración
            2. Test de funcionalidad básica de búsqueda
            3. Validation de integración con APIs externas
            4. Guidance para troubleshooting
            
        Validation Layers:
            - Configuration Layer: API keys y dependencias
            - Integration Layer: Conectividad con servicios
            - Functional Layer: Ejecución de búsquedas reales
            - Performance Layer: Respuesta y calidad de resultados
            
        Design Patterns:
            - Strategy: Diferentes enfoques de validation
            - Facade: Interfaz simplificada para validation
            - Observer: Reporting detallado de estado
            
        User Experience:
            - Clear status reporting con símbolos visuales
            - Actionable guidance para configuración
            - Differentiated feedback para diferentes problemas
            
        Side Effects:
            - Puede realizar búsquedas reales para testing
            - Actualiza colectores de resultados
            - Proporciona guidance de configuración
        """
        self.print_section("SISTEMA DE BÚSQUEDA")
        
        try:
            # Instanciación del sistema de búsqueda - Factory Pattern
            search_system = SearchSystem()
            status = search_system.get_status()
            
            # Display detallado de estado - Observer Pattern
            print(f"📊 Estado del sistema de búsqueda:")
            for key, value in status.items():
                symbol = "✅" if value else "❌"  # Visual feedback mapping
                print(f"   {symbol} {key}: {value}")
            
            # Conditional functional testing - Strategy Pattern
            if status["can_search"]:
                # Test de búsqueda real - Integration Testing
                try:
                    results = search_system.search("test python programming", max_results=1)
                    if results:
                        print("✅ Búsqueda de prueba exitosa")
                        self.successes.append("Sistema de búsqueda operativo")
                    else:
                        print("⚠️ Búsqueda funciona pero no devolvió resultados")
                        self.warnings.append("Búsqueda sin resultados")
                except Exception as e:
                    print(f"❌ Error en búsqueda de prueba: {e}")
                    self.errors.append(f"Búsqueda: {e}")
            else:
                # Configuration guidance - Help System Pattern
                print("❌ Sistema de búsqueda no puede funcionar")
                self.errors.append("Sistema de búsqueda no configurado")
                print("💡 Para habilitar búsquedas:")
                print("   1. Obtén API key en: https://tavily.com/")
                print("   2. Agrégala a .env: TAVILY_API_KEY=tu_key_aqui")
                
        except Exception as e:
            # Global exception handling con contexto específico
            print(f"❌ Error general en sistema de búsqueda: {e}")
            self.errors.append(f"Búsqueda general: {e}")

    def validate_debate_components(self) -> None:
        """
        Valida la funcionalidad de componentes específicos del dominio de debates.
        
        Implementa validation de componentes core del sistema, verificando que
        los elementos fundamentales del dominio de debates puedan ser instanciados
        y configurados correctamente.
        
        Component Testing Strategy:
            1. SlaveAgent instantiation y configuración
            2. SupervisorAgent creation y setup
            3. DebateOrchestrator initialization
            4. DebateConfig validation
            
        Domain Validation:
            - Core business objects creation
            - Configuration object validity
            - Integration between components
            - System readiness for debates
            
        Design Patterns:
            - Factory: Para creation de objetos de dominio
            - Builder: Para configuración compleja
            - Template Method: Estructura consistente de tests
            
        Quality Assurance:
            - Unit-level testing de componentes
            - Integration readiness verification
            - Configuration validation
            - Error detection temprana
            
        Architecture Validation:
            - Layered architecture integrity
            - Dependency injection functionality
            - Component lifecycle management
            - Interface contract compliance
            
        Side Effects:
            - Instancia objetos del dominio para testing
            - Actualiza colectores de resultados
            - Valida configuración de clases
        """
        self.print_section("COMPONENTES DEL DEBATE")
        
        try:
            # Validation de SlaveAgent - Domain Object Testing
            from src.agents.SlaveAgent import SlaveAgent
            from src.config import AgentRole
            
            # Test de instanciación con configuración mínima
            test_agent = SlaveAgent(role=AgentRole.CIENTIFICO, team="pro")
            print("✅ SlaveAgent se puede crear")
            self.successes.append("SlaveAgent funcional")
            
            # Validation de SupervisorAgent - Aggregate Root Testing
            from src.agents.SupervisorAgent import SupervisorAgent
            
            # Test de instanciación con dependencias complejas
            test_supervisor = SupervisorAgent(
                team="pro",
                position="Test position",
                supervisor_id="test_supervisor"
            )
            print("✅ SupervisorAgent se puede crear")
            self.successes.append("SupervisorAgent funcional")
            
            # Validation de DebateOrchestrator - Application Service Testing
            from src.agents.debate_graph import DebateOrchestrator, DebateConfig
            
            # Test de instanciación de orquestador principal
            orchestrator = DebateOrchestrator()
            print("✅ DebateOrchestrator se puede crear")
            self.successes.append("DebateOrchestrator funcional")
            
            # Validation de DebateConfig - Value Object Testing
            config = DebateConfig(
                topic="Test topic",
                pro_position="Test pro position",
                contra_position="Test contra position",
                max_rounds=1
            )
            print("✅ DebateConfig se puede crear")
            self.successes.append("DebateConfig funcional")
            
        except Exception as e:
            # Domain-specific error handling
            print(f"❌ Error en componentes del debate: {e}")
            self.errors.append(f"Componentes del debate: {e}")

    def validate_imports(self) -> None:
        """
        Valida la disponibilidad de todas las dependencias críticas del sistema.
        
        Implementa dependency checking comprehensivo para asegurar que todas
        las bibliotecas externas requeridas estén instaladas y sean importables.
        Utiliza el patrón Strategy para different tipos de dependencias.
        
        Dependency Categories:
            - Core Framework Dependencies: LangGraph, LangChain
            - AI/ML Dependencies: OpenAI, model libraries
            - External API Dependencies: Tavily para búsquedas
            - Standard Library Dependencies: datetime, dataclasses, etc.
            - Utility Dependencies: python-dotenv, logging
            
        Testing Strategy:
            1. Importación dinámica de cada dependencia
            2. Categorización de dependencias críticas vs opcionales
            3. Reporting detallado de status de cada dependencia
            4. Guidance para instalación de dependencias faltantes
            
        Design Patterns:
            - Strategy: Diferentes enfoques por tipo de dependencia
            - Iterator: Procesamiento sistemático de lista de dependencias
            - Observer: Reporting detallado de progreso
            
        Error Handling:
            - ImportError catching específico
            - Graceful handling de dependencias opcionales
            - Clear guidance para resolución de problemas
            
        Complexity:
            Tiempo: O(n) donde n es el número de dependencias
            Espacio: O(1) - Solo almacenamiento de resultado actual
        """
        self.print_section("DEPENDENCIAS E IMPORTACIONES")
        
        # Definición de dependencias críticas - Strategy Pattern
        # Cada tupla define (module_name, display_name) para testing
        required_imports: List[Tuple[str, str]] = [
            ("langgraph", "LangGraph"),        # Core framework para orquestación
            ("langchain", "LangChain"),        # Framework base para LLM
            ("openai", "OpenAI"),              # Cliente para modelos OpenAI
            ("tavily", "Tavily"),              # Cliente para búsquedas web
            ("dotenv", "python-dotenv"),       # Manejo de variables de entorno
            ("datetime", "datetime"),          # Manejo de fechas y timestamps
            ("dataclasses", "dataclasses"),   # Data structures para configuración
            ("enum", "enum"),                  # Enumeraciones para tipos seguros
            ("logging", "logging")             # Sistema de logging
        ]
        
        # Iteración de validation de dependencias - Iterator Pattern
        for module, name in required_imports:
            try:
                # Dynamic import testing - Strategy Pattern
                __import__(module)
                print(f"✅ {name} importado correctamente")
                self.successes.append(f"{name} disponible")
            except ImportError:
                # Dependency missing handling - Error Recovery
                print(f"❌ {name} no está instalado")
                self.errors.append(f"{name} faltante")

    def run_full_validation(self) -> bool:
        """
        Ejecuta el proceso completo de validación del sistema.
        
        Implementa el patrón Template Method para coordinar todas las validaciones
        específicas en una secuencia lógica y coherente. Proporciona timing
        information y resumen comprehensivo de resultados.
        
        Validation Sequence:
            1. Dependencies and imports validation
            2. Environment configuration validation
            3. LLM models connectivity validation
            4. Search system functionality validation
            5. Domain components validation
            6. Results aggregation and reporting
            
        Returns:
            bool: True si el sistema está listo para debates, False en caso contrario
            
        Decision Logic:
            - Errores críticos -> Sistema no listo (False)
            - Solo warnings -> Sistema listo con recomendaciones (True)
            - Sin errores ni warnings -> Sistema completamente listo (True)
            
        Design Patterns:
            - Template Method: Secuencia fija con pasos variables
            - Strategy: Diferentes tipos de validación
            - Observer: Reporting detallado de progreso y resultados
            
        Performance Monitoring:
            - Timing de validación completa
            - Conteo de resultados por categoría
            - Reporting de métricas de calidad
            
        User Experience:
            - Progress indication durante validación
            - Clear categorization de resultados
            - Actionable recommendations
            - Next steps guidance
            
        Quality Metrics:
            - Error count y categorization
            - Warning count y impact assessment  
            - Success rate y component readiness
            - Overall system health score
        """
        self.print_header("VALIDACIÓN COMPLETA DEL SISTEMA DE DEBATES")
        
        # Performance monitoring - Timing Pattern
        start_time = datetime.now()
        
        print("🎯 Validando que el sistema esté listo para debates reales...")
        
        # Ejecución secuencial de validaciones - Template Method Pattern
        # Orden específico para dependencies y logical flow
        self.validate_imports()           # 1. Base dependencies first
        self.validate_environment()       # 2. Configuration after dependencies
        self.validate_models()            # 3. External services after config
        self.validate_search_system()     # 4. Additional services
        self.validate_debate_components() # 5. Domain components last
        
        # Performance measurement - Metrics Collection
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Results aggregation y reporting - Observer Pattern
        self.print_section("RESUMEN DE VALIDACIÓN")
        
        print(f"⏱️ Validación completada en: {duration}")
        print(f"✅ Éxitos: {len(self.successes)}")
        print(f"⚠️ Advertencias: {len(self.warnings)}")
        print(f"❌ Errores: {len(self.errors)}")
        
        # Decision logic basada en results - Strategy Pattern
        if self.errors:
            # Critical errors present - System not ready
            print("\n❌ ERRORES CRÍTICOS ENCONTRADOS:")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
            print("\n🔧 ACCIÓN REQUERIDA: Corregir errores antes de ejecutar debates")
            return False
        
        elif self.warnings:
            # Warnings present but no critical errors - System ready with caveats
            print("\n⚠️ ADVERTENCIAS ENCONTRADAS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
            print("\n💡 RECOMENDACIÓN: Revisar advertencias para mejor rendimiento")
            return True
        
        else:
            # No errors or warnings - System fully ready
            print("\n🎉 ¡SISTEMA COMPLETAMENTE LISTO!")
            print("✅ Todos los componentes funcionan correctamente")
            print("🚀 Puedes ejecutar debates sin problemas")
            return True

    def get_system_info(self) -> None:
        """
        Muestra información detallada de la configuración actual del sistema.
        
        Implementa el patrón Information Display para proporcionar una vista
        comprehensiva del estado de configuración del sistema. Útil para
        debugging y verificación de configuración.
        
        Information Categories:
            - Core Configuration: Límites y parámetros principales
            - Environment Configuration: Settings específicos del ambiente
            - Operational Parameters: Configuración de runtime
            - Debug Settings: Configuración de desarrollo
            
        Display Strategy:
            1. Configuration loading y verification
            2. Structured information presentation
            3. Environment-specific settings
            4. Hierarchical information organization
            
        Design Patterns:
            - Information Expert: Config object knows its own state
            - Observer: Structured reporting of system state
            - Template Method: Consistent information display
            
        Data Sources:
            - Config class methods para core settings
            - Environment configuration para context-specific settings
            - Runtime parameters para operational state
            
        User Value:
            - System transparency para troubleshooting
            - Configuration verification para admins
            - Documentation de current state
            - Baseline establishment para comparisons
        """
        self.print_section("INFORMACIÓN DEL SISTEMA")
        
        # Asegurar que la configuración esté cargada - Lazy Loading
        Config.ensure_loaded()
        
        # Core configuration display - Information Expert Pattern
        print(f"🔧 Configuración actual:")
        print(f"   - MAX_ROUNDS: {Config.MAX_ROUNDS()}")                    # Límite de rondas de debate
        print(f"   - AGENTS_PER_TEAM: {Config.AGENTS_PER_TEAM()}")          # Agentes por equipo
        print(f"   - MAX_FRAGMENTS_PER_AGENT: {Config.MAX_FRAGMENTS_PER_AGENT}")  # Límite de evidencia
        print(f"   - MAX_QUERIES_PER_AGENT: {Config.MAX_QUERIES_PER_AGENT}")     # Límite de búsquedas
        print(f"   - MIN_FRAGMENT_SCORE: {Config.MIN_FRAGMENT_SCORE}")           # Umbral de calidad
        print(f"   - DEBUG_MODE: {Config.DEBUG_MODE()}")                     # Estado de debug
        
        # Environment-specific configuration - Context Awareness
        env_config = Config.get_environment_config()
        print(f"\n🌍 Configuración de ambiente:")
        for key, value in env_config.items():
            print(f"   - {key}: {value}")


def main() -> bool:
    """
    Función principal para ejecutar el proceso completo de validación.
    
    Implementa el patrón Main Controller para coordinar el flujo principal
    de validación del sistema, proporcionando una interfaz simple y clara
    para ejecutar todas las verificaciones necesarias.
    
    Execution Flow:
        1. Instanciación del validador
        2. Display de información del sistema
        3. Ejecución de validación completa
        4. Interpretación de resultados
        5. Guidance para próximos pasos
        
    Returns:
        bool: True si el sistema está listo, False si necesita configuración
        
    Design Patterns:
        - Main Controller: Coordinación de flujo principal
        - Facade: Interfaz simplificada para validación completa
        - Template Method: Secuencia estándar de operaciones
        
    User Experience:
        - Clear indication de status del sistema
        - Actionable next steps basados en resultados
        - Different paths para success vs failure scenarios
        
    Error Handling:
        - Graceful handling de validation failures
        - Clear communication de remediation steps
        - User-friendly messaging
        
    Side Effects:
        - Imprime información comprehensiva en stdout
        - Puede realizar llamadas a servicios externos
        - Timing de execution para performance awareness
    """
    # Instanciación del validador - Factory Pattern
    validator = SystemValidator()
    
    # Display de información del sistema - Information Pattern
    validator.get_system_info()
    
    # Ejecución de validación completa - Template Method
    success = validator.run_full_validation()
    
    # Conditional guidance basada en resultados - Strategy Pattern
    if success:
        # Success path - Sistema listo para uso
        print("\n🎭 LISTO PARA DEBATES!")
        print("📝 Puedes ejecutar:")
        print("   python test_real_debate_only.py")
    else:
        # Failure path - Sistema necesita configuración
        print("\n🛠️ SISTEMA NECESITA CONFIGURACIÓN")
        print("📖 Revisa la documentación y corrige los errores")
    
    return success


# Entry Point Pattern - Ejecución condicional
if __name__ == "__main__":
    """
    Entry point para ejecución standalone del validador.
    
    Implementa el patrón Entry Point estándar de Python, proporcionando
    una interfaz de línea de comandos para el sistema de validación.
    
    Execution Context:
        - Direct execution: Ejecuta validación completa con UI
        - Import context: No execution (library mode)
        
    User Interface:
        - Automated validation sequence
        - Interactive pause para review de resultados
        - Clear termination con user acknowledgment
        
    Best Practices:
        - Standard Python idiom para executable modules
        - Clear separation entre library y application code
        - User-friendly interaction patterns
    """
    main()
    input("\n👋 Presiona Enter para salir...")