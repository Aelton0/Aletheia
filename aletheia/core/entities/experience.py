"""Entidades do ciclo de ação, observação e experiência."""

from enum import Enum
from typing import List, Optional
from pydantic import Field
from aletheia.core.entities.base import CognitiveEntity


class DeltaType(str, Enum):
    """Classificação qualitativa do Epistemic Delta."""
    NO_MEANINGFUL_LEARNING = "NO_MEANINGFUL_LEARNING"  # Variação esperada / ruído
    CONFIRMATION = "CONFIRMATION"                      # Hipótese corroborada (SUPPORTED)
    CONTRADICTION = "CONTRADICTION"                    # Falsificação direta de premissa
    NEW_KNOWLEDGE = "NEW_KNOWLEDGE"                    # Variável omitida revelada
    PARADIGM_SHIFT = "PARADIGM_SHIFT"                  # Revisão profunda do modelo mental


class Action(CognitiveEntity):
    """Execução concreta originada de uma decisão deliberada."""
    decision_ref: str
    intent_description: str
    expected_state: str


class Outcome(CognitiveEntity):
    """Observação empírica da realidade pós-execução."""
    action_ref: str
    observed_state: str


class EpistemicDelta(CognitiveEntity):
    """Avaliação de discrepância estrutural/qualitativa entre expectativa e realidade.
    
    Invariante: Nem todo delta gera uma lição automaticamente.
    """
    action_ref: str
    outcome_ref: str
    expected_state: str
    observed_state: str
    delta_type: DeltaType
    discrepancy: str
    affected_claim_refs: List[str] = Field(default_factory=list)
    lesson_generated: bool = False


class Lesson(CognitiveEntity):
    """Princípio, heurística ou ajuste de modelo mental destilado da experiência."""
    title: str
    delta_ref: Optional[str] = None
    decision_ref: Optional[str] = None
    insight: str
    updated_rule_or_heuristic: str
    scope: str = Field(..., description="Contexto de aplicação da lição aprendida")
