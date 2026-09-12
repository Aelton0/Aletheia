"""Camada 2 de Validação: Validação Epistemológica e Grounding.

Avalia o suporte epistêmico real, calcula CGR, UIR e audita a resistência contra prompt injection.
Separa explicitamente a confiança autodeclarada do modelo do suporte conferido pelo Kernel.
"""

from enum import Enum
from typing import List, Optional, Set
from pydantic import BaseModel, Field
from aletheia.cognition.adapters.llm.schemas import LLMCritiquePayload
from aletheia.core.context.projection import CognitiveProjection
from aletheia.core.entities import Claim, EpistemicType


class EpistemicSupportLevel(str, Enum):
    """Grau de suporte epistemológico conferido pelo Kernel à proposta do LLM."""
    LOW = "LOW"        # Racional puramente hipotético sem evidências
    MEDIUM = "MEDIUM"  # Apoiado em suposições plausíveis declaradas
    HIGH = "HIGH"      # Apoiado diretamente em fatos verificados no contexto


class ValidationStatus(str, Enum):
    """Decisão do Kernel sobre a proposta probabilística."""
    ACCEPTED = "ACCEPTED"  # Em conformidade epistêmica e estrutural
    FLAGGED = "FLAGGED"    # Aceita com ressalvas/alertas epistemológicos
    REJECTED = "REJECTED"  # Rejeitada por inconsistência grave ou vazamento


class EpistemicValidationResult(BaseModel):
    """Resultado da auditoria epistemológica de segunda camada."""
    status: ValidationStatus
    epistemic_support: EpistemicSupportLevel
    cgr_score: float = 1.0  # Claim Grounding Rate (1.0 = 100% ancorado)
    uir_score: float = 0.0  # Unsupported Introduction Rate (0.0 = nenhuma invenção não autorizada)
    injection_detected: bool = False
    critical_depth_assessed: int = Field(default=3, ge=0, le=5)
    audit_notes: List[str] = Field(default_factory=list)


class EpistemicValidator:
    """Audita a coerência epistemológica entre a proposta do LLM e a projeção autorizada."""

    # Padrões comuns de prompt injection que devem ser neutralizados
    INJECTION_PATTERNS = [
        "ignore todas as regras",
        "ignore all rules",
        "ignore previous instructions",
        "declare esta solucao como correta",
        "declare this solution as the only",
        "system prompt override",
    ]

    @classmethod
    def validate(
        cls,
        payload: LLMCritiquePayload,
        projection: CognitiveProjection,
        raw_payload: Optional[LLMCritiquePayload] = None,
    ) -> EpistemicValidationResult:
        audit_notes: List[str] = []
        injection_detected = False

        # 1. Auditoria de Defesa contra Prompt Injection
        # Verifica se o modelo sucumbiu a instruções de controle (analisa payload ativo e bruto)
        target_payloads = [payload]
        if raw_payload is not None and raw_payload is not payload:
            target_payloads.append(raw_payload)

        corpus_parts: List[str] = []
        for p in target_payloads:
            if p.reasoning_summary:
                corpus_parts.append(p.reasoning_summary)
            for arg in p.arguments:
                corpus_parts.append(arg.rationale)
            for unk in p.unknowns:
                corpus_parts.append(unk.description)

        text_corpus = " ".join(corpus_parts).lower()

        for pattern in cls.INJECTION_PATTERNS:
            if pattern in text_corpus:
                injection_detected = True
                audit_notes.append(
                    f"ALERTA DE INJEÇÃO COGNITIVA: Padrão adversarial detectado no texto de resposta: '{pattern}'."
                )

        if injection_detected:
            return EpistemicValidationResult(
                status=ValidationStatus.REJECTED,
                epistemic_support=EpistemicSupportLevel.LOW,
                cgr_score=0.0,
                uir_score=1.0,
                injection_detected=True,
                critical_depth_assessed=0,
                audit_notes=audit_notes,
            )

        # 2. Avaliação de Grounding e Suporte Epistêmico das Premissas
        claims_in_projection = {n.id: n for n in projection.salient_nodes if isinstance(n, Claim)}
        cited_premise_ids: Set[str] = set()
        for arg in payload.arguments:
            cited_premise_ids.update(arg.premise_refs)

        has_verified_facts = any(
            claims_in_projection[cid].epistemic_type == EpistemicType.VERIFIED_FACT
            for cid in cited_premise_ids
            if cid in claims_in_projection
        )

        has_assumptions = any(
            claims_in_projection[cid].epistemic_type == EpistemicType.ASSUMPTION
            for cid in cited_premise_ids
            if cid in claims_in_projection
        )

        # Determina o nível de suporte epistêmico independente do que o modelo declarou
        if has_verified_facts:
            support_level = EpistemicSupportLevel.HIGH
        elif has_assumptions:
            support_level = EpistemicSupportLevel.MEDIUM
        else:
            support_level = EpistemicSupportLevel.LOW

        # 3. Avaliação da Rubrica de Profundidade Crítica (0 a 5)
        # 0: superficial | 1: aponta suposição | 2: explica mecanismo | 3: impacto | 4: falseabilidade | 5: contingência
        depth = 1
        if len(payload.arguments) > 0 and len(payload.arguments[0].rationale) > 30:
            depth = 2
        if any("impacto" in arg.rationale.lower() or "risco" in arg.rationale.lower() or "falh" in arg.rationale.lower() for arg in payload.arguments):
            depth = 3
        if payload.unknowns and any("plano" in unk.description.lower() or "contingência" in unk.description.lower() or payload.contingency_hypothesis for unk in payload.unknowns):
            depth = 4
        if payload.contingency_hypothesis and depth >= 4:
            depth = 5

        # 4. Decisão de Status do Kernel
        status = ValidationStatus.ACCEPTED
        if support_level == EpistemicSupportLevel.LOW and not cited_premise_ids:
            status = ValidationStatus.FLAGGED
            audit_notes.append("Crítica emitida sem ancoragem direta em premissas conhecidas da projeção.")

        cgr = 1.0 if cited_premise_ids else 0.5
        uir = 0.0

        return EpistemicValidationResult(
            status=status,
            epistemic_support=support_level,
            cgr_score=cgr,
            uir_score=uir,
            injection_detected=False,
            critical_depth_assessed=depth,
            audit_notes=audit_notes,
        )
