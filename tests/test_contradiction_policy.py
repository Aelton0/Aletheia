"""Testes da política de contradição dialética no Grafo Epistêmico."""

from aletheia.adapters.in_memory_graph import InMemoryGraphAdapter
from aletheia.cognition.epistemic.conflicts import register_contradiction
from aletheia.core.entities import Claim, EpistemicType, LifecycleStatus
from aletheia.core.events.schemas import EdgeRelation


def test_contradiction_does_not_auto_invalidate():
    """Invariante: contradicts não invalida nós arbitrariamente, mas estabelece CONFLICT."""
    graph = InMemoryGraphAdapter()

    claim_a = Claim(
        id="claim_sync",
        author_id="spec_arch",
        statement="A arquitetura deve ser orientada a chamadas RPC síncronas",
        epistemic_type=EpistemicType.HYPOTHESIS,
        lifecycle_status=LifecycleStatus.ACTIVE,
    )
    claim_b = Claim(
        id="claim_async",
        author_id="spec_pragmatic",
        statement="A arquitetura deve ser orientada a eventos assíncronos desacoplados",
        epistemic_type=EpistemicType.HYPOTHESIS,
        lifecycle_status=LifecycleStatus.ACTIVE,
    )

    graph.add_node(claim_a)
    graph.add_node(claim_b)

    # Registra a contradição mútua
    register_contradiction(
        graph,
        claim_a_id="claim_sync",
        claim_b_id="claim_async",
        rationale="Modelos de comunicação síncrono e assíncrono são mutuamente exclusivos no core",
    )

    # Invariante: Nenhum nó foi INVALIDATED
    node_a = graph.get_node("claim_sync")
    node_b = graph.get_node("claim_async")

    assert node_a.lifecycle_status == LifecycleStatus.CONFLICT
    assert node_b.lifecycle_status == LifecycleStatus.CONFLICT
    assert node_a.lifecycle_status != LifecycleStatus.INVALIDATED
    assert node_b.lifecycle_status != LifecycleStatus.INVALIDATED

    # Invariante: Aresta bidirecional CONTRADICTS
    edges_from_a = graph.get_outgoing_edges("claim_sync", EdgeRelation.CONTRADICTS)
    edges_from_b = graph.get_outgoing_edges("claim_async", EdgeRelation.CONTRADICTS)

    assert len(edges_from_a) == 1
    assert edges_from_a[0].target_id == "claim_async"
    assert len(edges_from_b) == 1
    assert edges_from_b[0].target_id == "claim_sync"
