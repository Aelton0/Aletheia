"""Testes da Fronteira de Segurança Cognitiva do M3: Validação Estrutural e Epistêmica."""

from aletheia.cognition.adapters.llm.epistemic_validator import (
    EpistemicSupportLevel,
    EpistemicValidator,
    ValidationStatus,
)
from aletheia.cognition.adapters.llm.schemas import (
    LLMArgumentProposal,
    LLMCritiquePayload,
    LLMUnknownProposal,
)
from aletheia.cognition.adapters.llm.structural_validator import StructuralValidator
from aletheia.core.context.projection import CognitiveProjection
from aletheia.core.entities import (
    Alternative,
    ArgumentStance,
    Claim,
    EpistemicType,
    LifecycleStatus,
)


def test_structural_validator_purges_hallucinated_ids():
    """Validação da Camada 1: Purga IDs alucinados pelo modelo probabilístico."""
    alt = Alternative(id="alt_valid", title="Alt Válida", description="Desc")
    claim = Claim(id="claim_valid", author_id="h1", statement="Premissa válida", epistemic_type=EpistemicType.ASSUMPTION)

    projection = CognitiveProjection(
        salient_nodes=[alt, claim],
    )

    # Payload adversarial com IDs inventados
    adversarial_payload = LLMCritiquePayload(
        target_alternative_id="alt_valid",
        arguments=[
            LLMArgumentProposal(
                alternative_id="alt_valid",
                stance=ArgumentStance.OPPOSE,
                premise_refs=["claim_valid", "claim_HALLUCINATED_999", "ghost_node"],
                rationale="Crítica citando premissas reais e fantasmas",
            )
        ],
        unknowns=[LLMUnknownProposal(description="Dúvida")],
        model_confidence=0.95,
        reasoning_summary="Resumo",
    )

    result = StructuralValidator.validate(adversarial_payload, projection)

    # 2 IDs alucinados foram capturados
    assert len(result.hallucinated_ids) == 2
    assert "claim_HALLUCINATED_999" in result.hallucinated_ids
    assert "ghost_node" in result.hallucinated_ids

    # O payload purgado contém apenas o ID válido autorizado
    assert result.purged_payload is not None
    assert result.purged_payload.arguments[0].premise_refs == ["claim_valid"]


def test_epistemic_validator_separates_confidence_from_epistemic_support():
    """Validação da Camada 2: Separa a confiança do modelo do suporte epistemológico conferido pelo Kernel."""
    alt = Alternative(id="alt_1", title="Alt 1", description="Desc")
    assump = Claim(
        id="assump_1",
        author_id="h1",
        statement="Apenas uma suposição não testada",
        epistemic_type=EpistemicType.ASSUMPTION,
        lifecycle_status=LifecycleStatus.ACTIVE,
    )

    projection = CognitiveProjection(
        salient_nodes=[alt, assump],
    )

    payload = LLMCritiquePayload(
        target_alternative_id="alt_1",
        arguments=[
            LLMArgumentProposal(
                alternative_id="alt_1",
                stance=ArgumentStance.OPPOSE,
                premise_refs=["assump_1"],
                rationale="A alternativa assume premissa não testada com risco de impacto.",
                critical_depth_score=3,
            )
        ],
        unknowns=[LLMUnknownProposal(description="Incerteza")],
        model_confidence=0.99,  # Modelo autodeclara certeza quase absoluta
        reasoning_summary="Análise",
    )

    epistemic_res = EpistemicValidator.validate(payload, projection)

    # Mesmo com confidence 0.99 do LLM, o Kernel atribui MEDIUM porque apoia-se em Assumption, não em Fact
    assert epistemic_res.status == ValidationStatus.ACCEPTED
    assert epistemic_res.epistemic_support == EpistemicSupportLevel.MEDIUM
    assert epistemic_res.cgr_score == 1.0
