"""Porta abstrata para provedores de Modelos de Linguagem Probabilísticos (LLM Provider Port).

Garante desacoplamento total entre o Core da Aletheia e fornecedores/SDKs proprietários.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel, ConfigDict, Field


class LLMResponse(BaseModel):
    """Resposta estruturada e auditável retornada por um provedor de LLM."""
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    parsed_output: Any
    model: str
    provider: str
    usage: Dict[str, int] = Field(default_factory=dict)
    latency_ms: float
    finish_reason: Optional[str] = None
    request_id: Optional[str] = None
    raw_response_hash: Optional[str] = None


class LLMProviderPort(ABC):
    """Contrato formal para provedores de modelos de linguagem (Hexagonal Port)."""

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_schema: Type[BaseModel],
        system_instruction: Optional[str] = None,
        temperature: float = 0.0,
    ) -> LLMResponse:
        """Gera resposta probabilística estritamente estruturada conforme o schema Pydantic."""
        pass
