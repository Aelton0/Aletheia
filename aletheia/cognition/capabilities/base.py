"""Contratos formais e primitivos do Capability Model (M2).

Invariantes centrais:
- Isolamento cognitivo: Capability recebe apenas CognitiveProjection.
- Autoridade consultiva (ADVISORY): Capability emite CapabilityResult; Kernel valida e aplica.
- Autoria explícita por SpecialistActor.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from aletheia.core.context.projection import CognitiveProjection
from aletheia.core.entities import Capability, CognitiveEntity, SpecialistActor
from aletheia.core.events.schemas import EdgeRelation


class CapabilityAuthority(str, Enum):
    """Grau de autoridade de uma capacidade cognitiva sobre o estado do sistema."""
    ADVISORY = "ADVISORY"  # Emite propostas e análises; Kernel detém autoridade sobre o estado


class HumanActionType(str, Enum):
    """Tipos formais de intervenção solicitada ao humano."""
    REVIEW_CLAIM = "REVIEW_CLAIM"
    ANSWER_QUESTION = "ANSWER_QUESTION"
    RESOLVE_CONFLICT = "RESOLVE_CONFLICT"
    DECIDE_ALTERNATIVE = "DECIDE_ALTERNATIVE"


class HumanActionRequest(BaseModel):
    """Solicitação tipada de ação ou julgamento humano emitida por uma capacidade."""
    action_type: HumanActionType
    target_ref: str
    reason: str
    required: bool = False


class CapabilityPriority(str, Enum):
    """Prioridade de despacho cognitivo."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class CapabilityTarget(BaseModel):
    """Alvo identificado pelo Seletor como demandante de atenção cognitiva."""
    capability_name: str
    target_id: str
    reason: str
    priority: CapabilityPriority = CapabilityPriority.NORMAL


class ProposedRelation(BaseModel):
    """Relação semântica proposta pela capacidade para conexão no grafo."""
    source_id: str
    target_id: str
    relation: EdgeRelation
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CapabilityResult(BaseModel):
    """Resultado estruturado e consultivo da execução de uma capacidade cognitiva."""
    capability_name: str
    specialist: SpecialistActor
    target_ref: str
    produced_entities: List[CognitiveEntity] = Field(default_factory=list)
    proposed_relations: List[ProposedRelation] = Field(default_factory=list)
    human_action_request: Optional[HumanActionRequest] = None
    rationale: str


class CapabilityContract(BaseModel):
    """Declaração formal das propriedades e limites de uma capacidade cognitiva."""
    identity: str
    capability_type: Capability
    perspective: str
    authority: CapabilityAuthority = CapabilityAuthority.ADVISORY
    side_effects: bool = False
    input_types: List[str]
    output_types: List[str]
    trigger_condition: str


class CapabilityStateSummary(BaseModel):
    """Resumo de estado derivado pelo Kernel (não expõe o grafo para a capacidade)."""
    active_alternatives_without_critique: List[str] = Field(default_factory=list)
    unresolved_blocking_unknowns: List[str] = Field(default_factory=list)
    alternatives_with_suspended_dependencies: List[str] = Field(default_factory=list)


class CognitiveCapability(ABC):
    """Contrato base abstrato para capacidades cognitivas puras."""

    @property
    @abstractmethod
    def contract(self) -> CapabilityContract:
        """Retorna o contrato formal da capacidade."""
        pass

    @abstractmethod
    def can_handle(self, summary: CapabilityStateSummary) -> List[CapabilityTarget]:
        """Avalia alvos aplicáveis usando unicamente o resumo de estado derivado."""
        pass

    @abstractmethod
    def run(
        self,
        projection: CognitiveProjection,
        target_id: str,
        specialist: SpecialistActor,
    ) -> CapabilityResult:
        """Executa a análise sobre a projeção contextual autorizada, sem tocar no Workspace."""
        pass
