"""Camada 1 de Validação: Validação Estrutural e Integridade de Referências (RHR).

Garante que nenhum ID alucinado pelo LLM atravesse a fronteira de segurança.
"""

from typing import List, Optional, Set
from pydantic import BaseModel, Field
from aletheia.cognition.adapters.llm.schemas import (
    LLMArgumentProposal,
    LLMCritiquePayload,
)
from aletheia.core.context.projection import CognitiveProjection


class StructuralValidationResult(BaseModel):
    """Resultado da auditoria estrutural do output de LLM."""
    is_valid: bool
    purged_payload: Optional[LLMCritiquePayload] = None
    hallucinated_ids: List[str] = Field(default_factory=list)
    structural_errors: List[str] = Field(default_factory=list)
    rhr_score: float = 0.0  # Referential Hallucination Rate (0.0 = 0% alucinação)


class StructuralValidator:
    """Audita a integridade estrutural e referencial do payload probabilístico."""

    @staticmethod
    def validate(
        payload: LLMCritiquePayload,
        projection: CognitiveProjection,
    ) -> StructuralValidationResult:
        """Inspeciona o payload contra os nós autorizados da projeção."""
        authorized_ids: Set[str] = {n.id for n in projection.salient_nodes}
        hallucinated_ids: List[str] = []
        structural_errors: List[str] = []
        total_references_cited = 0

        # 1. Valida se a alternativa alvo existe no contexto autorizado
        if payload.target_alternative_id not in authorized_ids:
            structural_errors.append(
                f"Alucinação de alvo: Alternativa '{payload.target_alternative_id}' não existe no contexto autorizado."
            )
            hallucinated_ids.append(payload.target_alternative_id)

        # 2. Inspeciona argumentos e purga premissas alucinadas
        cleaned_arguments: List[LLMArgumentProposal] = []

        for arg in payload.arguments:
            valid_premise_refs = []
            for ref in arg.premise_refs:
                total_references_cited += 1
                if ref in authorized_ids:
                    valid_premise_refs.append(ref)
                else:
                    hallucinated_ids.append(ref)

            # Preserva o argumento apenas se tiver fundamentação válida na projeção
            if valid_premise_refs or not arg.premise_refs:
                cleaned_arg = arg.model_copy(update={"premise_refs": valid_premise_refs})
                cleaned_arguments.append(cleaned_arg)
            else:
                structural_errors.append(
                    f"Argumento descartado: todas as premissas citadas eram alucinadas ({arg.premise_refs})."
                )

        # Cálculo da métrica RHR (Referential Hallucination Rate)
        rhr = (len(hallucinated_ids) / total_references_cited) if total_references_cited > 0 else (1.0 if hallucinated_ids else 0.0)

        is_valid = len(structural_errors) == 0

        purged_payload = payload.model_copy(
            update={
                "arguments": cleaned_arguments,
            }
        )

        return StructuralValidationResult(
            is_valid=is_valid,
            purged_payload=purged_payload,
            hallucinated_ids=hallucinated_ids,
            structural_errors=structural_errors,
            rhr_score=rhr,
        )
