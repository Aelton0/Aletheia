"""Modelos de atores e capacidades cognitivas."""

from enum import Enum
from typing import List
from pydantic import Field
from aletheia.core.entities.base import CognitiveEntity, generate_id


class ActorRole(str, Enum):
    """Papel do ator no sistema de cognição colaborativa."""
    HUMAN = "HUMAN"
    SPECIALIST = "SPECIALIST"


class Capability(str, Enum):
    """Capacidades cognitivas atômicas do Capability Model."""
    REASONING = "REASONING"          # Dedução, indução, abdução
    CRITIQUE = "CRITIQUE"            # Busca de riscos, contradições e falhas
    RESEARCH = "RESEARCH"            # Coleta de evidências e leitura
    EXPLANATION = "EXPLANATION"      # Síntese, clareza e adaptação conceitual
    PLANNING = "PLANNING"            # Decomposição de metas em passos acionáveis
    MEMORY_RETRIEVAL = "MEMORY_RETRIEVAL"  # Recuperação de precedentes relevantes


class Actor(CognitiveEntity):
    """Ator capaz de introduzir, contestar ou deliberar sobre proposições."""
    role: ActorRole
    name: str


class HumanActor(Actor):
    """Ator humano soberano: fonte de valores, intenção, veto e validação."""
    role: ActorRole = ActorRole.HUMAN
    has_veto_power: bool = True

    @classmethod
    def create_default(cls, name: str = "Human") -> "HumanActor":
        return cls(id=generate_id("human"), name=name)


class SpecialistActor(Actor):
    """Módulo especialista: Capability + Perspective + Policies."""
    role: ActorRole = ActorRole.SPECIALIST
    perspective: str
    capabilities: List[Capability] = Field(default_factory=list)
    policies: List[str] = Field(default_factory=list)
