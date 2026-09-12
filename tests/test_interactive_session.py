"""Teste do Cenário Dourado do Milestone 1 (M1): Sessão Cognitiva Interativa em 10 Passos."""

from aletheia.cognition.reasoning.synthesizer import CognitiveSynthesizer
from aletheia.core.context.workspace import CognitiveWorkspace
from aletheia.core.entities import (
    ArgumentStance,
    DissentingView,
    EpistemicType,
    LifecycleStatus,
)
from aletheia.core.events.schemas import EdgeRelation
from aletheia.interaction.session import InteractiveSession


def test_m1_golden_scenario_10_steps():
    """Validação ponta a ponta do cenário cognitivo interativo não-linear."""
    session = InteractiveSession(human_name="Aelton")

    # =========================================================================
    # PASSO 1: Humano cria problema
    # =========================================================================
    goal_ids = session.define_problem(
        statement="Definir arquitetura de comunicação e persistência do projeto",
        goals=["Latência previsível", "Custo operacional baixo"],
        constraints=["Agnóstico a domínio", "Sem acoplamento proprietário"],
    )
    assert len(goal_ids) == 3

    # =========================================================================
    # PASSO 2: Aletheia registra contexto
    # =========================================================================
    # Premissas
    claim_fast_lan = session.introduce_claim(
        statement="A rede interna possui latência desprezível (< 1ms)",
        epistemic_type=EpistemicType.ASSUMPTION,
        invalidation_conditions=["Medição de rede apresentar jitter > 10ms"],
    )
    claim_cheap_disk = session.introduce_claim(
        statement="Armazenamento em disco local custa 90% menos que nuvem gerenciada",
        epistemic_type=EpistemicType.ASSUMPTION,
        invalidation_conditions=["Custo de IOPS local superar nuvem"],
    )

    # Alternativas propostas
    alt_sync_rpc = session.propose_alternative(
        title="Arquitetura RPC Síncrona",
        description="Comunicação direta síncrona entre módulos",
        addresses_goal_ids=[goal_ids[0]],
        depends_on_claim_ids=[claim_fast_lan.id],
    )
    alt_local_file = session.propose_alternative(
        title="Persistência em Arquivo Local",
        description="Armazenamento em disco local com baixo custo",
        addresses_goal_ids=[goal_ids[0]],
        depends_on_claim_ids=[claim_cheap_disk.id],
    )

    summary_step2 = session.get_cognitive_summary()
    assert summary_step2["claims_count"] == 2
    assert summary_step2["alternatives_count"] == 2

    # =========================================================================
    # PASSO 3: Aletheia apresenta uma interpretação
    # =========================================================================
    interpretation_step3 = session.get_interpretation()
    assert "A rede interna possui latência desprezível (< 1ms)" in interpretation_step3
    assert "Quer examiná-la?" in interpretation_step3

    # =========================================================================
    # PASSO 4: Humano contesta uma premissa (HumanInitiative)
    # =========================================================================
    affected_nodes = session.challenge_premise(
        claim_id=claim_fast_lan.id,
        rationale="Ambientes em nuvem pública sofrem variações frequentes de jitter",
    )

    # =========================================================================
    # PASSO 5: Kernel suspende derivados
    # =========================================================================
    assert session.workspace.graph.get_node(claim_fast_lan.id).lifecycle_status == LifecycleStatus.UNDER_REVIEW
    assert alt_sync_rpc.id in affected_nodes
    assert session.workspace.graph.get_node(alt_sync_rpc.id).lifecycle_status == LifecycleStatus.SUSPENDED

    # A interpretação pós-contestação agora reflete o bloqueio
    interpretation_step5 = session.get_interpretation()
    assert "SOB REVISÃO/SUSPENSO" in interpretation_step5

    # =========================================================================
    # PASSO 6: Humano muda o foco ("Esquece velocidade por enquanto. Vamos discutir custo.")
    # =========================================================================
    projection_cost = session.change_direction("custo")
    assert session.current_focus == "custo"

    # A projeção de custo deve priorizar a alternativa de disco local e a meta de custo
    cost_node_ids = {n.id for n in projection_cost.salient_nodes}
    assert alt_local_file.id in cost_node_ids
    assert claim_cheap_disk.id in cost_node_ids

    # =========================================================================
    # PASSO 7: Workspace mantém tudo que aconteceu (Imutabilidade Histórica)
    # =========================================================================
    all_nodes_step7 = session.workspace.graph.get_all_nodes()
    node_ids_step7 = {n.id for n in all_nodes_step7}

    assert claim_fast_lan.id in node_ids_step7
    assert alt_sync_rpc.id in node_ids_step7
    # O nó contestado continua UNDER_REVIEW
    assert session.workspace.graph.get_node(claim_fast_lan.id).lifecycle_status == LifecycleStatus.UNDER_REVIEW
    # O nó dependente continua SUSPENDED
    assert session.workspace.graph.get_node(alt_sync_rpc.id).lifecycle_status == LifecycleStatus.SUSPENDED

    # =========================================================================
    # PASSO 8: Nova deliberação parte do estado revisado
    # =========================================================================
    # alt_sync_rpc está inviável por ter premissas sob revisão
    viable_sync, reasons_sync = CognitiveSynthesizer.evaluate_viability(
        session.workspace.graph, alt_sync_rpc.id
    )
    assert viable_sync is False
    assert any("SOB REVISÃO/SUSPENSAS" in r for r in reasons_sync)

    # alt_local_file permanece viável
    viable_local, reasons_local = CognitiveSynthesizer.evaluate_viability(
        session.workspace.graph, alt_local_file.id
    )
    assert viable_local is True
    assert len(reasons_local) == 0

    # =========================================================================
    # PASSO 9: CDR é criado e ratificado no Workspace
    # =========================================================================
    cdr = session.deliberate_and_decide(
        title="Adoção de Persistência em Arquivo Local com Foco em Custo",
        chosen_alt_id=alt_local_file.id,
        scope="Módulo de persistência da Aletheia v0.1",
        underlying_assumptions=[claim_cheap_disk.id],
        human_rationale="Decidido priorizar redução de custo e evitar dependência de rede instável.",
        dissenting_views=[
            DissentingView(
                actor_id="spec_cloud",
                position=ArgumentStance.OPPOSE,
                argument_refs=[],
                rationale="Armazenamento local exige políticas de backup manual mais elaboradas.",
            )
        ],
    )
    assert cdr.chosen_alternative_ref == alt_local_file.id
    assert len(cdr.dissenting_views) == 1
    assert session.workspace.graph.has_node(cdr.id)

    # Verifica aresta SELECTS
    selects_edges = session.workspace.graph.get_outgoing_edges(cdr.id, EdgeRelation.SELECTS)
    assert len(selects_edges) == 1
    assert selects_edges[0].target_id == alt_local_file.id

    # =========================================================================
    # PASSO 10: Replay reproduz exatamente a sessão
    # =========================================================================
    events = session.workspace.event_store.get_all_events()
    assert len(events) >= 12  # Múltiplos passos, introduções, contestação, foco, CDR

    reconstructed_ws = CognitiveWorkspace.replay(events)

    # 1. Compara contagem e integridade dos nós
    orig_nodes = session.workspace.graph.get_all_nodes()
    rep_nodes = reconstructed_ws.graph.get_all_nodes()
    assert len(orig_nodes) == len(rep_nodes)

    for orig in orig_nodes:
        reconstructed_node = reconstructed_ws.graph.get_node(orig.id)
        assert reconstructed_node is not None
        assert reconstructed_node.__class__ == orig.__class__
        if hasattr(orig, "lifecycle_status"):
            assert reconstructed_node.lifecycle_status == orig.lifecycle_status

    # 2. Compara contagem e tuplas de arestas
    orig_edges = session.workspace.graph.get_all_edges()
    rep_edges = reconstructed_ws.graph.get_all_edges()
    assert len(orig_edges) == len(rep_edges)

    orig_edge_set = {(e.source_id, e.target_id, e.relation) for e in orig_edges}
    rep_edge_set = {(e.source_id, e.target_id, e.relation) for e in rep_edges}
    assert orig_edge_set == rep_edge_set

    # 3. Compara contagem de eventos
    assert reconstructed_ws.event_store.count() == session.workspace.event_store.count()
