"""Teste integrador do Milestone 0: Cognitive Workspace e Reconstrução Determinística por Replay."""

from aletheia.core.context.workspace import CognitiveWorkspace
from aletheia.core.entities import (
    Alternative,
    Argument,
    ArgumentStance,
    Claim,
    CognitiveDecisionRecord,
    Constraint,
    DerivationMethod,
    DissentingView,
    EpistemicType,
    Evidence,
    Goal,
    HumanActor,
    Inference,
    LifecycleStatus,
    Question,
    Recommendation,
    ReversibilityType,
    SpecialistActor,
    Unknown,
)
from aletheia.core.events.schemas import EdgeRelation


def test_complete_deliberation_and_event_replay():
    """Milestone 0: Ciclo deliberativo completo e validação do Invariante de Replay."""
    ws = CognitiveWorkspace()

    # 1. Introduz Atores
    human = HumanActor.create_default("Aelton")
    specialist = SpecialistActor(
        id="spec_arch",
        name="Cognitive Architect",
        perspective="Consistência conceitual",
    )
    ws.introduce_entity(human, actor_id=human.id)
    ws.introduce_entity(specialist, actor_id=human.id)

    # 2. Introduz Metas e Restrições
    goal = Goal(
        id="goal_1",
        statement="Construir o Kernel Cognitivo v0.1 com contratos formais",
        success_criteria=["Suíte de testes 100% verde", "Replay determinístico"],
    )
    constraint = Constraint(
        id="const_1",
        statement="Agnóstico a domínio e sem acoplamento a LLMs no core",
        inviolable=True,
    )
    ws.introduce_entity(goal, actor_id=human.id)
    ws.introduce_entity(constraint, actor_id=human.id)

    # 3. Introduz Claims, Unknown e Question
    fact = Claim(
        id="fact_python",
        author_id=specialist.id,
        statement="Python 3.11+ oferece tipagem estática e dataclasses eficientes",
        epistemic_type=EpistemicType.VERIFIED_FACT,
        lifecycle_status=LifecycleStatus.ACTIVE,
    )
    assumption_latency = Claim(
        id="assump_lat",
        author_id=specialist.id,
        statement="O grafo em memória para uma sessão não ultrapassará 1000 nós",
        epistemic_type=EpistemicType.ASSUMPTION,
        lifecycle_status=LifecycleStatus.ACTIVE,
        invalidation_conditions=["Medição de memória exceder 50MB"],
    )
    unknown = Unknown(
        id="unk_pers",
        author_id=specialist.id,
        description="Qual a frequência ideal de snapshots do log de eventos?",
    )
    question = Question(
        id="q_pers",
        author_id=specialist.id,
        question_text="Aelton, devemos persistir a cada evento ou em lote?",
        target_unknown_id="unk_pers",
        asked_by=specialist.id,
        addressed_to=human.id,
    )

    ws.introduce_entity(fact, actor_id=specialist.id)
    ws.introduce_entity(assumption_latency, actor_id=specialist.id)
    ws.introduce_entity(unknown, actor_id=specialist.id)
    ws.introduce_entity(question, actor_id=specialist.id)

    # 4. Introduz Alternativas e Argumentos
    alt1 = Alternative(
        id="alt_mem_graph",
        title="InMemoryGraphAdapter Puro Python",
        description="Dicionários de adjacência em memória sem dependências externas",
    )
    alt2 = Alternative(
        id="alt_neo4j",
        title="Neo4j Graph Database",
        description="Banco gráfico distribuído externo",
    )
    ws.introduce_entity(alt1, actor_id=specialist.id)
    ws.introduce_entity(alt2, actor_id=specialist.id)

    # Conecta alternativas às metas
    ws.connect(alt1.id, goal.id, EdgeRelation.ADDRESSES, actor_id=specialist.id)
    ws.connect(alt2.id, goal.id, EdgeRelation.ADDRESSES, actor_id=specialist.id)

    # Argumentos
    arg_alt1 = Argument(
        id="arg_1",
        alternative_id=alt1.id,
        stance=ArgumentStance.SUPPORT,
        premise_refs=[fact.id, assumption_latency.id],
        rationale="Simplicidade operacional e zero overhead de rede",
        author_id=specialist.id,
    )
    ws.introduce_entity(arg_alt1, actor_id=specialist.id)
    ws.connect(arg_alt1.id, alt1.id, EdgeRelation.SUPPORTS, actor_id=specialist.id)

    # 5. Cria Inferência e Recomendação
    infer = Inference(
        id="infer_scale",
        author_id=specialist.id,
        conclusion="O adaptador em memória atende todos os requisitos do Milestone 0",
        derivation_method=DerivationMethod.DEDUCTIVE,
        premise_ids=[fact.id, assumption_latency.id],
    )
    rec = Recommendation(
        id="rec_adopt_mem",
        author_id=specialist.id,
        proposed_alternative_id=alt1.id,
        rationale="Recomendamos InMemoryGraphAdapter",
        depends_on_assumptions=[assumption_latency.id],
        supported_by=[infer.id],
    )
    ws.introduce_entity(infer, actor_id=specialist.id)
    ws.introduce_entity(rec, actor_id=specialist.id)

    ws.connect(infer.id, assumption_latency.id, EdgeRelation.DEPENDS_ON, actor_id=specialist.id)
    ws.connect(infer.id, fact.id, EdgeRelation.DEPENDS_ON, actor_id=specialist.id)
    ws.connect(rec.id, infer.id, EdgeRelation.DEPENDS_ON, actor_id=specialist.id)
    ws.connect(assumption_latency.id, rec.id, EdgeRelation.SUPPORTS, actor_id=specialist.id)

    # 6. Registra Contradição dialética entre hipóteses arquiteturais
    hypo_a = Claim(
        id="hypo_sync",
        author_id=specialist.id,
        statement="Chamadas síncronas no barramento são desejáveis",
        epistemic_type=EpistemicType.HYPOTHESIS,
    )
    hypo_b = Claim(
        id="hypo_async",
        author_id=specialist.id,
        statement="Chamadas síncronas bloqueiam o loop de eventos",
        epistemic_type=EpistemicType.HYPOTHESIS,
    )
    ws.introduce_entity(hypo_a, actor_id=specialist.id)
    ws.introduce_entity(hypo_b, actor_id=specialist.id)
    ws.declare_contradiction(hypo_a.id, hypo_b.id, actor_id=specialist.id, rationale="Divergência síncrono vs assíncrono")

    # 7. Humano intervém: contesta uma premissa (HumanInitiative)
    ws.challenge(
        claim_id=assumption_latency.id,
        actor_id=human.id,
        rationale="Podemos rodar simulações com mais de 5000 nós no futuro",
    )

    # Verifica que a premissa entrou em UNDER_REVIEW e derivados foram suspensos
    assert ws.graph.get_node(assumption_latency.id).lifecycle_status == LifecycleStatus.UNDER_REVIEW
    assert ws.graph.get_node(infer.id).lifecycle_status == LifecycleStatus.SUSPENDED

    # 8. Ratifica CDR no Workspace
    cdr = CognitiveDecisionRecord(
        cdr_id="CDR-2026-001",
        title="Adoção de InMemoryGraphAdapter para v0.1",
        decision_owner=human.id,
        decision_scope="Core do Cognitive Workspace v0.1",
        reversibility=ReversibilityType.TYPE_2_REVERSIBLE,
        chosen_alternative_ref=alt1.id,
        underlying_assumptions=[assumption_latency.id],
        dissenting_views=[
            DissentingView(
                actor_id="spec_pragmatic",
                position=ArgumentStance.OPPOSE,
                argument_refs=[],
                rationale="Preferia SQLite desde o primeiro momento",
            )
        ],
        human_rationale="Adoção em memória permite validar os contratos com máxima velocidade e sem atrito.",
    )
    ws.ratify_decision(cdr, actor_id=human.id)

    # 9. EXECUÇÃO DO INVARIANTE DE REPLAY: Reconstrução determinística a partir do Event Store!
    all_events = ws.event_store.get_all_events()
    assert len(all_events) > 10

    reconstructed_ws = CognitiveWorkspace.replay(all_events)

    # Compara contagem de nós
    original_nodes = ws.graph.get_all_nodes()
    replayed_nodes = reconstructed_ws.graph.get_all_nodes()
    assert len(original_nodes) == len(replayed_nodes)

    # Compara integridade de cada nó (IDs e Lifecycle Statuses)
    for orig_node in original_nodes:
        replayed_node = reconstructed_ws.graph.get_node(orig_node.id)
        assert replayed_node is not None
        assert replayed_node.__class__ == orig_node.__class__
        if hasattr(orig_node, "lifecycle_status"):
            assert replayed_node.lifecycle_status == orig_node.lifecycle_status

    # Compara contagem de arestas
    original_edges = ws.graph.get_all_edges()
    replayed_edges = reconstructed_ws.graph.get_all_edges()
    assert len(original_edges) == len(replayed_edges)

    # Compara cada aresta
    orig_edge_tuples = {(e.source_id, e.target_id, e.relation) for e in original_edges}
    replayed_edge_tuples = {(e.source_id, e.target_id, e.relation) for e in replayed_edges}
    assert orig_edge_tuples == replayed_edge_tuples

    # Compara contagem de eventos
    assert reconstructed_ws.event_store.count() == ws.event_store.count()
