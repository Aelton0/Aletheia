"""Teste integrador de ponta a ponta: LLMCritiqueCapability dentro do CapabilityRuntime."""

from aletheia.adapters.mock_llm_adapter import MockLLMAdapter
from aletheia.cognition.adapters.llm.schemas import (
    LLMArgumentProposal,
    LLMCritiquePayload,
    LLMUnknownProposal,
)
from aletheia.cognition.capabilities.llm_critique import LLMCritiqueCapability
from aletheia.cognition.runtime import CapabilityRuntime
from aletheia.core.context.workspace import CognitiveWorkspace
from aletheia.core.entities import (
    Alternative,
    Argument,
    ArgumentStance,
    Claim,
    EpistemicType,
    HumanActor,
    LifecycleStatus,
    Unknown,
)
from aletheia.core.events.schemas import EdgeRelation


def test_llm_critique_capability_end_to_end_in_runtime():
    """Ciclo completo: Workspace -> StateAnalyzer -> Selector -> Projection -> LLMCritiqueCapability -> Kernel -> Event -> Replay."""
    workspace = CognitiveWorkspace()
    mock_llm = MockLLMAdapter()

    # Prepara resposta estruturada do mock
    fixture_critique = LLMCritiquePayload(
        target_alternative_id="alt_cloud_sync",
        arguments=[
            LLMArgumentProposal(
                alternative_id="alt_cloud_sync",
                stance=ArgumentStance.OPPOSE,
                premise_refs=["assump_unlimited_bw"],
                rationale="A alternativa assume largura de banda ilimitada e sem custo de egresso, o que pode gerar fatura abusiva sob carga de pico.",
                critical_depth_score=4,
            )
        ],
        unknowns=[
            LLMUnknownProposal(
                description="Qual é a cota máxima de transferência mensal prevista antes do limite de custo?",
                blocking=False,
            )
        ],
        model_confidence=0.91,
        reasoning_summary="Crítica focada no custo de egresso de rede.",
    )
    mock_llm.register_fixture("contexto autorizado", fixture_critique)

    runtime = CapabilityRuntime()
    llm_cap = LLMCritiqueCapability(llm_provider=mock_llm)
    runtime.registry.register(llm_cap)

    human = HumanActor.create_default("Aelton")
    workspace.introduce_entity(human, actor_id=human.id)

    # 1. Cria Alternativa e Suposição
    alt = Alternative(
        id="alt_cloud_sync",
        title="Sincronização em Nuvem em Tempo Real",
        description="Replica cada mutação do workspace diretamente em bucket S3",
    )
    assump = Claim(
        id="assump_unlimited_bw",
        author_id=human.id,
        statement="O custo de transferência de dados (egress) é desprezível",
        epistemic_type=EpistemicType.ASSUMPTION,
        lifecycle_status=LifecycleStatus.ACTIVE,
    )
    workspace.introduce_entity(alt, actor_id=human.id)
    workspace.introduce_entity(assump, actor_id=human.id)
    workspace.connect(alt.id, assump.id, EdgeRelation.DEPENDS_ON, actor_id=human.id)

    # 2. Executa step do runtime com a LLMCritiqueCapability
    result = runtime.step(workspace)
    assert result is not None
    assert result.capability_name == "LLMCritiqueCapability"
    assert len(result.produced_entities) == 2

    # 3. Verifica entidades no Workspace
    args = [n for n in workspace.graph.get_all_nodes() if isinstance(n, Argument)]
    assert len(args) == 1
    produced_arg = args[0]
    assert produced_arg.alternative_id == alt.id
    assert produced_arg.stance == ArgumentStance.OPPOSE
    assert "egresso" in produced_arg.rationale

    # Verifica metadados de observabilidade
    assert produced_arg.metadata["model"] == "mock-deterministic-v1"
    assert produced_arg.metadata["model_confidence"] == 0.91
    assert produced_arg.metadata["epistemic_support"] == "MEDIUM"
    assert produced_arg.metadata["rhr_score"] == 0.0

    # 4. Verifica arestas no grafo
    opposes_edges = workspace.graph.get_outgoing_edges(produced_arg.id, EdgeRelation.OPPOSES)
    assert len(opposes_edges) == 1
    assert opposes_edges[0].target_id == alt.id

    # 5. Verifica Replay Determinístico
    events = workspace.event_store.get_all_events()
    assert len(events) >= 5

    replayed = CognitiveWorkspace.replay(events)
    assert len(replayed.graph.get_all_nodes()) == len(workspace.graph.get_all_nodes())
    assert len(replayed.graph.get_all_edges()) == len(workspace.graph.get_all_edges())
