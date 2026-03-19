"""
Cliente OpenAI - Implementa ILLMClient
"""

from typing import List, Dict, Optional
from openai import OpenAI
from src.core.interfaces import ILLMClient
from src.core.config import Config


class OpenAIClient(ILLMClient):
    """
    Cliente para interactuar con la API de OpenAI
    Implementa ILLMClient para cumplir con DIP (Dependency Inversion Principle)
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializa el cliente de OpenAI
        
        Args:
            api_key: API key de OpenAI (usa Config.OPENAI_API_KEY si no se proporciona)
            model: Modelo a usar (usa Config.OPENAI_MODEL si no se proporciona)
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key no configurada. "
                "Configura OPENAI_API_KEY como variable de entorno o pásala al constructor."
            )
        
        self.client = OpenAI(api_key=self.api_key)
    
    def query(self, prompt: str, system_prompt: Optional[str] = None, 
              temperature: float = 0.7, max_tokens: int = 500) -> str:
        """
        Realiza una consulta al modelo de lenguaje OpenAI
        
        Args:
            prompt: Texto de entrada del usuario
            system_prompt: Instrucciones del sistema
            temperature: Creatividad de la respuesta (0-1)
            max_tokens: Longitud máxima de la respuesta
            
        Returns:
            Respuesta generada por el modelo
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"❌ Error al consultar OpenAI: {e}")
            return f"Lo siento, hubo un error al procesar tu solicitud. Por favor, intenta de nuevo."
    
    def classify_intent(self, user_input: str, possible_intents: List[str]) -> Dict[str, float]:
        """
        Clasifica la intención del usuario usando OpenAI
        
        Args:
            user_input: Texto del usuario
            possible_intents: Lista de intenciones posibles
            
        Returns:
            Diccionario con intenciones y sus probabilidades
        """
        intents_str = "\n".join([f"- {intent}" for intent in possible_intents])
        
        prompt = f"""Mensaje del usuario: "{user_input}"

Intenciones posibles:
{intents_str}

Clasifica el mensaje en UNA de estas intenciones. Responde SOLO con el nombre de la intención."""
        
        try:
            intent = self.query(
                prompt=prompt,
                system_prompt=Config.SYSTEM_PROMPTS["intent_detection"],
                temperature=0.3,  # Baja temperatura para clasificación consistente
                max_tokens=50
            ).lower().strip()
            
            # Encuentra la intención más similar de las disponibles
            if intent in possible_intents:
                return {intent: 1.0}
            
            # Si no hay coincidencia exacta, busca la más cercana
            for possible_intent in possible_intents:
                if possible_intent in intent or intent in possible_intent:
                    return {possible_intent: 0.8}
            
            # Default a "general" si no hay match
            return {"general": 0.5}
        
        except Exception as e:
            print(f"❌ Error al clasificar intención: {e}")
            return {"general": 0.5}


class MockLLMClient(ILLMClient):
    """
    Cliente Mock para pruebas sin usar OpenAI
    Útil para desarrollo y testing
    """
    
    def query(self, prompt: str, system_prompt: Optional[str] = None, 
              temperature: float = 0.7, max_tokens: int = 500) -> str:
        """Simula una respuesta del LLM"""
        return (
            f"[MODO SIMULACIÓN] He recibido tu mensaje. "
            f"Esta es una respuesta simulada porque no hay API key configurada. "
            f"El sistema funciona correctamente y procesaría tu consulta con OpenAI."
        )
    
    def classify_intent(self, user_input: str, possible_intents: List[str]) -> Dict[str, float]:
        """Simula clasificación de intención basada en keywords"""
        user_input_lower = user_input.lower()
        
        # Clasificación simple por keywords
        if any(word in user_input_lower for word in ["error", "problema", "no puedo", "no funciona", "ayuda"]):
            return {"support": 0.9}
        elif any(word in user_input_lower for word in ["recomienda", "producto", "comprar", "busco", "necesito"]):
            return {"recommendation": 0.9}
        elif any(word in user_input_lower for word in ["queja", "malo", "terrible", "pésimo", "molesto"]):
            return {"complaint": 0.9}
        elif any(word in user_input_lower for word in ["cómo", "cuánto", "cuál", "dónde", "política", "garantía"]):
            return {"faq": 0.9}
        else:
            return {"general": 0.7}
