"""Estrutura do Cognitive Decision Record (CDR) contextual e deliberativo."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from aletheia.core.entities.base import CognitiveEntity
from aletheia.core.entities.deliberation import ArgumentStance


class DecisionStatus(str, Enum):
    """Status do ciclo de vida de uma decisão."""
    PROPOSED = "PROPOSED"
    RATIFIED = "RATIFIED"
    SUPERSEDED = "SUPERSEDED"
    REVERTED = "REVERTED"


class ReversibilityType(str, Enum):
    """Grau de reversibilidade da decisão."""
    TYPE_1_IRREVERSIBLE = "TYPE_1_IRREVERSIBLE"  # Porta de uma via: alto risco, veto humano mandatório
    TYPE_2_REVERSIBLE = "TYPE_2_REVERSIBLE"      # Porta de duas vias: reversível com baixo custo


class DissentingView(BaseModel):
    """Registro explícito de dissidência preservada para auditoria e aprendizado."""
    actor_id: str
    position: ArgumentStance
    argument_refs: List[str] = Field(default_factory=list)
    rationale: str


class CognitiveDecisionRecord(CognitiveEntity):
    """Registro cognitivo de decisão com ancoragem contextual, premissas e dissidência."""
    cdr_id: str
    title: str
    status: DecisionStatus = DecisionStatus.RATIFIED
    decision_owner: str = Field(..., description="ID do ator soberano ou módulo responsável")
    decision_scope: str = Field(
        ...,
        min_length=3,
        description="Escopo contextual estrito onde a decisão é válida (não é verdade universal)"
    )
    review_at: Optional[str] = Field(default=None, description="Data, marco ou evento para reavaliação")
    reversibility: ReversibilityType = ReversibilityType.TYPE_2_REVERSIBLE

    problem_ref: Optional[str] = None
    goal_refs: List[str] = Field(default_factory=list)
    constraint_refs: List[str] = Field(default_factory=list)

    chosen_alternative_ref: str = Field(..., description="ID da alternativa selecionada")
    supersedes_ref: Optional[str] = Field(default=None, description="ID do CDR anterior que esta decisão substitui")

    alternatives_considered: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_refs: List[str] = Field(default_factory=list)
    uncertainty_refs: List[str] = Field(default_factory=list, description="Incertezas/Unknowns assumidos na decisão")
    underlying_assumptions: List[str] = Field(default_factory=list, description="Premissas cuja queda força revisão")

    dissenting_views: List[DissentingView] = Field(
        default_factory=list,
        description="Preservação obrigatória de visões contrárias"
    )
    human_rationale: Optional[str] = Field(default=None, description="Justificativa do humano ao assumir o caminho")
    expected_outcomes: List[str] = Field(default_factory=list)
    review_triggers: List[str] = Field(default_factory=list)
