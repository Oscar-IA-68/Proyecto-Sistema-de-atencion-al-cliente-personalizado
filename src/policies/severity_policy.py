"""
Politica para clasificar severidad de quejas.
"""

import re
import unicodedata


class SeverityPolicy:
    """Clasifica quejas en high, medium o low."""

    def __init__(self):
        self.high_severity_words = [
            "pesimo",
            "terrible",
            "horrible",
            "fraude",
            "estafa",
            "abogado",
            "demanda",
            "nunca mas",
            "peor",
            "inaceptable",
        ]
        self.medium_severity_words = [
            "malo",
            "decepcionado",
            "molesto",
            "insatisfecho",
            "problema",
            "error",
            "equivocado",
        ]
        self.negation_prefixes = ["no", "sin", "ningun", "ninguna"]

    def assess(self, complaint: str) -> str:
        """Evalua severidad basada en palabras clave."""
        complaint_lower = self._normalize_text(complaint)
        filtered_text = self._remove_negated_keywords(complaint_lower)

        if self._contains_keyword(filtered_text, self.high_severity_words):
            return "high"
        if self._contains_keyword(filtered_text, self.medium_severity_words):
            return "medium"
        return "low"

    def _contains_keyword(self, text: str, keywords: list[str]) -> bool:
        for keyword in keywords:
            if " " in keyword:
                if keyword in text:
                    return True
            else:
                pattern = rf"\b{re.escape(keyword)}\b"
                if re.search(pattern, text):
                    return True
        return False

    def _remove_negated_keywords(self, text: str) -> str:
        result = text
        for keyword in self.high_severity_words + self.medium_severity_words:
            if " " in keyword:
                for prefix in self.negation_prefixes:
                    result = result.replace(f"{prefix} {keyword}", " ")
            else:
                for prefix in self.negation_prefixes:
                    pattern = rf"\b{prefix}\s+{re.escape(keyword)}\b"
                    result = re.sub(pattern, " ", result)
                for helper in ["es", "esta"]:
                    pattern = rf"\bno\s+{helper}\s+{re.escape(keyword)}\b"
                    result = re.sub(pattern, " ", result)
        return result

    def _normalize_text(self, text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text)
        without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        return without_accents.lower()
