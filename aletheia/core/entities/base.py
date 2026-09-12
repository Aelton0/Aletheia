"""Primitivos base para entidades do Kernel Cognitivo."""

from datetime import datetime, timezone
from typing import Any, Dict
import uuid
from pydantic import BaseModel, ConfigDict, Field


def generate_id(prefix: str = "node") -> str:
    """Gera um identificador único com prefixo legível."""
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


class CognitiveEntity(BaseModel):
    """Classe base para todas as entidades registradas no Cognitive Workspace."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)
