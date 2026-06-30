from typing import Any

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the sender (system, user, assistant, tool)")
    content: str = Field(..., description="Message content")
    name: str | None = Field(None, description="Name for the participant")


class ProviderRequest(BaseModel):
    messages: list[ChatMessage]
    model: str
    temperature: float = 0.7
    max_tokens: int | None = None
    stream: bool = False
    tools: list[dict[str, Any]] | None = None
    response_format: dict[str, Any] | None = None
    organization_id: str | None = None


class ProviderResponse(BaseModel):
    message: ChatMessage
    model: str
    provider: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0


class EmbeddingRequest(BaseModel):
    input: str | list[str]
    model: str


class EmbeddingResponse(BaseModel):
    embeddings: list[list[float]]
    model: str
    provider: str
    total_tokens: int = 0
