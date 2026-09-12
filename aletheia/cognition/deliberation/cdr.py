"""Validação de integridade e registro de Cognitive Decision Records (CDRs)."""

from typing import List
from aletheia.core.entities.decision import CognitiveDecisionRecord
from aletheia.ports.graph_port import GraphStoragePort


def validate_cdr_integrity(
    cdr: CognitiveDecisionRecord,
    graph: GraphStoragePort,
) -> List[str]:
    """Verifica a integridade referencial e os invariantes do CDR no grafo.
    
    Retorna uma lista de alertas caso existam incertezas ou dissidências registradas.
    Dispara ValueError se invariantes fundamentais forem violados.
    """
    # 1. Escopo de decisão é mandatório e contextual
    if not cdr.decision_scope or len(cdr.decision_scope.strip()) < 3:
        raise ValueError("Invariante violada: CDR deve possuir decision_scope explicitamente contextual.")

    # 2. Alternativa escolhida deve existir no workspace
    if not graph.has_node(cdr.chosen_alternative_ref):
        raise ValueError(
            f"Alternativa escolhida '{cdr.chosen_alternative_ref}' não existe no workspace."
        )

    # 3. Decisão substituída (supersedes), se indicada, deve existir
    if cdr.supersedes_ref and not graph.has_node(cdr.supersedes_ref):
        raise ValueError(
            f"Decisão anterior '{cdr.supersedes_ref}' referenciada em supersedes não existe no workspace."
        )

    warnings: List[str] = []

    # 4. Alerta sobre premissas subjacentes
    for claim_id in cdr.underlying_assumptions:
        node = graph.get_node(claim_id)
        if not node:
            warnings.append(f"Premissa referenciada '{claim_id}' não foi encontrada no grafo.")

    # 5. Preservação de dissidência
    if cdr.dissenting_views:
        warnings.append(
            f"CDR ratificado preservando {len(cdr.dissenting_views)} visão(ões) dissidente(s)."
        )

    return warnings
