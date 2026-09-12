"""Política de gestão de contradições dialéticas no Grafo Epistêmico.

Invariante fundamental:
contradicts não invalida automaticamente nenhum dos dois Claims; cria um estado
de conflito (CONFLICT) que exige resolução por evidência empírica, decisão humana
ou sustentação consciente da inconsistência.
"""

from typing import Optional
from aletheia.core.entities.epistemic import Claim, LifecycleStatus
from aletheia.core.events.schemas import EdgeRelation
from aletheia.ports.graph_port import Edge, GraphStoragePort


def register_contradiction(
    graph: GraphStoragePort,
    claim_a_id: str,
    claim_b_id: str,
    rationale: Optional[str] = None,
) -> None:
    """Registra uma relação de contradição mútua sem auto-invalidação arbitrária."""
    node_a = graph.get_node(claim_a_id)
    node_b = graph.get_node(claim_b_id)

    if not node_a:
        raise KeyError(f"Claim A com ID '{claim_a_id}' não existe no workspace.")
    if not node_b:
        raise KeyError(f"Claim B com ID '{claim_b_id}' não existe no workspace.")

    # Atualiza o status de ambos para CONFLICT se forem Claims
    if isinstance(node_a, Claim):
        node_a.lifecycle_status = LifecycleStatus.CONFLICT
        graph.update_node(node_a)

    if isinstance(node_b, Claim):
        node_b.lifecycle_status = LifecycleStatus.CONFLICT
        graph.update_node(node_b)

    # Registra aresta bidirecional de contradição
    edge_ab = Edge(
        source_id=claim_a_id,
        target_id=claim_b_id,
        relation=EdgeRelation.CONTRADICTS,
        metadata={"rationale": rationale} if rationale else {},
    )
    edge_ba = Edge(
        source_id=claim_b_id,
        target_id=claim_a_id,
        relation=EdgeRelation.CONTRADICTS,
        metadata={"rationale": rationale} if rationale else {},
    )

    graph.add_edge(edge_ab)
    graph.add_edge(edge_ba)
