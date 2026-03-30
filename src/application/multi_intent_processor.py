"""Procesamiento multi-intencion (P3)."""

from typing import Dict, List

from src.core.interfaces import ChatContext, ChatResponse, IStrategyFactory


class MultiIntentProcessor:
    """Orquesta varias estrategias y sintetiza una sola respuesta."""

    def __init__(self, strategy_factory: IStrategyFactory):
        self.strategy_factory = strategy_factory

    def process(self, context: ChatContext, intent_scores: List[Dict[str, object]]) -> ChatResponse:
        if not intent_scores:
            strategy = self.strategy_factory.get_strategy("general")
            return strategy.process(context)

        responses: List[Dict[str, object]] = []

        for item in intent_scores:
            intent_name = str(item.get("intent", "general"))
            strategy = self.strategy_factory.get_strategy(intent_name)

            strategy_context = ChatContext(
                user_input=context.user_input,
                conversation_history=context.conversation_history,
                user_id=context.user_id,
                metadata={**(context.metadata or {}), "sub_intent": intent_name},
            )

            strategy_response = strategy.process(strategy_context)
            responses.append(
                {
                    "intent": intent_name,
                    "score": float(item.get("score", 0.0)),
                    "message": strategy_response.message,
                    "metadata": strategy_response.metadata,
                }
            )

        synthesized = self._synthesize_sequential(responses)
        primary_intent = responses[0]["intent"]
        avg_confidence = sum(r["score"] for r in responses) / len(responses)

        merged_metadata = {
            "multi_intent": True,
            "intents_detected": [r["intent"] for r in responses],
            "intent_scores": {r["intent"]: r["score"] for r in responses},
            "individual_metadata": {r["intent"]: r.get("metadata", {}) for r in responses},
            "synthesis_mode": "sequential",
        }

        return ChatResponse(
            message=synthesized,
            intent=primary_intent,
            confidence=avg_confidence,
            metadata=merged_metadata,
        )

    def _synthesize_sequential(self, responses: List[Dict[str, object]]) -> str:
        blocks = []
        for r in responses:
            intent_name = str(r["intent"]).capitalize()
            text = str(r["message"]).strip()
            if not text:
                continue
            blocks.append(f"[{intent_name}] {text}")

        return "\n\n".join(blocks) if blocks else "Lo siento, no pude sintetizar una respuesta válida."
