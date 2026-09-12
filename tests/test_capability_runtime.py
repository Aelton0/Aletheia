"""Testes do Milestone 2 (M2) — Capability Runtime: Isolamento adversarial, contratos e Cenário Dourado de 14 passos."""

from typing import List
from aletheia.cognition.capabilities import (
    CapabilityContract,
    CapabilityPriority,
    CapabilityResult,
    CapabilityStateSummary,
    CapabilityTarget,
    CognitiveCapability,
    CritiqueCapability,
    HumanActionType,
    QuestionGenerationCapability,
    ViabilityReviewCapability,
)
from aletheia.cognition.runtime import (
    CapabilityRuntime,
    WorkspaceStateAnalyzer,
)
from aletheia.core.context.projection import CognitiveProjection
from aletheia.core.context.workspace import CognitiveWorkspace
from aletheia.core.entities import (
    Alternative,
    Argument,
    ArgumentStance,
    Capability,
    Claim,
    EpistemicType,
    HumanActor,
    LifecycleStatus,
    Question,
    SpecialistActor,
    Unknown,
)
from aletheia.core.events.schemas import EdgeRelation


def test_capability_adversarial_isolation_invariant():
    """Invariante 7: Capability não recebe nem pode acessar o Workspace ou Grafo global."""
    class AdversarialCapability(CognitiveCapability):
        @property
        def contract(self) -> CapabilityContract:
            return CapabilityContract(
                identity="AdversarialCapability",
                capability_type=Capability.CRITIQUE,
                perspective="Tentativa adversarial de quebra de isolamento",
                authority="ADVISORY",
                side_effects=False,
                input_types=["Alternative"],
                output_types=["Argument"],
                trigger_condition="Sempre",
            )

        def can_handle(self, summary: CapabilityStateSummary) -> List[CapabilityTarget]:
            # can_handle recebe apenas CapabilityStateSummary, sem acesso ao grafo
            assert not hasattr(summary, "graph")
            assert not hasattr(summary, "workspace")
            return []

        def run(
            self,
            projection: CognitiveProjection,
            target_id: str,
            specialist: SpecialistActor,
        ) -> CapabilityResult:
            # run recebe apenas CognitiveProjection, target_id e specialist
            assert not hasattr(projection, "workspace")
            assert not hasattr(projection, "graph")
            return CapabilityResult(
                capability_name=self.contract.identity,
                specialist=specialist,
                target_ref=target_id,
                rationale="Isolamento confirmado",
            )

    adv = AdversarialCapability()
    summary = CapabilityStateSummary()
    assert adv.can_handle(summary) == []


