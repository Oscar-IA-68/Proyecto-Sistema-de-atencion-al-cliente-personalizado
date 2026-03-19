"""
Tests para Strategy Factory
"""

import pytest
from src.clients.openai_client import MockLLMClient
from src.infrastructure.database_sim import DatabaseSimulator
from src.factories.strategy_factory import StrategyFactory
from src.strategies.support_strategy import SupportStrategy
from src.strategies.recommendation_strategy import RecommendationStrategy


class LowConfidenceLLMClient:
    def query(self, prompt, system_prompt=None, temperature=0.7, max_tokens=500):
        return "mock"

    def classify_intent(self, user_input, possible_intents):
        return {"support": 0.2}


class EmptyScoresLLMClient:
    def query(self, prompt, system_prompt=None, temperature=0.7, max_tokens=500):
        return "mock"

    def classify_intent(self, user_input, possible_intents):
        return {}


class TestStrategyFactory:
    """Tests para el Factory Pattern"""
    
    @pytest.fixture
    def factory(self):
        """Fixture que crea un factory para tests"""
        llm_client = MockLLMClient()
        database = DatabaseSimulator()
        return StrategyFactory(llm_client, database)
    
    def test_factory_initialization(self, factory):
        """Test que el factory se inicializa correctamente"""
        assert factory is not None
        assert factory.llm_client is not None
        assert factory.database is not None
    
    def test_get_available_intents(self, factory):
        """Test que retorna todas las intenciones disponibles"""
        intents = factory.get_available_intents()
        
        assert isinstance(intents, list)
        assert len(intents) > 0
        assert "support" in intents
        assert "recommendation" in intents
        assert "complaint" in intents
        assert "faq" in intents
        assert "general" in intents
    
    def test_get_strategy_support(self, factory):
        """Test que retorna la estrategia de soporte"""
        strategy = factory.get_strategy("support")
        
        assert strategy is not None
        assert isinstance(strategy, SupportStrategy)
        assert strategy.get_strategy_name() == "SupportStrategy"
    
    def test_get_strategy_recommendation(self, factory):
        """Test que retorna la estrategia de recomendación"""
        strategy = factory.get_strategy("recommendation")
        
        assert strategy is not None
        assert isinstance(strategy, RecommendationStrategy)
        assert strategy.get_strategy_name() == "RecommendationStrategy"
    
    def test_get_strategy_unknown_returns_general(self, factory):
        """Test que retorna estrategia general para intenciones desconocidas"""
        strategy = factory.get_strategy("unknown_intent")
        
        assert strategy is not None
        assert strategy.get_strategy_name() == "GeneralStrategy"
    
    def test_detect_intent_support(self, factory):
        """Test detección de intención de soporte"""
        user_input = "Tengo un error en mi cuenta, no puedo iniciar sesión"
        intent = factory.detect_intent(user_input)
        
        assert intent in factory.get_available_intents()
        # MockLLMClient usa keywords, debería detectar "support"
        assert intent == "support"
    
    def test_detect_intent_recommendation(self, factory):
        """Test detección de intención de recomendación"""
        user_input = "Busco una laptop buena, ¿qué producto me recomiendas?"
        intent = factory.detect_intent(user_input)
        
        assert intent in factory.get_available_intents()
        assert intent == "recommendation"
    
    def test_detect_intent_complaint(self, factory):
        """Test detección de intención de queja"""
        user_input = "Esto es terrible, muy malo el servicio"
        intent = factory.detect_intent(user_input)
        
        assert intent in factory.get_available_intents()
        assert intent == "complaint"
    
    def test_detect_intent_faq(self, factory):
        """Test detección de intención de FAQ"""
        user_input = "¿Cómo puedo cambiar mi contraseña?"
        intent = factory.detect_intent(user_input)
        
        assert intent in factory.get_available_intents()
        assert intent == "faq"

    def test_detect_intent_low_confidence_falls_back_to_general(self):
        database = DatabaseSimulator()
        factory = StrategyFactory(LowConfidenceLLMClient(), database)

        intent = factory.detect_intent("Tengo una incidencia")

        assert intent == "general"

    def test_detect_intent_empty_scores_falls_back_to_general(self):
        database = DatabaseSimulator()
        factory = StrategyFactory(EmptyScoresLLMClient(), database)

        intent = factory.detect_intent("Mensaje ambiguo")

        assert intent == "general"
