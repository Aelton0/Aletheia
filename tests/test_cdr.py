"""Testes de integridade e governança de Cognitive Decision Records (CDRs)."""

import pytest
from aletheia.adapters.in_memory_graph import InMemoryGraphAdapter
from aletheia.cognition.deliberation.cdr import validate_cdr_integrity
from aletheia.core.entities import (
    Alternative,
    ArgumentStance,
    CognitiveDecisionRecord,
    DecisionStatus,
    DissentingView,
    ReversibilityType,
)


def test_cdr_validation_success_and_dissent_preservation():
    """Invariante: CDR válido preserva visões dissidentes e valida referências."""
    graph = InMemoryGraphAdapter()

    alt = Alternative(
        id="alt_event_sourcing",
        title="Event Sourcing com Grafo em Memória",
        description="Persistir eventos imutáveis e reconstruir o grafo",
    )
    graph.add_node(alt)

    cdr = CognitiveDecisionRecord(
        cdr_id="CDR-2026-001",
        title="Adoção de Event Sourcing",
        decision_owner="human_aelton",
        decision_scope="Core do Cognitive Workspace v0.1",
        reversibility=ReversibilityType.TYPE_2_REVERSIBLE,
        chosen_alternative_ref="alt_event_sourcing",
        dissenting_views=[
            DissentingView(
                actor_id="critic_simplicity",
                position=ArgumentStance.OPPOSE,
                argument_refs=["arg_simple_state"],
                rationale="Event sourcing aumenta ligeiramente a complexidade inicial de replay",
            )
        ],
    )

    warnings = validate_cdr_integrity(cdr, graph)
    assert any("preservando 1 visão(ões) dissidente(s)" in w for w in warnings)


def test_cdr_fails_on_missing_alternative():
    """Invariante: CDR não pode escolher alternativa inexistente no workspace."""
    graph = InMemoryGraphAdapter()

    cdr = CognitiveDecisionRecord(
        cdr_id="CDR-02",
        title="Decisão Órfã",
        decision_owner="human_1",
        decision_scope="Escopo válido",
        chosen_alternative_ref="alt_inexistente",
    )

    with pytest.raises(ValueError, match="não existe no workspace"):
        validate_cdr_integrity(cdr, graph)


def test_cdr_fails_on_missing_superseded_decision():
    """Invariante: Se CDR declara substituir uma decisão anterior, ela deve existir."""
    graph = InMemoryGraphAdapter()

    alt = Alternative(id="alt_1", title="Alt 1", description="Desc")
    graph.add_node(alt)

    cdr = CognitiveDecisionRecord(
        cdr_id="CDR-03",
        title="Decisão Substituta",
        decision_owner="human_1",
        decision_scope="Escopo válido",
        chosen_alternative_ref="alt_1",
        supersedes_ref="CDR-INEXISTENTE",
    )

    with pytest.raises(ValueError, match="referenciada em supersedes não existe"):
        validate_cdr_integrity(cdr, graph)
