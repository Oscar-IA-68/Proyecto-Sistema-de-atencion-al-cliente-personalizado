"""
Tests para Strategies
"""

import pytest
from src.core.interfaces import ChatContext
from src.clients.openai_client import MockLLMClient
from src.infrastructure.database_sim import DatabaseSimulator
from src.strategies.support_strategy import SupportStrategy
from src.strategies.recommendation_strategy import RecommendationStrategy
from src.strategies.complaint_strategy import ComplaintStrategy
from src.strategies.faq_strategy import FAQStrategy
from src.strategies.general_strategy import GeneralStrategy


class TestStrategies:
    """Tests para las estrategias de chat"""
    
    @pytest.fixture
    def llm_client(self):
        """Fixture para cliente LLM mock"""
        return MockLLMClient()
    
    @pytest.fixture
    def database(self):
        """Fixture para base de datos"""
        return DatabaseSimulator()
    
    def test_support_strategy(self, llm_client, database):
        """Test estrategia de soporte"""
        strategy = SupportStrategy(llm_client, database)
        
        context = ChatContext(
            user_input="No puedo iniciar sesión",
            conversation_history=[],
            user_id=1
        )
        
        response = strategy.process(context)
        
        assert response is not None
        assert response.intent == "support"
        assert response.message is not None
        assert len(response.message) > 0
    
    def test_recommendation_strategy(self, llm_client, database):
        """Test estrategia de recomendación"""
        strategy = RecommendationStrategy(llm_client, database)
        
        context = ChatContext(
            user_input="Busco una laptop",
            conversation_history=[]
        )
        
        response = strategy.process(context)
        
        assert response is not None
        assert response.intent == "recommendation"
        assert response.message is not None
    
    def test_complaint_strategy(self, llm_client, database):
        """Test estrategia de quejas"""
        strategy = ComplaintStrategy(llm_client, database)
        
        context = ChatContext(
            user_input="Muy malo el servicio",
            conversation_history=[],
            user_id=1
        )
        
        response = strategy.process(context)
        
        assert response is not None
        assert response.intent == "complaint"
        assert response.message is not None
        assert "metadata" in response.__dict__
    
    def test_faq_strategy(self, llm_client, database):
        """Test estrategia de FAQ"""
        strategy = FAQStrategy(llm_client, database)
        
        context = ChatContext(
            user_input="¿Cómo cambio mi contraseña?",
            conversation_history=[]
        )
        
        response = strategy.process(context)
        
        assert response is not None
        assert response.intent == "faq"
        assert response.message is not None
    
    def test_general_strategy_greeting(self, llm_client, database):
        """Test estrategia general con saludo"""
        strategy = GeneralStrategy(llm_client, database)
        
        context = ChatContext(
            user_input="Hola",
            conversation_history=[]
        )
        
        response = strategy.process(context)
        
        assert response is not None
        assert response.intent == "general"
        assert "Bienvenido" in response.message or "Hola" in response.message
    
    def test_general_strategy_thanks(self, llm_client, database):
        """Test estrategia general con agradecimiento"""
        strategy = GeneralStrategy(llm_client, database)
        
        context = ChatContext(
            user_input="Gracias por tu ayuda",
            conversation_history=[]
        )
        
        response = strategy.process(context)
        
        assert response is not None
        assert response.intent == "general"
        assert "nada" in response.message.lower() or "placer" in response.message.lower()
    
    def test_strategy_names(self, llm_client, database):
        """Test que todas las estrategias retornan su nombre correcto"""
        strategies = [
            (SupportStrategy(llm_client, database), "SupportStrategy"),
            (RecommendationStrategy(llm_client, database), "RecommendationStrategy"),
            (ComplaintStrategy(llm_client, database), "ComplaintStrategy"),
            (FAQStrategy(llm_client, database), "FAQStrategy"),
            (GeneralStrategy(llm_client, database), "GeneralStrategy")
        ]
        
        for strategy, expected_name in strategies:
            assert strategy.get_strategy_name() == expected_name
