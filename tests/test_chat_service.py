"""
Tests para Chat Service
"""

import pytest
from src.application.chat_service import ChatService
from src.factories.strategy_factory import StrategyFactory
from src.clients.openai_client import MockLLMClient
from src.infrastructure.database_sim import DatabaseSimulator


class TestChatService:
    """Tests para el servicio de chat"""
    
    @pytest.fixture
    def chat_service(self):
        """Fixture que crea un servicio de chat para tests"""
        llm_client = MockLLMClient()
        database = DatabaseSimulator()
        factory = StrategyFactory(llm_client, database)
        return ChatService(factory)
    
    def test_service_initialization(self, chat_service):
        """Test que el servicio se inicializa correctamente"""
        assert chat_service is not None
        assert chat_service.strategy_factory is not None
        assert chat_service.conversation_history is not None
        assert len(chat_service.conversation_history) == 0
    
    def test_process_message(self, chat_service):
        """Test procesar un mensaje básico"""
        response = chat_service.process_message("Hola, necesito ayuda")
        
        assert response is not None
        assert response.message is not None
        assert len(response.message) > 0
        assert response.intent is not None
        assert 0 <= response.confidence <= 1.0
    
    def test_process_empty_message(self, chat_service):
        """Test procesar mensaje vacío"""
        response = chat_service.process_message("")
        
        assert response is not None
        assert "No recibí ningún mensaje" in response.message
    
    def test_process_message_updates_history(self, chat_service):
        """Test que procesar mensaje actualiza el historial"""
        initial_length = len(chat_service.get_conversation_history())
        
        chat_service.process_message("Test message")
        
        final_length = len(chat_service.get_conversation_history())
        assert final_length == initial_length + 2  # User + assistant
    
    def test_conversation_history(self, chat_service):
        """Test obtener historial de conversación"""
        chat_service.process_message("Primera pregunta")
        chat_service.process_message("Segunda pregunta")
        
        history = chat_service.get_conversation_history()
        
        assert isinstance(history, list)
        assert len(history) == 4  # 2 mensajes * 2 (user + assistant)
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
    
    def test_clear_history(self, chat_service):
        """Test limpiar historial"""
        chat_service.process_message("Test message")
        assert len(chat_service.get_conversation_history()) > 0
        
        chat_service.clear_history()
        
        assert len(chat_service.get_conversation_history()) == 0
    
    def test_process_message_with_user_id(self, chat_service):
        """Test procesar mensaje con ID de usuario"""
        response = chat_service.process_message(
            "Necesito ayuda",
            user_id=1
        )
        
        assert response is not None
        assert response.message is not None
    
    def test_get_stats(self, chat_service):
        """Test obtener estadísticas"""
        chat_service.process_message("Test 1")
        chat_service.process_message("Test 2")
        
        stats = chat_service.get_stats()
        
        assert isinstance(stats, dict)
        assert "total_messages" in stats
        assert "user_messages" in stats
        assert "bot_messages" in stats
        assert "avg_response_time_ms" in stats
        assert "p95_response_time_ms" in stats
        assert "fallback_to_general_count" in stats
        assert "fallback_rate_pct" in stats
        assert "intent_accuracy_pct" in stats
        assert stats["total_messages"] == 4
        assert stats["user_messages"] == 2
        assert stats["bot_messages"] == 2
        assert stats["avg_response_time_ms"] >= 0
        assert stats["p95_response_time_ms"] >= 0
        assert stats["fallback_to_general_count"] >= 0
        assert 0 <= stats["fallback_rate_pct"] <= 100

    def test_stats_intent_accuracy_with_expected_labels(self, chat_service):
        """Test accuracy de intención usando expected_intent opcional"""
        chat_service.process_message(
            "No puedo iniciar sesión en mi cuenta",
            expected_intent="support"
        )
        chat_service.process_message(
            "¿Cuánto tarda el envío?",
            expected_intent="faq"
        )

        stats = chat_service.get_stats()

        assert stats["intent_evaluated_samples"] == 2
        assert stats["intent_accuracy_pct"] is not None
        assert 0 <= stats["intent_accuracy_pct"] <= 100

    def test_stats_intent_accuracy_without_labels(self, chat_service):
        """Test accuracy en N/A cuando no hay etiquetas esperadas"""
        chat_service.process_message("Hola")

        stats = chat_service.get_stats()

        assert stats["intent_evaluated_samples"] == 0
        assert stats["intent_accuracy_pct"] is None

    def test_stats_fallback_rate_when_general_intent_detected(self, chat_service):
        """Test tasa de fallback cuando la intención detectada es general"""
        chat_service.process_message("hola")

        stats = chat_service.get_stats()

        assert stats["user_messages"] == 1
        assert stats["fallback_to_general_count"] >= 1
        assert stats["fallback_rate_pct"] > 0
    
    def test_support_intent_detection(self, chat_service):
        """Test detección de intención de soporte"""
        response = chat_service.process_message(
            "Tengo un error en mi cuenta, no puedo iniciar sesión"
        )
        
        assert response.intent == "support"
    
    def test_recommendation_intent_detection(self, chat_service):
        """Test detección de intención de recomendación"""
        response = chat_service.process_message(
            "Busco un producto, ¿qué me recomiendas?"
        )
        
        assert response.intent == "recommendation"
    
    def test_complaint_intent_detection(self, chat_service):
        """Test detección de intención de queja"""
        response = chat_service.process_message(
            "Esto es terrible, muy malo el servicio"
        )
        
        assert response.intent == "complaint"
    
    def test_faq_intent_detection(self, chat_service):
        """Test detección de intención de FAQ"""
        response = chat_service.process_message(
            "¿Cómo puedo cambiar mi contraseña?"
        )
        
        assert response.intent == "faq"
