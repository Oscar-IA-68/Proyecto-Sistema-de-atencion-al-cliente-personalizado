"""
Estrategia de FAQ (Preguntas Frecuentes)
Responde preguntas comunes usando base de conocimiento
"""

from typing import List, Dict, Any
from src.core.interfaces import IChatStrategy, ChatContext, ChatResponse, ILLMClient, IDatabase
from src.core.config import Config
from src.policies.fallback_policy import FAQFallbackPolicy


class FAQStrategy(IChatStrategy):
    """
    Estrategia para responder preguntas frecuentes
    Cumple con SRP (Single Responsibility Principle) - solo maneja FAQ
    """
    
    def __init__(self, llm_client: ILLMClient, database: IDatabase, fallback_policy: FAQFallbackPolicy | None = None):
        """
        Inicializa la estrategia con dependencias inyectadas
        
        Args:
            llm_client: Cliente LLM para generar/mejorar respuestas
            database: Base de datos para consultar FAQ
        """
        self.llm_client = llm_client
        self.database = database
        self.fallback_policy = fallback_policy or FAQFallbackPolicy()
    
    def process(self, context: ChatContext) -> ChatResponse:
        """
        Procesa una pregunta frecuente
        
        Args:
            context: Contexto de la conversación
            
        Returns:
            Respuesta basada en FAQ o generada por LLM
        """
        user_input = context.user_input
        
        # Buscar en FAQ
        faq_results = self.database.search_faq(user_input)
        
        if self.fallback_policy.should_use_faq(faq_results):
            # Encontró FAQ relevantes
            response_text = self._format_faq_response(user_input, faq_results)
            confidence = 0.95
            used_faq = True
        else:
            # No encontró FAQ, usar LLM con contexto general
            response_text = self._generate_general_response(user_input)
            confidence = 0.7
            used_faq = False
        
        return ChatResponse(
            message=response_text,
            intent="faq",
            confidence=confidence,
            metadata={
                "used_faq": used_faq,
                "faq_results_count": len(faq_results) if faq_results else 0
            }
        )
    
    def _format_faq_response(self, question: str, faq_results: List[Dict[str, Any]]) -> str:
        """
        Formatea respuesta basada en resultados de FAQ
        
        Args:
            question: Pregunta del usuario
            faq_results: Resultados de búsqueda en FAQ
            
        Returns:
            Respuesta formateada
        """
        # Tomar el mejor resultado
        best_match = faq_results[0]
        
        response = f"{best_match['answer']}"
        
        # Si hay más resultados relevantes, mencionarlos
        if len(faq_results) > 1:
            response += "\n\n📚 Otras preguntas relacionadas:\n"
            for i, faq in enumerate(faq_results[1:3], 1):  # Máximo 2 adicionales
                response += f"{i}. {faq['question']}\n"
        
        return response
    
    def _generate_general_response(self, question: str) -> str:
        """
        Genera respuesta general cuando no hay FAQ match
        
        Args:
            question: Pregunta del usuario
            
        Returns:
            Respuesta generada por LLM
        """
        # Obtener todas las FAQ como contexto para el LLM
        all_faq = self.database.get_faq()
        faq_context = "\n".join([
            f"P: {faq['question']}\nR: {faq['answer']}"
            for faq in all_faq[:5]  # Solo incluir las primeras 5 para no saturar
        ])
        
        prompt = f"""Pregunta del usuario: "{question}"

Información disponible en nuestra base de conocimiento:
{faq_context}

Responde la pregunta de forma clara. Si la información exacta no está disponible, indica cómo el usuario puede obtenerla (contactar soporte, revisar la sección X, etc.)."""
        
        return self.llm_client.query(
            prompt=prompt,
            system_prompt=Config.get_system_prompt("faq"),
            temperature=0.5,  # Baja temperatura para respuestas consistentes
            max_tokens=400
        )
    
    def get_strategy_name(self) -> str:
        """Retorna el nombre de la estrategia"""
        return "FAQStrategy"
