"""
Politica de creacion de tickets para soporte.
"""

import re
import unicodedata
from typing import List


class TicketPolicy:
    """Decide cuando una consulta de soporte requiere ticket."""

    def __init__(self, trigger_words: List[str] | None = None):
        triggers = trigger_words or [
            "error",
            "no funciona",
            "problema grave",
            "urgente",
        ]
        self.trigger_words = [self._normalize_text(word) for word in triggers]
        self.negated_expressions = [
            "no hay error",
            "sin error",
            "no es urgente",
            "no tengo error",
            "ningun error",
            "ningun problema grave",
            "ningun problema",
        ]

    def should_create_ticket(self, user_input: str) -> bool:
        """Retorna True si el mensaje coincide con criterios de escalamiento."""
        if not user_input or not user_input.strip():
            return False

        text = self._normalize_text(user_input)

        if not self._has_trigger(text):
            return False

        # Elimina expresiones negadas para evitar falsos positivos de keywords aisladas.
        sanitized_text = text
        for expr in self.negated_expressions:
            sanitized_text = sanitized_text.replace(expr, " ")

        return self._has_trigger(sanitized_text)

    def _has_trigger(self, normalized_text: str) -> bool:
        for trigger in self.trigger_words:
            if " " in trigger:
                if trigger in normalized_text:
                    return True
            else:
                pattern = rf"\b{re.escape(trigger)}\b"
                if re.search(pattern, normalized_text):
                    return True
        return False

    def _normalize_text(self, text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text)
        without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        return without_accents.lower()
