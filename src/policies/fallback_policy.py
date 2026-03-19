"""
Politica de fallback para FAQ.
"""

from typing import Any, Dict, List


class FAQFallbackPolicy:
    """Decide si usar FAQ encontrada o fallback a respuesta general."""

    def should_use_faq(self, faq_results: List[Dict[str, Any]]) -> bool:
        """Usa FAQ cuando hay resultados relevantes."""
        return bool(faq_results)
