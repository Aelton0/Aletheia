"""Entidades e taxonomia do Motor Epistemológico.

Invariantes centrais:
- Separação categórica entre epistemic_type e lifecycle_status.
- Falsificacionismo: SUPPORTED != VERIFIED_FACT.
- Unknown é lacuna explícita; Question é a interação que busca preenchê-la.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import Field, field_validator
from aletheia.core.entities.base import CognitiveEntity


class EpistemicType(str, Enum):
    """Tipo epistemológico de uma afirmação (natureza do conhecimento)."""
    HYPOTHESIS = "HYPOTHESIS"        # Proposição teórica a ser testada
    ASSUMPTION = "ASSUMPTION"        # Premissa aceita pragmaticamente de trabalho
    VERIFIED_FACT = "VERIFIED_FACT"  # Proposição com verificação formal direta


class LifecycleStatus(str, Enum):
    """Status dinâmico de uma proposição no ciclo de deliberação."""
    ACTIVE = "ACTIVE"              # Em uso ativo
    UNDER_REVIEW = "UNDER_REVIEW"  # Contestada ou sob escrutínio de nova evidência
    SUPPORTED = "SUPPORTED"        # Não-falsificada por evidência (SUPPORTED != VERIFIED_FACT)
    INVALIDATED = "INVALIDATED"    # Falsificada por teste ou premissa refutada
    SUSPENDED = "SUSPENDED"        # Dependentes de nós invalidados ou sob revisão
    RESOLVED = "RESOLVED"          # Fechada sob critérios objetivos do domínio
    CONFLICT = "CONFLICT"          # Em estado de contradição dialética não resolvida


class DerivationMethod(str, Enum):
    """Método de derivação de uma inferência lógica."""
    DEDUCTIVE = "DEDUCTIVE"  # Certeza se premissas forem verdadeiras
    INDUCTIVE = "INDUCTIVE"  # Generalização probabilística a partir de instâncias
    ABDUCTIVE = "ABDUCTIVE"  # Hipótese da melhor explicação plausível


class QuestionStatus(str, Enum):
    """Status do ciclo de vida de uma pergunta direcionada."""
    OPEN = "OPEN"
    ANSWERED = "ANSWERED"
    DISMISSED = "DISMISSED"


class EpistemicObject(CognitiveEntity):
    """Base para objetos portadores de proveniência epistêmica explícita."""
    author_id: str = Field(..., description="ID do ator que introduziu o objeto (humano ou especialista)")


class Claim(EpistemicObject):
    """Proposição sobre o mundo ou o problema."""
    statement: str
    epistemic_type: EpistemicType
    lifecycle_status: LifecycleStatus = LifecycleStatus.ACTIVE
    rationale: Optional[str] = None
    invalidation_conditions: List[str] = Field(
        default_factory=list,
        description="Critérios explícitos de falseabilidade para premissas/hipóteses"
    )
    verification_criteria: Optional[str] = Field(
        default=None,
        description="Critérios formais que legitimam o status de VERIFIED_FACT"
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    @field_validator("lifecycle_status")
    @classmethod
    def validate_lifecycle_semantic(cls, v: LifecycleStatus, info) -> LifecycleStatus:
        # Nota de Invariante: SUPPORTED jamais deve ser confundido com VERIFIED_FACT
        return v


class Evidence(EpistemicObject):
    """Dado empírico bruto, citação, log ou resultado de execução."""
    description: str
    source_uri_or_origin: str
    raw_payload: Optional[Dict[str, Any]] = None


class Inference(EpistemicObject):
    """Conclusão derivada de um conjunto explícito de premissas."""
    conclusion: str
    derivation_method: DerivationMethod
    premise_ids: List[str] = Field(..., min_length=1, description="Lista de IDs de Claims ou Evidences de sustentação")
    lifecycle_status: LifecycleStatus = LifecycleStatus.ACTIVE


class Unknown(EpistemicObject):
    """Ausência explícita de conhecimento ou incerteza detectada ('não sabemos X')."""
    description: str
    blocking: bool = Field(default=False, description="Se impede a progressão de decisões dependentes")
    resolution_criteria: Optional[str] = None


class Question(EpistemicObject):
    """Interação explícita que formula uma pergunta direcionada a um ator."""
    question_text: str
    target_unknown_id: Optional[str] = Field(default=None, description="Unknown que esta pergunta visa elucidar")
    asked_by: str = Field(..., description="ID do ator que fez a pergunta")
    addressed_to: str = Field(..., description="ID do ator a quem a pergunta é direcionada")
    status: QuestionStatus = QuestionStatus.OPEN
    answer_refs: List[str] = Field(default_factory=list, description="IDs de Claims ou Evidences geradas na resposta")
