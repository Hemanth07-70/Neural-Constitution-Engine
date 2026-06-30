from backend.integrations.providers.anthropic.provider import AnthropicProvider
from backend.integrations.providers.gemini.provider import GeminiProvider
from backend.integrations.providers.ollama.provider import OllamaProvider
from backend.integrations.providers.openai.provider import OpenAIProvider
from backend.integrations.providers.registry import ProviderRegistry

ProviderRegistry.register("openai", OpenAIProvider)
ProviderRegistry.register("anthropic", AnthropicProvider)
ProviderRegistry.register("gemini", GeminiProvider)
ProviderRegistry.register("ollama", OllamaProvider)