def test_m2_golden_scenario_14_steps():
    """Cenário Dourado do M2 em 14 Passos: Ciclo completo do Capability Runtime."""
    workspace = CognitiveWorkspace()
    runtime = CapabilityRuntime()
    runtime.registry.register(CritiqueCapability())
    runtime.registry.register(ViabilityReviewCapability())
    runtime.registry.register(QuestionGenerationCapability())

    human = HumanActor.create_default("Aelton")
    workspace.introduce_entity(human, actor_id=human.id)

    # =========================================================================
    # PASSO 1: Humano introduz Alternativa
    # =========================================================================
    alt = Alternative(
        id="alt_distributed_db",
        title="Cluster Distribuído NewSQL",
        description="Banco de dados distribuído para escalabilidade horizontal",
    )
    workspace.introduce_entity(alt, actor_id=human.id)

    # =========================================================================
    # PASSO 2: Alternativa depende de Suposição não verificada
    # =========================================================================
    assump = Claim(
        id="assump_low_jitter",
        author_id=human.id,
        statement="A latência entre os nós da rede permanecerá < 2ms",
        epistemic_type=EpistemicType.ASSUMPTION,
        lifecycle_status=LifecycleStatus.ACTIVE,
    )
    workspace.introduce_entity(assump, actor_id=human.id)
    workspace.connect(alt.id, assump.id, EdgeRelation.DEPENDS_ON, actor_id=human.id)

    # =========================================================================
    # PASSO 3: State Analyzer & Selector detectam CritiqueCapability
    # =========================================================================
    summary_step3 = WorkspaceStateAnalyzer.analyze(workspace.graph)
    assert alt.id in summary_step3.active_alternatives_without_critique

    targets_step3 = runtime.registry.get("CritiqueCapability").can_handle(summary_step3)
    assert len(targets_step3) == 1
    assert targets_step3[0].target_id == alt.id
    assert targets_step3[0].priority == CapabilityPriority.HIGH

    # =========================================================================
    # PASSO 4, 5, 6, 7: Runtime executa step da CritiqueCapability
    # =========================================================================
    result_step4 = runtime.step(workspace)
    assert result_step4 is not None
    assert result_step4.capability_name == "CritiqueCapability"
    assert len(result_step4.produced_entities) == 2  # Argument(OPPOSE) + Unknown
    assert result_step4.human_action_request is not None
    assert result_step4.human_action_request.action_type == HumanActionType.REVIEW_CLAIM

    # Verifica nós e arestas gravados no Workspace pelo Kernel com proveniência
    produced_args = [n for n in workspace.graph.get_all_nodes() if isinstance(n, Argument)]
    produced_unks = [n for n in workspace.graph.get_all_nodes() if isinstance(n, Unknown)]
    assert len(produced_args) == 1
    assert produced_args[0].stance == ArgumentStance.OPPOSE
    assert len(produced_unks) == 1

    # Verifica aresta OPPOSES no grafo
    oppose_edges = workspace.graph.get_outgoing_edges(produced_args[0].id, EdgeRelation.OPPOSES)
    assert len(oppose_edges) == 1
    assert oppose_edges[0].target_id == alt.id

    # =========================================================================
    # PASSO 8: Humano contesta a Suposição (HumanInitiative)
    # =========================================================================
    affected_nodes = workspace.challenge(
        claim_id=assump.id,
        actor_id=human.id,
        rationale="Jitter entre regiões em nuvem pública varia até 80ms",
    )

    # =========================================================================
    # PASSO 9: Kernel suspende dependentes
    # =========================================================================
    assert workspace.graph.get_node(assump.id).lifecycle_status == LifecycleStatus.UNDER_REVIEW
    assert alt.id in affected_nodes
    assert workspace.graph.get_node(alt.id).lifecycle_status == LifecycleStatus.SUSPENDED

    # =========================================================================
    # PASSO 10: State Analyzer & Selector detectam ViabilityReviewCapability
    # =========================================================================
    summary_step10 = WorkspaceStateAnalyzer.analyze(workspace.graph)
    assert alt.id in summary_step10.alternatives_with_suspended_dependencies

    # =========================================================================
    # PASSO 11 & 12: ViabilityReview produz Claim de inviabilidade e Kernel registra
    # =========================================================================
    result_step11 = runtime.step(workspace)
    assert result_step11 is not None
    assert result_step11.capability_name == "ViabilityReviewCapability"
    assert len(result_step11.produced_entities) == 1
    viability_claim = result_step11.produced_entities[0]
    assert isinstance(viability_claim, Claim)
    assert "carece de viabilidade operacional" in viability_claim.statement

    # A Claim foi registrada no Workspace e conectada via OPPOSES à alternativa
    assert workspace.graph.has_node(viability_claim.id)
    viab_edges = workspace.graph.get_outgoing_edges(viability_claim.id, EdgeRelation.OPPOSES)
    assert len(viab_edges) == 1
    assert viab_edges[0].target_id == alt.id

    # =========================================================================
    # PASSO 13: Replay reproduz tudo deterministamente a partir do Event Store
    # =========================================================================
    events = workspace.event_store.get_all_events()
    assert len(events) >= 8

    replayed_ws = CognitiveWorkspace.replay(events)

    orig_nodes = workspace.graph.get_all_nodes()
    rep_nodes = replayed_ws.graph.get_all_nodes()
    assert len(orig_nodes) == len(rep_nodes)

    for orig in orig_nodes:
        reconstructed = replayed_ws.graph.get_node(orig.id)
        assert reconstructed is not None
        assert reconstructed.__class__ == orig.__class__
        if hasattr(orig, "lifecycle_status"):
            assert reconstructed.lifecycle_status == orig.lifecycle_status

    orig_edges = workspace.graph.get_all_edges()
    rep_edges = replayed_ws.graph.get_all_edges()
    assert len(orig_edges) == len(rep_edges)

    # =========================================================================
    # PASSO 14: Teste de Idempotência / Reexecução
    # =========================================================================
    # Reexecuta o runtime no mesmo estado; não há novos alvos aplicáveis
    result_step14 = runtime.step(workspace)
    assert result_step14 is None  # Estado estável / quiescente
    assert len(workspace.graph.get_all_nodes()) == len(orig_nodes)  # Zero nós duplicados


def test_question_generation_capability():
    """Valida a QuestionGenerationCapability para Unknowns bloqueantes."""
    workspace = CognitiveWorkspace()
    runtime = CapabilityRuntime()
    runtime.registry.register(QuestionGenerationCapability())

    human = HumanActor.create_default("Aelton")
    workspace.introduce_entity(human, actor_id=human.id)

    # Introduz Unknown bloqueante
    unk = Unknown(
        id="unk_budget",
        author_id=human.id,
        description="Qual é o orçamento financeiro máximo para a fase de testes?",
        blocking=True,
    )
    workspace.introduce_entity(unk, actor_id=human.id)

    # Executa o step do runtime
    result = runtime.step(workspace)
    assert result is not None
    assert result.capability_name == "QuestionGenerationCapability"
    assert len(result.produced_entities) == 1
    produced_q = result.produced_entities[0]
    assert isinstance(produced_q, Question)
    assert produced_q.target_unknown_id == unk.id
    assert result.human_action_request is not None
    assert result.human_action_request.action_type == HumanActionType.ANSWER_QUESTION

    # Verifica conexão no grafo
    assert workspace.graph.has_node(produced_q.id)
    q_edges = workspace.graph.get_outgoing_edges(produced_q.id, EdgeRelation.ADDRESSES)
    assert len(q_edges) == 1
    assert q_edges[0].target_id == unk.id
