"""
Strategy Factory - Factory Pattern para crear estrategias
Cumple con OCP (Open/Closed Principle)
"""

from typing import Dict, List
from src.core.interfaces import IStrategyFactory, IChatStrategy, ILLMClient, IDatabase
from src.core.config import Config
from src.strategies.support_strategy import SupportStrategy
from src.strategies.recommendation_strategy import RecommendationStrategy
from src.strategies.complaint_strategy import ComplaintStrategy
from src.strategies.faq_strategy import FAQStrategy
from src.strategies.general_strategy import GeneralStrategy
from src.policies.ticket_policy import TicketPolicy
from src.policies.severity_policy import SeverityPolicy
from src.policies.fallback_policy import FAQFallbackPolicy


class StrategyFactory(IStrategyFactory):
    """
    Factory para crear estrategias de chat
    
    Cumple con:
    - OCP: Nuevas estrategias se agregan sin modificar código existente
    - DIP: Depende de abstracciones (ILLMClient, IDatabase)
    - SRP: Solo se encarga de crear y seleccionar estrategias
    """
    
    def __init__(self, llm_client: ILLMClient, database: IDatabase):
        """
        Inicializa el factory con dependencias inyectadas
        
        Args:
            llm_client: Cliente LLM para inyectar en estrategias
            database: Base de datos para inyectar en estrategias
        """
        self.llm_client = llm_client
        self.database = database
        self.ticket_policy = TicketPolicy()
        self.severity_policy = SeverityPolicy()
        self.fallback_policy = FAQFallbackPolicy()
        
        # Registro de estrategias (hace fácil agregar nuevas sin cambiar lógica)
        self._strategies: Dict[str, IChatStrategy] = {
            "support": SupportStrategy(llm_client, database, self.ticket_policy),
            "recommendation": RecommendationStrategy(llm_client, database),
            "complaint": ComplaintStrategy(llm_client, database, self.severity_policy),
            "faq": FAQStrategy(llm_client, database, self.fallback_policy),
            "general": GeneralStrategy(llm_client, database)
        }
    
    def get_strategy(self, intent: str) -> IChatStrategy:
        """
        Obtiene la estrategia apropiada según la intención
        
        Args:
            intent: Intención detectada del usuario
            
        Returns:
            Estrategia correspondiente (default: GeneralStrategy)
        """
        strategy = self._strategies.get(intent)
        
        if strategy is None:
            print(f"⚠️  Intención '{intent}' no reconocida, usando estrategia general")
            return self._strategies["general"]
        
        return strategy
    
    def detect_intent(self, user_input: str) -> str:
        """
        Detecta la intención del usuario usando el LLM
        
        Args:
            user_input: Texto del usuario
            
        Returns:
            Nombre de la intención detectada
        """
        # Obtener intenciones disponibles
        available_intents = self.get_available_intents()
        
        # Usar el LLM para clasificar
        intent_scores = self.llm_client.classify_intent(user_input, available_intents)
        
        # Obtener la intención con mayor confianza
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            intent_name = best_intent[0]
            confidence = best_intent[1]
            
            print(f"🎯 Intención detectada: {intent_name} (confianza: {confidence:.2f})")
            
            # Si la confianza es muy baja, usar "general"
            if confidence < Config.INTENT_CONFIDENCE_THRESHOLD:
                print(f"⚠️  Confianza baja, usando estrategia general")
                return "general"
            
            return intent_name
        
        # Fallback a general
        return "general"

    def detect_all_intents(self, user_input: str) -> List[Dict[str, object]]:
        """Detecta múltiples intenciones con fallback compatible."""
        available_intents = self.get_available_intents()

        # Ruta preferida: cliente con clasificador multi-intencion.
        multi_method = getattr(self.llm_client, "classify_all_intents", None)
        if callable(multi_method):
            try:
                raw_scores = multi_method(user_input, available_intents)
                normalized: List[Dict[str, object]] = []
                for item in raw_scores or []:
                    intent = str(item.get("intent", "general"))
                    if intent not in available_intents:
                        continue
                    normalized.append(
                        {
                            "intent": intent,
                            "score": float(item.get("score", 0.0)),
                            "keywords_matched": item.get("keywords_matched", []),
                        }
                    )

                if normalized:
                    normalized.sort(key=lambda x: x["score"], reverse=True)
                    return normalized
            except Exception as e:
                print(f"⚠️  Error en classify_all_intents, fallback a clasificación única: {e}")

        # Fallback: clasificación tradicional -> lista de 1 intención.
        single_scores = self.llm_client.classify_intent(user_input, available_intents)
        if not single_scores:
            return [{"intent": "general", "score": 0.5, "keywords_matched": []}]

        intent, score = max(single_scores.items(), key=lambda x: x[1])
        if intent not in available_intents:
            intent = "general"
            score = 0.5

        return [{"intent": intent, "score": float(score), "keywords_matched": []}]
    
    def get_available_intents(self) -> List[str]:
        """
        Retorna lista de intenciones disponibles
        
        Returns:
            Lista de nombres de intenciones
        """
        return list(self._strategies.keys())
    
    def register_strategy(self, intent: str, strategy: IChatStrategy) -> None:
        """
        Registra una nueva estrategia (permite extensibilidad)
        
        Args:
            intent: Nombre de la intención
            strategy: Instancia de la estrategia
        """
        self._strategies[intent] = strategy
        print(f"✅ Estrategia '{intent}' registrada exitosamente")
