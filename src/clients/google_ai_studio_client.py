"""
Cliente Google AI Studio - Implementa ILLMClient
Utiliza el SDK de Google Generative AI (google-genai) para acceso a modelos Gemini
"""

import random
import time
from typing import List, Dict, Optional
from google import genai
from src.core.interfaces import ILLMClient
from src.core.config import Config


class GoogleAIStudioClient(ILLMClient):
    """
    Cliente para interactuar con Google AI Studio (Gemini)
    Implementa ILLMClient para cumplir con DIP (Dependency Inversion Principle)
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializa el cliente de Google AI Studio
        
        Args:
            api_key: API key de Google AI Studio (usa Config.GOOGLE_API_KEY si no se proporciona)
            model: Modelo a usar (usa Config.GOOGLE_MODEL si no se proporciona)
        """
        self.api_key = (api_key if api_key is not None else Config.GOOGLE_API_KEY).strip()
        self.model = model or Config.GOOGLE_MODEL
        
        if not self.api_key:
            raise ValueError(
                "Google AI Studio API key no configurada. "
                "Configura GOOGLE_API_KEY como variable de entorno o pásala al constructor."
            )
        
        # Inicializar cliente con API key
        self.client = genai.Client(api_key=self.api_key)

    def _query_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: Optional[int]
    ) -> str:
        """Ejecuta una consulta con reintentos para errores transitorios."""
        max_attempts = 3
        base_delay_seconds = 0.5

        for attempt in range(max_attempts):
            try:
                # Construir contenido con system prompt si existe
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"
                else:
                    full_prompt = prompt

                config_kwargs = {
                    "temperature": temperature,
                }
                if max_tokens is not None:
                    config_kwargs["max_output_tokens"] = max_tokens
                
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                    config=genai.types.GenerateContentConfig(**config_kwargs)
                )
                
                # Extraer texto de respuesta
                if response.text:
                    return response.text.strip()
                else:
                    return ""

            except (Exception) as e:
                error_str = str(e)
                is_transient = any(x in error_str for x in ["429", "500", "503", "timeout"])
                is_last_attempt = attempt == max_attempts - 1
                
                if not is_transient or is_last_attempt:
                    raise e

                delay = base_delay_seconds * (2 ** attempt) + random.uniform(0, 0.25)
                print(
                    f"⚠️  Error transitorio de Google AI Studio ({type(e).__name__}). "
                    f"Reintentando en {delay:.2f}s..."
                )
                time.sleep(delay)

        raise RuntimeError("No se pudo obtener respuesta de Google AI Studio tras varios intentos")
    
    def query(self, prompt: str, system_prompt: Optional[str] = None, 
              temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """
        Realiza una consulta al modelo de lenguaje Google Gemini
        
        Args:
            prompt: Texto de entrada del usuario
            system_prompt: Instrucciones del sistema
            temperature: Creatividad de la respuesta (0-1)
            max_tokens: Longitud máxima de la respuesta (None = default del proveedor)
            
        Returns:
            Respuesta generada por el modelo
        """
        try:
            return self._query_with_retry(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            print(f"❌ Error al consultar Google AI Studio: {e}")
            return f"Lo siento, hubo un error al procesar tu solicitud. Por favor, intenta de nuevo."
    
    def classify_intent(self, user_input: str, possible_intents: List[str]) -> Dict[str, float]:
        """
        Clasifica la intención del usuario usando Google Gemini
        Utiliza fuzzy matching y detección de palabras clave para mayor precisión
        
        Args:
            user_input: Texto del usuario
            possible_intents: Lista de intenciones posibles
            
        Returns:
            Diccionario con intenciones y sus probabilidades
        """
        from difflib import get_close_matches
        fallback_intent = "general" if "general" in possible_intents else (
            possible_intents[0] if possible_intents else "general"
        )
        
        # Palabras clave por intención para mejor clasificación
        intent_keywords = {
            "support": ["error", "problema", "no funciona", "broken", "crash", "fallo", "urgente", "crítico", "grave"],
            "recommendation": ["recomendación", "recomiendas", "sugerencia", "qué compro", "busco", "alternativa", "opciones"],
            "complaint": ["queja", "molesto", "insatisfecho", "malo", "terrible", "decepcionado", "fraude"],
            "faq": ["cómo", "qué es", "cuál", "dónde", "cuándo", "por qué", "política", "procedimiento"],
        }
        
        user_input_lower = user_input.lower()
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
                max_tokens=Config.INTENT_CLASSIFICATION_MAX_TOKENS
            ).lower().strip()
            
            # 1. Búsqueda exacta
            if intent in possible_intents:
                return {intent: 1.0}
            
            # 2. Búsqueda fuzzy: get_close_matches con threshold 0.85
            close_matches = get_close_matches(intent, possible_intents, n=1, cutoff=0.85)
            if close_matches:
                return {close_matches[0]: 0.95}
            
            # 3. Búsqueda por palabras clave
            best_intent = None
            max_matches = 0
            for possible_intent, keywords in intent_keywords.items():
                if possible_intent not in possible_intents:
                    continue
                matches = sum(1 for kw in keywords if kw in user_input_lower)
                if matches > max_matches:
                    max_matches = matches
                    best_intent = possible_intent
            
            if best_intent and max_matches > 0:
                confidence = min(0.9, 0.6 + (max_matches * 0.15))  # +0.15 por cada keyword
                return {best_intent: confidence}
            
            # 4. Fallback seguro: devolver solo intenciones permitidas
            return {fallback_intent: 0.5}
        
        except Exception as e:
            print(f"❌ Error al clasificar intención: {e}")
            return {fallback_intent: 0.5}

    def classify_all_intents(self, user_input: str, possible_intents: List[str]) -> List[Dict[str, object]]:
        """
        Detecta múltiples intenciones en un mensaje.

        Returns:
            Lista ordenada por score descendente con formato:
            [{"intent": str, "score": float, "keywords_matched": List[str]}]
        """
        user_input_lower = user_input.lower()

        intent_keywords = {
            "support": [
                "error", "problema", "no funciona", "broken", "crash", "fallo",
                "urgente", "crítico", "grave", "no puedo", "ayuda"
            ],
            "recommendation": [
                "recomendación", "recomiendas", "sugerencia", "qué compro", "busco",
                "alternativa", "opciones"
            ],
            "complaint": [
                "queja", "molesto", "insatisfecho", "malo", "terrible", "decepcionado", "fraude"
            ],
            "faq": [
                "cómo", "qué es", "cuál", "dónde", "cuándo", "por qué", "política", "procedimiento"
            ],
            "general": []
        }

        scored: List[Dict[str, object]] = []
        for intent in possible_intents:
            keywords = intent_keywords.get(intent, [])
            matched = [kw for kw in keywords if kw in user_input_lower]
            if matched:
                score = min(0.95, 0.55 + (0.12 * len(matched)))
                scored.append({
                    "intent": intent,
                    "score": float(score),
                    "keywords_matched": matched,
                })

        # Refuerzo de intención principal para mantener consistencia con el clasificador actual.
        primary_scores = self.classify_intent(user_input, possible_intents)
        if primary_scores:
            primary_intent, primary_score = max(primary_scores.items(), key=lambda item: item[1])
            found = next((x for x in scored if x["intent"] == primary_intent), None)
            if found:
                found["score"] = max(float(found["score"]), float(primary_score))
            else:
                scored.append({
                    "intent": primary_intent,
                    "score": float(primary_score),
                    "keywords_matched": [],
                })

        if not scored:
            fallback_intent = "general" if "general" in possible_intents else (
                possible_intents[0] if possible_intents else "general"
            )
            return [{"intent": fallback_intent, "score": 0.5, "keywords_matched": []}]

        scored.sort(key=lambda item: float(item["score"]), reverse=True)
        return scored
