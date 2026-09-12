"""Motor Epistemológico V1: Rastreamento de dependências e suspensão em cascata."""

from typing import List, Optional, Set
from aletheia.core.entities.epistemic import Claim, Inference, LifecycleStatus
from aletheia.core.entities.deliberation import Recommendation
from aletheia.core.events.schemas import EdgeRelation
from aletheia.ports.graph_port import GraphStoragePort


def invalidate_claim(
    graph: GraphStoragePort,
    claim_id: str,
    evidence_id: Optional[str] = None,
) -> List[str]:
    """Invalida uma premissa e propaga suspensão determinística em cascata.
    
    Retorna a lista de IDs de nós dependentes que foram suspensos.
    """
    target = graph.get_node(claim_id)
    if not target:
        raise KeyError(f"Nó '{claim_id}' não encontrado no grafo.")

    if hasattr(target, "lifecycle_status"):
        target.lifecycle_status = LifecycleStatus.INVALIDATED
        graph.update_node(target)

    suspended_nodes: List[str] = []
    visited: Set[str] = {claim_id}

    def _cascade(current_id: str) -> None:
        # 1. Dependentes diretos que declaram DEPENDS_ON ou DERIVED_FROM (Source -> Target=current_id)
        incoming_deps = graph.get_incoming_edges(current_id, EdgeRelation.DEPENDS_ON)
        incoming_derived = graph.get_incoming_edges(current_id, EdgeRelation.DERIVED_FROM)

        direct_dependents = [e.source_id for e in incoming_deps + incoming_derived]

        # 2. Recomendações que eram sustentadas por este nó (current_id -> Target)
        outgoing_supports = graph.get_outgoing_edges(current_id, EdgeRelation.SUPPORTS)
        for e in outgoing_supports:
            target_node = graph.get_node(e.target_id)
            if isinstance(target_node, Recommendation):
                direct_dependents.append(e.target_id)

        for dep_id in direct_dependents:
            if dep_id in visited:
                continue
            visited.add(dep_id)

            dep_node = graph.get_node(dep_id)
            if dep_node and hasattr(dep_node, "lifecycle_status"):
                dep_node.lifecycle_status = LifecycleStatus.SUSPENDED
                graph.update_node(dep_node)
                suspended_nodes.append(dep_id)
                _cascade(dep_id)

    _cascade(claim_id)
    return suspended_nodes


def challenge_claim(
    graph: GraphStoragePort,
    claim_id: str,
    actor_id: str,
    rationale: str,
) -> List[str]:
    """Processa a contestação de uma premissa pelo humano (HumanInitiative).
    
    Marca a premissa como UNDER_REVIEW e suspende temporariamente os derivados diretos.
    """
    target = graph.get_node(claim_id)
    if not target:
        raise KeyError(f"Nó '{claim_id}' não encontrado no grafo.")

    if hasattr(target, "lifecycle_status"):
        target.lifecycle_status = LifecycleStatus.UNDER_REVIEW
        graph.update_node(target)

    affected_nodes: List[str] = []

    # Localiza dependentes diretos
    incoming_deps = graph.get_incoming_edges(claim_id, EdgeRelation.DEPENDS_ON)
    incoming_derived = graph.get_incoming_edges(claim_id, EdgeRelation.DERIVED_FROM)

    for edge in incoming_deps + incoming_derived:
        dep_node = graph.get_node(edge.source_id)
        if dep_node and hasattr(dep_node, "lifecycle_status"):
            dep_node.lifecycle_status = LifecycleStatus.SUSPENDED
            graph.update_node(dep_node)
            affected_nodes.append(edge.source_id)

    return affected_nodes
