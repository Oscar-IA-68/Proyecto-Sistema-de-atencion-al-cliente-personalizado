"""Tests para AppFactory."""

from src.application.app_factory import AppFactory
from src.application.chat_service import ChatService
from src.infrastructure.database_sim import DatabaseSimulator


class TestAppFactory:
    """Valida que AppFactory construye el grafo de dependencias esperado."""

    def test_create_components_returns_expected_types(self):
        components = AppFactory.create_components("mock")

        assert isinstance(components.chat_service, ChatService)
        assert isinstance(components.database, DatabaseSimulator)
        assert components.llm_client is not None

    def test_create_components_exposes_provider_name(self):
        components = AppFactory.create_components("mock")

        assert components.provider_name == "mock"

    def test_create_components_supports_configured_provider(self, monkeypatch):
        from src.core.config import Config

        monkeypatch.setattr(Config, "LLM_PROVIDER", "mock")
        components = AppFactory.create_components()

        assert components.provider_name == "mock"

    def test_create_components_returns_openai_provider_name(self, monkeypatch):
        from src.core.config import Config

        monkeypatch.setattr(Config, "OPENAI_API_KEY", "sk-test")
        components = AppFactory.create_components("openai")

        assert components.provider_name == "openai"

    def test_create_components_returns_google_ai_studio_provider_name(self, monkeypatch):
        from src.core.config import Config

        monkeypatch.setattr(Config, "GOOGLE_API_KEY", "test-api-key")
        components = AppFactory.create_components("google_ai_studio")

        assert components.provider_name == "google_ai_studio"

    def test_create_components_returns_actual_provider_name_after_fallback(self, monkeypatch):
        from src.core.config import Config

        monkeypatch.setattr(Config, "OPENAI_API_KEY", "")
        components = AppFactory.create_components("openai")

        assert components.provider_name == "mock"

    def test_create_components_google_falls_back_to_mock_without_key(self, monkeypatch):
        from src.core.config import Config

        monkeypatch.setattr(Config, "GOOGLE_API_KEY", "")
        components = AppFactory.create_components("google_ai_studio")

        assert components.provider_name == "mock"
