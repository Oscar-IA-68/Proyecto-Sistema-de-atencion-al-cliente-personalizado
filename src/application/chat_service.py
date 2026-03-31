"""
Chat Service - Servicio principal de la aplicación
Orquesta el flujo de conversación
"""

import time
from typing import List, Dict, Optional, Any
from src.core.interfaces import (
    IChatService, IStrategyFactory, ChatContext, ChatResponse
)
from src.core.config import Config
from src.application.multi_intent_processor import MultiIntentProcessor


class ChatService(IChatService):
    """
    Servicio principal de chat
    
    Cumple con:
    - SRP: Solo orquesta, no implementa lógica de negocio
    - DIP: Depende de abstracciones (IStrategyFactory)
    - OCP: Extensible sin modificación
    """
    
    def __init__(self, strategy_factory: IStrategyFactory):
        """
        Inicializa el servicio con dependencias inyectadas
        
        Args:
            strategy_factory: Factory para obtener estrategias
        """
        self.strategy_factory = strategy_factory
        self.conversation_history: List[Dict[str, str]] = []
        self._response_times_ms: List[float] = []
        self._fallback_to_general_count = 0
        self._intent_predictions_total = 0
        self._intent_predictions_correct = 0
    
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
            expected_intent: Intención esperada para medir accuracy (opcional)
            
        Returns:
            Respuesta del chatbot
        """
        # Validar entrada
        if not user_input or not user_input.strip():
            return ChatResponse(
                message="No recibí ningún mensaje. ¿Podrías escribir algo?",
                intent="general",
                confidence=1.0
            )
        started_at = time.perf_counter()
        
        # Detectar intención
        print(f"\n💬 Usuario: {user_input}")
        detect_all = getattr(self.strategy_factory, "detect_all_intents", None)
        all_intents = detect_all(user_input) if callable(detect_all) else []

        threshold = Config.MULTI_INTENT_THRESHOLD
        significant_intents = [
            item for item in all_intents
            if float(item.get("score", 0.0)) >= threshold
        ]
        significant_intents.sort(key=lambda x: float(x.get("score", 0.0)), reverse=True)

        if not significant_intents:
            intent = self.strategy_factory.detect_intent(user_input)
            significant_intents = [{"intent": intent, "score": 0.5}]
        else:
            intent = str(significant_intents[0]["intent"])

        # Entrada muy corta/ambigua: priorizar fallback conservador a general.
        word_count = len(user_input.strip().split())
        ambiguous_short_terms = {"ayuda", "help", "hola", "buenas", "hello", "hi"}
        normalized_input = user_input.strip().lower()
        if normalized_input in ambiguous_short_terms:
            intent = "general"
            significant_intents = [{"intent": "general", "score": 0.5}]

        if word_count <= 2 and intent != "general":
            conservative_intent = self.strategy_factory.detect_intent(user_input)
            if conservative_intent == "general":
                intent = "general"
                significant_intents = [{"intent": "general", "score": 0.5}]

        if intent == "general":
            self._fallback_to_general_count += 1
        if expected_intent:
            self._intent_predictions_total += 1
            if expected_intent.strip().lower() == intent:
                self._intent_predictions_correct += 1

        max_strategies = max(1, Config.MULTI_INTENT_MAX_STRATEGIES)
        selected_intents = significant_intents[:max_strategies]
        use_multi_intent = (
            Config.MULTI_INTENT_ENABLED
            and len(selected_intents) > 1
            and any(item.get("intent") != "general" for item in selected_intents)
        )
        
        # Crear contexto de conversación
        context = ChatContext(
            user_input=user_input,
            conversation_history=self.conversation_history.copy(),
            user_id=user_id,
            metadata={"detected_intent": intent}
        )
        
        # Procesar con una o varias estrategias
        if use_multi_intent:
            print(
                "🧠 Modo multi-intención activado: "
                + ", ".join(
                    f"{i['intent']}({float(i['score']):.2f})" for i in selected_intents
                )
            )
            processor = MultiIntentProcessor(self.strategy_factory)
            response = processor.process(context, selected_intents)
        else:
            # Obtener estrategia apropiada
            strategy = self.strategy_factory.get_strategy(intent)
            print(f"🔧 Usando estrategia: {strategy.get_strategy_name()}")
            response = strategy.process(context)

            # Adjuntar trazabilidad de clasificación cuando no entra al modo multi-intent
            response.metadata = response.metadata or {}
            response.metadata.setdefault("multi_intent", False)
            response.metadata.setdefault("intents_detected", [intent])
            response.metadata.setdefault("intent_scores", {intent: float(selected_intents[0].get("score", 0.0))})
        
        # Normalizar confidence: asegurar que está en rango [0, 1]
        if hasattr(response, 'confidence') and response.confidence is not None:
            # Si confidence está dado como 0.8-1.0, usarla tal cual
            # Si está dado como 0-100, normalizarla
            if response.confidence > 1.0:
                response.confidence = response.confidence / 100.0
        else:
            # Calcular confidence desde la estrategia si no está definido
            response.confidence = 0.7  # Default moderado
        
        # Actualizar historial
        self._add_to_history(user_input, response.message)
        
        print(f"🤖 Asistente: {response.message[:100]}{'...' if len(response.message) > 100 else ''}")
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        self._response_times_ms.append(elapsed_ms)
        
        return response
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Obtiene el historial de conversación
        
        Returns:
            Lista de mensajes en el historial
        """
        return self.conversation_history.copy()
    
    def clear_history(self) -> None:
        """Limpia el historial de conversación"""
        self.conversation_history.clear()
        print("🗑️  Historial de conversación limpiado")
    
    def _add_to_history(self, user_message: str, bot_message: str) -> None:
        """
        Agrega un intercambio al historial
        
        Args:
            user_message: Mensaje del usuario
            bot_message: Respuesta del bot
        """
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": bot_message
        })
        
        # Limitar tamaño del historial
        max_length = Config.MAX_HISTORY_LENGTH * 2  # *2 porque guardamos user + assistant
        if len(self.conversation_history) > max_length:
            # Mantener solo los últimos N mensajes
            self.conversation_history = self.conversation_history[-max_length:]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la sesión de chat
        
        Returns:
            Diccionario con estadísticas
        """
        total_messages = len(self.conversation_history)
        user_messages = len([m for m in self.conversation_history if m["role"] == "user"])
        interactions = user_messages
        avg_response_time_ms = (
            round(sum(self._response_times_ms) / len(self._response_times_ms), 2)
            if self._response_times_ms else 0.0
        )
        p95_response_time_ms = self._calculate_p95_response_time_ms()
        fallback_rate = (
            round((self._fallback_to_general_count / interactions) * 100, 2)
            if interactions > 0 else 0.0
        )
        intent_accuracy = (
            round((self._intent_predictions_correct / self._intent_predictions_total) * 100, 2)
            if self._intent_predictions_total > 0 else None
        )
        
        return {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "bot_messages": total_messages - user_messages,
            "available_intents": self.strategy_factory.get_available_intents(),
            "avg_response_time_ms": avg_response_time_ms,
            "p95_response_time_ms": p95_response_time_ms,
            "fallback_to_general_count": self._fallback_to_general_count,
            "fallback_rate_pct": fallback_rate,
            "intent_accuracy_pct": intent_accuracy,
            "intent_evaluated_samples": self._intent_predictions_total
        }

    def _calculate_p95_response_time_ms(self) -> float:
        """Calcula percentil 95 del tiempo de respuesta en milisegundos."""
        if not self._response_times_ms:
            return 0.0

        sorted_times = sorted(self._response_times_ms)
        idx = max(0, int(0.95 * (len(sorted_times) - 1)))
        return round(sorted_times[idx], 2)
