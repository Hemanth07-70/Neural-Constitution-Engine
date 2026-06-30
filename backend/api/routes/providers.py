from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.integrations.providers.manager import ProviderManager
from backend.integrations.providers.models import ChatMessage, ProviderRequest, ProviderResponse
from backend.integrations.providers.registry import ProviderRegistry

router = APIRouter(prefix="/providers", tags=["providers"])


class HealthResponse(BaseModel):
    status: str
    providers: dict[str, bool]


class GenerateRequest(BaseModel):
    provider: str
    model: str
    messages: list[ChatMessage]
    temperature: float = 0.7
    max_tokens: int | None = None


@router.get("", response_model=list[str])
async def list_providers():
    """Lists all registered AI providers."""
    return ProviderRegistry.list_providers()


@router.get("/health", response_model=HealthResponse)
async def check_health():
    """Checks the health of all registered AI providers."""
    providers = ProviderRegistry.list_providers()
    health_status = {}

    for provider in providers:
        health_status[provider] = await ProviderManager.health(provider)

    overall_status = "healthy" if any(health_status.values()) else "unhealthy"

    return HealthResponse(status=overall_status, providers=health_status)


@router.get("/models", response_model=dict[str, list[str]])
async def list_models():
    """Lists supported models per provider."""
    providers = ProviderRegistry.list_providers()
    models = {}

    for provider_name in providers:
        try:
            provider = await ProviderManager.get_provider(provider_name)
            models[provider_name] = await provider.models()
        except Exception:
            models[provider_name] = []

    return models


@router.post("/generate", response_model=ProviderResponse)
async def generate_completion(request: GenerateRequest):
    """
    Generates a completion using a specific provider.
    In a real implementation, Governance Hooks would be injected here.
    """
    try:
        prov_req = ProviderRequest(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        return await ProviderManager.generate(prov_req, provider_name=request.provider)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
