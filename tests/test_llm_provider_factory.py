"""Tests para LLMProviderFactory."""

from src.clients.openai_client import MockLLMClient, OpenAIClient
from src.clients.google_ai_studio_client import GoogleAIStudioClient
from src.factories.llm_provider_factory import LLMProviderFactory
from src.core.config import Config


class TestLLMProviderFactory:
    """Valida seleccion de proveedor y fallback seguro a mock."""

    def test_create_mock_provider_explicitly(self):
        client = LLMProviderFactory.create("mock")

        assert isinstance(client, MockLLMClient)

    def test_create_openai_without_key_falls_back_to_mock(self, monkeypatch):
        monkeypatch.setattr(Config, "OPENAI_API_KEY", "")

        client = LLMProviderFactory.create("openai")

        assert isinstance(client, MockLLMClient)

    def test_create_google_ai_studio_without_key_falls_back_to_mock(self, monkeypatch):
        monkeypatch.setattr(Config, "GOOGLE_API_KEY", "")

        client = LLMProviderFactory.create("google_ai_studio")

        assert isinstance(client, MockLLMClient)

    def test_create_unknown_provider_falls_back_to_mock(self):
        client = LLMProviderFactory.create("unknown_provider")

        assert isinstance(client, MockLLMClient)

    def test_create_openai_with_key_uses_openai_client(self, monkeypatch):
        monkeypatch.setattr(Config, "OPENAI_API_KEY", "sk-test")

        client = LLMProviderFactory.create("openai")

        assert isinstance(client, OpenAIClient)

    def test_create_google_ai_studio_with_key_uses_google_client(self, monkeypatch):
        monkeypatch.setattr(Config, "GOOGLE_API_KEY", "test-api-key")

        client = LLMProviderFactory.create("google_ai_studio")

        assert isinstance(client, GoogleAIStudioClient)

    def test_register_provider_allows_extension_without_modifying_factory(self):
        class CustomLLMClient(MockLLMClient):
            pass

        LLMProviderFactory.register_provider("custom", CustomLLMClient)
        client = LLMProviderFactory.create("custom")

        assert isinstance(client, CustomLLMClient)

    def test_get_supported_providers_contains_defaults(self):
        providers = LLMProviderFactory.get_supported_providers()

        assert "openai" in providers
        assert "google_ai_studio" in providers
        assert "mock" in providers
