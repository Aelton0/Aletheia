"""Entidades do espaço de deliberação: Metas, Restrições, Alternativas e Argumentos."""

from enum import Enum
from typing import List, Optional
from pydantic import Field
from aletheia.core.entities.base import CognitiveEntity
from aletheia.core.entities.epistemic import LifecycleStatus


class AlternativeStatus(str, Enum):
    """Status de uma alternativa no espaço deliberativo."""
    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class ArgumentStance(str, Enum):
    """Postura de um argumento em relação a uma alternativa."""
    SUPPORT = "SUPPORT"
    OPPOSE = "OPPOSE"


class Goal(CognitiveEntity):
    """Estado desejado ou objetivo deliberativo."""
    statement: str
    success_criteria: List[str] = Field(default_factory=list)
    priority: int = Field(default=1, ge=1)
    is_active: bool = True


class Constraint(CognitiveEntity):
    """Invariante ou fronteira que nenhuma solução pode violar."""
    statement: str
    inviolable: bool = True
    source: Optional[str] = None


class Alternative(CognitiveEntity):
    """Caminho ou opção discreta sob consideração."""
    title: str
    description: str
    status: AlternativeStatus = AlternativeStatus.PROPOSED
    goal_refs: List[str] = Field(default_factory=list)
    constraint_refs: List[str] = Field(default_factory=list)


class Argument(CognitiveEntity):
    """Racional estruturado pró ou contra uma alternativa."""
    alternative_id: str
    stance: ArgumentStance
    premise_refs: List[str] = Field(default_factory=list, description="IDs de Claims ou Evidences que embasam o argumento")
    rationale: str
    author_id: str
    weight: float = Field(default=1.0, ge=0.0)


class Recommendation(CognitiveEntity):
    """Proposta de síntese de ação com explicitação de premissas vulneráveis."""
    proposed_alternative_id: str
    author_id: str
    rationale: str
    depends_on_assumptions: List[str] = Field(default_factory=list, description="Suposições que sustentam a recomendação")
    supported_by: List[str] = Field(default_factory=list, description="Fatos e evidências de sustentação")
    lifecycle_status: LifecycleStatus = LifecycleStatus.ACTIVE
