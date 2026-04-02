"""
Cliente OpenAI - Implementa ILLMClient
"""

import random
import time
from typing import List, Dict, Optional, Any
from openai import OpenAI, APIConnectionError, APITimeoutError, APIStatusError, RateLimitError
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
        self.api_key = (api_key if api_key is not None else Config.OPENAI_API_KEY).strip()
        self.model = model or Config.OPENAI_MODEL
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key no configurada. "
                "Configura OPENAI_API_KEY como variable de entorno o pásala al constructor."
            )
        
        self.client = OpenAI(api_key=self.api_key, timeout=20.0, max_retries=0)

    def _query_with_retry(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> str:
        """Ejecuta una consulta con reintentos para errores transitorios."""
        max_attempts = 3
        base_delay_seconds = 0.5

        for attempt in range(max_attempts):
            try:
                request_kwargs: Dict[str, Any] = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                }
                if max_tokens is not None:
                    request_kwargs["max_tokens"] = max_tokens

                response = self.client.chat.completions.create(**request_kwargs)
                content = response.choices[0].message.content if response.choices else ""
                return content.strip() if isinstance(content, str) else ""

            except (APIConnectionError, APITimeoutError, RateLimitError) as e:
                is_last_attempt = attempt == max_attempts - 1
                if is_last_attempt:
                    raise e

                delay = base_delay_seconds * (2 ** attempt) + random.uniform(0, 0.25)
                print(
                    f"⚠️  Error transitorio de OpenAI ({type(e).__name__}). "
                    f"Reintentando en {delay:.2f}s..."
                )
                time.sleep(delay)

            except APIStatusError as e:
                status_code = getattr(e, "status_code", None)
                is_server_error = status_code is not None and status_code >= 500
                is_last_attempt = attempt == max_attempts - 1

                if (not is_server_error) or is_last_attempt:
                    raise e

                delay = base_delay_seconds * (2 ** attempt) + random.uniform(0, 0.25)
                print(
                    f"⚠️  Error HTTP {status_code} de OpenAI. "
                    f"Reintentando en {delay:.2f}s..."
                )
                time.sleep(delay)

        raise RuntimeError("No se pudo obtener respuesta de OpenAI tras varios intentos")
    
    def query(self, prompt: str, system_prompt: Optional[str] = None, 
              temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """
        Realiza una consulta al modelo de lenguaje OpenAI
        
        Args:
            prompt: Texto de entrada del usuario
            system_prompt: Instrucciones del sistema
            temperature: Creatividad de la respuesta (0-1)
            max_tokens: Longitud máxima de la respuesta (None = default del proveedor)
            
        Returns:
            Respuesta generada por el modelo
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            return self._query_with_retry(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
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

        fallback_intent = "general" if "general" in possible_intents else (
            possible_intents[0] if possible_intents else "general"
        )
        
        prompt = f"""Mensaje del usuario: "{user_input}"

Intenciones posibles:
{intents_str}

Clasifica el mensaje en UNA de estas intenciones. Responde SOLO con el nombre de la intención."""
        
        try:
            intent = self.query(
                prompt=prompt,
                system_prompt=Config.SYSTEM_PROMPTS["intent_detection"],
                temperature=0.3,  # Baja temperatura para clasificación consistente
                max_tokens=Config.INTENT_CLASSIFICATION_MAX_TOKENS
            ).lower().strip()
            
            # Encuentra la intención más similar de las disponibles
            if intent in possible_intents:
                return {intent: 1.0}
            
            # Si no hay coincidencia exacta, busca la más cercana
            for possible_intent in possible_intents:
                if possible_intent in intent or intent in possible_intent:
                    return {possible_intent: 0.8}
            
            # Fallback seguro: devolver solo intenciones permitidas
            return {fallback_intent: 0.5}
        
        except Exception as e:
            print(f"❌ Error al clasificar intención: {e}")
            return {fallback_intent: 0.5}


class MockLLMClient(ILLMClient):
    """
    Cliente Mock para pruebas sin usar OpenAI
    Útil para desarrollo y testing
    """
    
    def query(self, prompt: str, system_prompt: Optional[str] = None, 
              temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """Simula una respuesta del LLM"""
        return (
            f"[MODO SIMULACIÓN] He recibido tu mensaje. "
            f"Esta es una respuesta simulada porque no hay API key configurada. "
            f"El sistema funciona correctamente y procesaría tu consulta con OpenAI."
        )
    
    def classify_intent(self, user_input: str, possible_intents: List[str]) -> Dict[str, float]:
        """Simula clasificación de intención basada en keywords"""
        user_input_lower = user_input.lower()
        fallback_intent = "general" if "general" in possible_intents else (
            possible_intents[0] if possible_intents else "general"
        )

        def _safe_result(intent: str, confidence: float) -> Dict[str, float]:
            if intent in possible_intents:
                return {intent: confidence}
            return {fallback_intent: 0.5}
        
        # Clasificación simple por keywords
        if any(word in user_input_lower for word in ["error", "problema", "no puedo", "no funciona", "ayuda"]):
            return _safe_result("support", 0.9)
        elif any(word in user_input_lower for word in ["recomienda", "producto", "comprar", "busco", "necesito"]):
            return _safe_result("recommendation", 0.9)
        elif any(word in user_input_lower for word in ["queja", "malo", "terrible", "pésimo", "molesto"]):
            return _safe_result("complaint", 0.9)
        elif any(word in user_input_lower for word in ["cómo", "cuánto", "cuál", "dónde", "política", "garantía"]):
            return _safe_result("faq", 0.9)
        else:
            return {fallback_intent: 0.7 if fallback_intent == "general" else 0.5}
