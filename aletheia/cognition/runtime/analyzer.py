"""Analisador de estado do Workspace: deriva o CapabilityStateSummary deterministicamente."""

from typing import List
from aletheia.cognition.capabilities.base import CapabilityStateSummary
from aletheia.core.entities import (
    Alternative,
    Argument,
    ArgumentStance,
    Claim,
    EpistemicType,
    LifecycleStatus,
    Question,
    Unknown,
)
from aletheia.core.events.schemas import EdgeRelation
from aletheia.ports.graph_port import GraphStoragePort


class WorkspaceStateAnalyzer:
    """Extrai o resumo estrutural de estado do grafo para consumo exclusivo pelo Seletor."""

    @staticmethod
    def analyze(graph: GraphStoragePort) -> CapabilityStateSummary:
        """Produz uma síntese determinística das demandas cognitivas pendentes."""
        all_nodes = graph.get_all_nodes()

        alternatives_without_critique: List[str] = []
        unresolved_blocking_unknowns: List[str] = []
        alternatives_with_suspended_dependencies: List[str] = []

        # 1. Analisa Alternativas
        for node in all_nodes:
            if isinstance(node, Alternative):
                dep_edges = graph.get_outgoing_edges(node.id, EdgeRelation.DEPENDS_ON)
                support_edges = graph.get_incoming_edges(node.id, EdgeRelation.SUPPORTS)
                oppose_edges = graph.get_incoming_edges(node.id, EdgeRelation.OPPOSES)

                direct_claim_ids = [e.target_id for e in dep_edges] + [e.source_id for e in support_edges]
                claims = [graph.get_node(cid) for cid in direct_claim_ids if graph.has_node(cid)]

                # Premissas que são suposições não verificadas ativas
                has_active_assumptions = any(
                    isinstance(c, Claim)
                    and c.epistemic_type == EpistemicType.ASSUMPTION
                    and c.lifecycle_status == LifecycleStatus.ACTIVE
                    for c in claims
                )

                # Verifica se já possui argumento de oposição (OPPOSE)
                has_oppose_argument = False
                for edge in oppose_edges:
                    opp_node = graph.get_node(edge.source_id)
                    if isinstance(opp_node, Argument) and opp_node.stance == ArgumentStance.OPPOSE:
                        has_oppose_argument = True
                        break

                if has_active_assumptions and not has_oppose_argument:
                    alternatives_without_critique.append(node.id)

                # Verifica se tem dependências comprometidas (UNDER_REVIEW ou SUSPENDED)
                has_suspended_dep = any(
                    isinstance(c, Claim)
                    and c.lifecycle_status in [LifecycleStatus.UNDER_REVIEW, LifecycleStatus.SUSPENDED, LifecycleStatus.INVALIDATED]
                    for c in claims
                )

                # Verifica se já possui aviso de inviabilidade emitido (idempotência)
                already_has_viability_claim = False
                for edge in oppose_edges:
                    opp_node = graph.get_node(edge.source_id)
                    if isinstance(opp_node, Claim) and hasattr(opp_node, "statement"):
                        stmt = opp_node.statement.lower()
                        if "viabilidade" in stmt:
                            already_has_viability_claim = True
                            break

                if has_suspended_dep and not already_has_viability_claim:
                    alternatives_with_suspended_dependencies.append(node.id)

        # 2. Analisa Unknowns bloqueantes sem Question associada
        questions = [n for n in all_nodes if isinstance(n, Question)]
        questioned_unknown_ids = {q.target_unknown_id for q in questions if q.target_unknown_id}

        for node in all_nodes:
            if isinstance(node, Unknown) and node.blocking:
                if node.id not in questioned_unknown_ids:
                    unresolved_blocking_unknowns.append(node.id)

        return CapabilityStateSummary(
            active_alternatives_without_critique=alternatives_without_critique,
            unresolved_blocking_unknowns=unresolved_blocking_unknowns,
            alternatives_with_suspended_dependencies=alternatives_with_suspended_dependencies,
        )
