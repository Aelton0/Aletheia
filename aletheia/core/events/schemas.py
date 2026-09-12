"""Definições de relações do grafo e schemas de eventos cognitivos."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class EdgeRelation(str, Enum):
    """Relações semânticas formais do Grafo Epistêmico da Aletheia."""
    SUPPORTS = "supports"          # Sustentação epistêmica/argumentativa
    OPPOSES = "opposes"            # Objeção ou contra-argumento
    DEPENDS_ON = "depends_on"      # Dependência de premissa lógica
    DERIVED_FROM = "derived_from"  # Origem de inferência
    INVALIDATES = "invalidates"    # Falsificação formal
    CONTRADICTS = "contradicts"    # Inconsistência mútua (gera CONFLICT dialético)
    SUPERSEDES = "supersedes"      # Substituição histórica rastreável
    ADDRESSES = "addresses"        # Proposta de solução para meta/problema
    VIOLATES = "violates"          # Colisão com restrição inviolável
    SELECTS = "selects"            # Escolha deliberada formalizada
    IMPLEMENTS = "implements"      # Execução de ação decorrente de decisão
    RESULTS_IN = "results_in"      # Conexão de ação ao outcome empírico
    REVEALS = "reveals"            # Detecção de discrepância (Epistemic Delta)
    LEARNED_FROM = "learned_from"  # Ancoragem da lição na experiência


class CognitiveEvent(BaseModel):
    """Evento atômico e imutável que registra qualquer mutação no espaço cognitivo."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:10]}")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor_id: str
    event_type: str
    payload: Dict[str, Any]


class EntityIntroducedPayload(BaseModel):
    """Payload para introdução de nova entidade no espaço."""
    entity_type: str
    entity_data: Dict[str, Any]


class RelationConnectedPayload(BaseModel):
    """Payload para conexão de nós no grafo."""
    source_id: str
    target_id: str
    relation: EdgeRelation
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PremiseChallengedPayload(BaseModel):
    """Payload de contestação humana (iniciativa mista)."""
    target_claim_id: str
    rationale: str
    suspended_dependent_ids: List[str] = Field(default_factory=list)


class PremiseInvalidatedPayload(BaseModel):
    """Payload de invalidação por evidência empírica."""
    target_claim_id: str
    evidence_id: Optional[str] = None
    suspended_dependent_ids: List[str] = Field(default_factory=list)


class ContradictionRegisteredPayload(BaseModel):
    """Payload de registro de conflito dialético entre proposições."""
    claim_a_id: str
    claim_b_id: str
    rationale: Optional[str] = None


class DecisionRatifiedPayload(BaseModel):
    """Payload de ratificação de CDR."""
    cdr_id: str
    decision_owner: str
    chosen_alternative_ref: str
    scope: str
