"""LLM provider abstraction for LangGraph agent."""

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import AzureChatOpenAI

from template_fastapi.settings.azure_openai import get_azure_openai_settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def get_llm(self, **kwargs: Any) -> BaseChatModel:
        """Get the LLM instance."""


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI provider implementation."""

    def __init__(self):
        self.settings = get_azure_openai_settings()

    def get_llm(self, **kwargs: Any) -> BaseChatModel:
        """Get Azure OpenAI LLM instance."""
        return AzureChatOpenAI(
            azure_endpoint=self.settings.azure_openai_endpoint,
            api_key=self.settings.azure_openai_api_key,
            api_version=self.settings.azure_openai_api_version,
            azure_deployment=kwargs.get("model", self.settings.azure_openai_model_chat),
            temperature=kwargs.get("temperature", 0.7),
            streaming=kwargs.get("streaming", True),
        )


class LLMFactory:
    """Factory for creating LLM providers."""

    _providers = {
        "azure_openai": AzureOpenAIProvider,
    }

    @classmethod
    def create_provider(cls, provider_name: str = "azure_openai") -> LLMProvider:
        """Create LLM provider instance."""
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_name}")

        return cls._providers[provider_name]()

    @classmethod
    def get_llm(cls, provider_name: str = "azure_openai", **kwargs: Any) -> BaseChatModel:
        """Get LLM instance from provider."""
        provider = cls.create_provider(provider_name)
        return provider.get_llm(**kwargs)
