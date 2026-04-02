"""
Estrategia General
Maneja conversaciones generales y saludos
"""

from src.core.interfaces import IChatStrategy, ChatContext, ChatResponse, ILLMClient, IDatabase
from src.core.config import Config


class GeneralStrategy(IChatStrategy):
    """
    Estrategia para conversaciones generales
    Cumple con SRP (Single Responsibility Principle) - solo maneja conversación general
    """
    
    def __init__(self, llm_client: ILLMClient, database: IDatabase):
        """
        Inicializa la estrategia con dependencias inyectadas
        
        Args:
            llm_client: Cliente LLM para generar respuestas
            database: Base de datos (opcional para esta estrategia)
        """
        self.llm_client = llm_client
        self.database = database
    
    def process(self, context: ChatContext) -> ChatResponse:
        """
        Procesa una conversación general
        
        Args:
            context: Contexto de la conversación
            
        Returns:
            Respuesta conversacional y amigable
        """
        user_input = context.user_input
        
        # Detectar saludos y despedidas
        if self._is_greeting(user_input):
            response_text = self._handle_greeting()
        elif self._is_farewell(user_input):
            response_text = self._handle_farewell()
        elif self._is_thanks(user_input):
            response_text = self._handle_thanks()
        else:
            # Conversación general usando LLM
            response_text = self._generate_general_conversation(user_input)
        
        return ChatResponse(
            message=response_text,
            intent="general",
            confidence=0.8,
            metadata={"conversation_type": "general"}
        )
    
    def _is_greeting(self, text: str) -> bool:
        """Detecta saludos"""
        greetings = ["hola", "buenos días", "buenas tardes", "buenas noches", "hey", "qué tal"]
        return any(greeting in text.lower() for greeting in greetings)
    
    def _is_farewell(self, text: str) -> bool:
        """Detecta despedidas"""
        farewells = ["adiós", "hasta luego", "chao", "bye", "nos vemos", "hasta pronto"]
        return any(farewell in text.lower() for farewell in farewells)
    
    def _is_thanks(self, text: str) -> bool:
        """Detecta agradecimientos"""
        thanks = ["gracias", "muchas gracias", "te agradezco", "agradecido"]
        return any(thank in text.lower() for thank in thanks)
    
    def _handle_greeting(self) -> str:
        """Maneja saludos"""
        return (
            "¡Hola! 👋 Bienvenido a nuestro servicio de atención al cliente.\n\n"
            "Puedo ayudarte con:\n"
            "• 🔧 Soporte técnico y resolución de problemas\n"
            "• 🛍️ Recomendaciones de productos\n"
            "• 📝 Quejas y feedback\n"
            "• ❓ Preguntas frecuentes\n\n"
            "¿En qué puedo asistirte hoy?"
        )
    
    def _handle_farewell(self) -> str:
        """Maneja despedidas"""
        return (
            "¡Hasta pronto! 👋 Gracias por usar nuestro servicio.\n"
            "Si necesitas ayuda en el futuro, estaré aquí para asistirte. "
            "¡Que tengas un excelente día!"
        )
    
    def _handle_thanks(self) -> str:
        """Maneja agradecimientos"""
        return (
            "¡De nada! 😊 Es un placer ayudarte.\n"
            "Si tienes alguna otra pregunta o necesitas asistencia adicional, "
            "no dudes en contactarme."
        )
    
    def _generate_general_conversation(self, user_input: str) -> str:
        """Genera conversación general usando LLM"""
        prompt = f"""El usuario dice: "{user_input}"

Responde de forma amigable y profesional. Si el mensaje parece que necesita un tipo especifico de ayuda (soporte, recomendaciones, etc.), sugiere amablemente que especifique su necesidad.
{Config.get_response_style_instruction('general')}"""
        
        return self.llm_client.query(
            prompt=prompt,
            system_prompt=Config.get_system_prompt("general"),
            temperature=0.8,
            max_tokens=Config.get_response_max_tokens("general")
        )
    
    def get_strategy_name(self) -> str:
        """Retorna el nombre de la estrategia"""
        return "GeneralStrategy"
