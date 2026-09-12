"""Testes do Motor Epistemológico V1: Invalidação e suspensão em cascata."""

from aletheia.adapters.in_memory_graph import InMemoryGraphAdapter
from aletheia.cognition.epistemic.tms import challenge_claim, invalidate_claim
from aletheia.core.entities import (
    Claim,
    DerivationMethod,
    EpistemicType,
    Evidence,
    Inference,
    LifecycleStatus,
    Recommendation,
)
from aletheia.core.events.schemas import EdgeRelation
from aletheia.ports.graph_port import Edge


def test_cascade_invalidation_suspends_downstream():
    """Invariante: Invalidação de premissa propaga SUSPENDED determinístico para dependentes."""
    graph = InMemoryGraphAdapter()

    # 1. Cria Fato e Suposição
    fact = Claim(
        id="fact_1",
        author_id="actor_1",
        statement="O banco SQLite suporta transações ACID locais",
        epistemic_type=EpistemicType.VERIFIED_FACT,
        lifecycle_status=LifecycleStatus.ACTIVE,
    )
    assumption = Claim(
        id="assump_1",
        author_id="actor_1",
        statement="A taxa de escrita será sempre inferior a 10 req/s",
        epistemic_type=EpistemicType.ASSUMPTION,
        lifecycle_status=LifecycleStatus.ACTIVE,
        invalidation_conditions=["Medição de escrita ultrapassar 10 req/s"],
    )

    # 2. Cria Inferência que depende de ambos
    inference = Inference(
        id="infer_1",
        author_id="spec_1",
        conclusion="SQLite em disco é suficiente para a escala inicial",
        derivation_method=DerivationMethod.DEDUCTIVE,
        premise_ids=["fact_1", "assump_1"],
        lifecycle_status=LifecycleStatus.ACTIVE,
    )

    # 3. Cria Recomendação sustentada pela inferência
    recommendation = Recommendation(
        id="rec_1",
        author_id="spec_1",
        proposed_alternative_id="alt_sqlite",
        rationale="Adotar SQLite puro",
        depends_on_assumptions=["assump_1"],
        supported_by=["infer_1"],
        lifecycle_status=LifecycleStatus.ACTIVE,
    )

    # Insere nós no grafo
    for node in [fact, assumption, inference, recommendation]:
        graph.add_node(node)

    # Conecta as arestas de dependência
    graph.add_edge(Edge(source_id="infer_1", target_id="assump_1", relation=EdgeRelation.DEPENDS_ON))
    graph.add_edge(Edge(source_id="infer_1", target_id="fact_1", relation=EdgeRelation.DEPENDS_ON))
    graph.add_edge(Edge(source_id="rec_1", target_id="infer_1", relation=EdgeRelation.DEPENDS_ON))
    graph.add_edge(Edge(source_id="assump_1", target_id="rec_1", relation=EdgeRelation.SUPPORTS))

    # Invalida a suposição através de evidência empírica
    affected = invalidate_claim(graph, claim_id="assump_1")

    # Verifica os estados resultantes
    assert graph.get_node("assump_1").lifecycle_status == LifecycleStatus.INVALIDATED
    assert graph.get_node("infer_1").lifecycle_status == LifecycleStatus.SUSPENDED
    assert graph.get_node("rec_1").lifecycle_status == LifecycleStatus.SUSPENDED
    assert "infer_1" in affected
    assert "rec_1" in affected


def test_human_challenge_marks_under_review_and_suspends_dependents():
    """Invariante: Contestação humana coloca premissa em UNDER_REVIEW e suspende dependentes."""
    graph = InMemoryGraphAdapter()

    assumption = Claim(
        id="assump_speed",
        author_id="spec_1",
        statement="Rede interna possui latência desprezível",
        epistemic_type=EpistemicType.ASSUMPTION,
        lifecycle_status=LifecycleStatus.ACTIVE,
    )
    inference = Inference(
        id="infer_sync",
        author_id="spec_1",
        conclusion="Podemos usar chamadas síncronas bloqueantes",
        derivation_method=DerivationMethod.DEDUCTIVE,
        premise_ids=["assump_speed"],
        lifecycle_status=LifecycleStatus.ACTIVE,
    )

    graph.add_node(assumption)
    graph.add_node(inference)
    graph.add_edge(Edge(source_id="infer_sync", target_id="assump_speed", relation=EdgeRelation.DEPENDS_ON))

    # Humano contesta a premissa
    affected = challenge_claim(
        graph,
        claim_id="assump_speed",
        actor_id="human_1",
        rationale="Ambientes em nuvem sofrem jitter frequente de rede",
    )

    assert graph.get_node("assump_speed").lifecycle_status == LifecycleStatus.UNDER_REVIEW
    assert graph.get_node("infer_sync").lifecycle_status == LifecycleStatus.SUSPENDED
    assert "infer_sync" in affected
