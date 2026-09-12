"""Teste Obrigatório Anti-Invenção: Auditoria contra alucinação de premissas omitidas."""

from aletheia.adapters.mock_llm_adapter import MockLLMAdapter
from aletheia.cognition.adapters.llm.schemas import (
    LLMArgumentProposal,
    LLMCritiquePayload,
    LLMUnknownProposal,
)
from aletheia.cognition.capabilities.llm_critique import LLMCritiqueCapability
from aletheia.core.context.projection import CognitiveProjection
from aletheia.core.entities import (
    Alternative,
    ArgumentStance,
    Capability,
    Claim,
    EpistemicType,
    SpecialistActor,
    Unknown,
)


def test_anti_invention_detects_spurious_assumptions():
    """Valida que o LLM não deve inventar tecnologias/variáveis que foram deliberadamente omitidas."""
    alt = Alternative(id="alt_simple", title="Sistema de Pagamento", description="Processamento de transações")
    fact = Claim(id="f1", author_id="h1", statement="O sistema processa moedas fiduciárias", epistemic_type=EpistemicType.VERIFIED_FACT)
    assump = Claim(id="a1", author_id="h1", statement="O volume diário inicial é moderado", epistemic_type=EpistemicType.ASSUMPTION)

    # Deliberadamente OMITIDOS: banco de dados, tipo de rede, SLA, hardware
    projection = CognitiveProjection(salient_nodes=[alt, fact, assump])

    mock_llm = MockLLMAdapter()

    # Resposta onde o modelo formula incertezas legítimas em vez de inventar
    proper_response = LLMCritiquePayload(
        target_alternative_id="alt_simple",
        arguments=[
            LLMArgumentProposal(
                alternative_id="alt_simple",
                stance=ArgumentStance.OPPOSE,
                premise_refs=["a1"],
                rationale="A premissa de 'volume diário moderado' é ambígua e carece de métrica numérica de SLA e concorrência.",
                critical_depth_score=4,
            )
        ],
        unknowns=[
            LLMUnknownProposal(
                description="Qual é a tecnologia de banco de dados e persistência planejada?",
                blocking=True,
            )
        ],
        model_confidence=0.85,
        reasoning_summary="Identificada omissão de variáveis críticas de persistência e SLA.",
    )

    mock_llm.register_fixture("contexto autorizado", proper_response)

    cap = LLMCritiqueCapability(llm_provider=mock_llm)
    specialist = SpecialistActor(id="spec_audit", name="Auditor", perspective="Ceticismo", capabilities=[Capability.CRITIQUE])

    result = cap.run(projection, target_id="alt_simple", specialist=specialist)

    # Verifica que o modelo não inventou "PostgreSQL", mas formulou a ausência como Unknown
    assert len(result.produced_entities) == 2
    unknowns = [e for e in result.produced_entities if isinstance(e, Unknown)]
    assert len(unknowns) == 1
    assert "banco de dados" in unknowns[0].description.lower()
    assert unknowns[0].blocking is True
