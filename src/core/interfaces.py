"""
Interfaces Core - Contratos para componentes del sistema
Cumple con ISP (Interface Segregation Principle) y DIP (Dependency Inversion Principle)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ChatContext:
    """Contexto de conversación para estrategias"""
    user_input: str
    conversation_history: List[Dict[str, str]]
    user_id: Optional[int] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ChatResponse:
    """Respuesta del chatbot"""
    message: str
    intent: str
    confidence: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ILLMClient(ABC):
    """
    Interfaz para clientes de modelos de lenguaje
    Permite intercambiar proveedores (OpenAI, Anthropic, etc.) sin cambiar código
    """
    
    @abstractmethod
    def query(self, prompt: str, system_prompt: Optional[str] = None, 
              temperature: float = 0.7, max_tokens: int = 500) -> str:
        """
        Realiza una consulta al modelo de lenguaje
        
        Args:
            prompt: Texto de entrada del usuario
            system_prompt: Instrucciones del sistema
            temperature: Creatividad de la respuesta (0-1)
            max_tokens: Longitud máxima de la respuesta
            
        Returns:
            Respuesta generada por el modelo
        """
        pass
    
    @abstractmethod
    def classify_intent(self, user_input: str, possible_intents: List[str]) -> Dict[str, float]:
        """
        Clasifica la intención del usuario
        
        Args:
            user_input: Texto del usuario
            possible_intents: Lista de intenciones posibles
            
        Returns:
            Diccionario con intenciones y sus probabilidades
        """
        pass


class IDatabase(ABC):
    """
    Interfaz para acceso a datos
    Abstrae la implementación de persistencia (JSON, SQL, etc.)
    """
    
    @abstractmethod
    def get_customers(self) -> List[Dict[str, Any]]:
        """Obtiene lista de clientes"""
        pass
    
    @abstractmethod
    def get_customer_by_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un cliente específico"""
        pass
    
    @abstractmethod
    def get_products(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtiene productos, opcionalmente filtrados por categoría"""
        pass
    
    @abstractmethod
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un producto específico"""
        pass
    
    @abstractmethod
    def get_tickets(self, customer_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtiene tickets, opcionalmente filtrados por cliente"""
        pass
    
    @abstractmethod
    def create_ticket(self, customer_id: int, ticket_type: str, 
                     subject: str) -> Dict[str, Any]:
        """Crea un nuevo ticket de soporte"""
        pass
    
    @abstractmethod
    def get_faq(self) -> List[Dict[str, Any]]:
        """Obtiene preguntas frecuentes"""
        pass
    
    @abstractmethod
    def search_faq(self, query: str) -> List[Dict[str, Any]]:
        """Busca en FAQ por similitud de texto"""
        pass


class IChatStrategy(ABC):
    """
    Interfaz para estrategias de chat (Strategy Pattern)
    Cada tipo de consulta tiene su propia estrategia
    """
    
    @abstractmethod
    def process(self, context: ChatContext) -> ChatResponse:
        """
        Procesa un mensaje según la estrategia específica
        
        Args:
            context: Contexto de la conversación
            
        Returns:
            Respuesta del chatbot
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Retorna el nombre de la estrategia"""
        pass


class IStrategyFactory(ABC):
    """
    Interfaz para Factory de estrategias (Factory Pattern)
    Permite agregar nuevas estrategias sin modificar el código existente (OCP)
    """
    
    @abstractmethod
    def get_strategy(self, intent: str) -> IChatStrategy:
        """
        Obtiene la estrategia apropiada según la intención
        
        Args:
            intent: Intención detectada del usuario
            
        Returns:
            Estrategia correspondiente
        """
        pass
    
    @abstractmethod
    def detect_intent(self, user_input: str) -> str:
        """
        Detecta la intención del usuario
        
        Args:
            user_input: Texto del usuario
            
        Returns:
            Nombre de la intención detectada
        """
        pass
    
    @abstractmethod
    def get_available_intents(self) -> List[str]:
        """Retorna lista de intenciones disponibles"""
        pass


class IChatService(ABC):
    """
    Interfaz para el servicio de chat principal
    Orquesta el flujo de la conversación
    """
    
    @abstractmethod
    def process_message(
        self,
        user_input: str,
        user_id: Optional[int] = None,
        expected_intent: Optional[str] = None
    ) -> ChatResponse:
        """
        Procesa un mensaje del usuario
        
        Args:
            user_input: Mensaje del usuario
            user_id: ID del usuario (opcional)
            expected_intent: Intención esperada para medición de accuracy (opcional)
            
        Returns:
            Respuesta del chatbot
        """
        pass
    
    @abstractmethod
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Obtiene el historial de conversación"""
        pass
    
    @abstractmethod
    def clear_history(self) -> None:
        """Limpia el historial de conversación"""
        pass
