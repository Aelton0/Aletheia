"""Testes unitários para o Motor de Projeção Contextual e Síntese Cognitiva."""

from aletheia.adapters.in_memory_graph import InMemoryGraphAdapter
from aletheia.cognition.reasoning.synthesizer import CognitiveSynthesizer
from aletheia.core.context.projection import ProjectionEngine
from aletheia.core.entities import (
    Alternative,
    Claim,
    Constraint,
    EpistemicType,
    Goal,
    LifecycleStatus,
)
from aletheia.core.events.schemas import EdgeRelation
from aletheia.ports.graph_port import Edge


def test_projection_engine_filters_by_focus_and_invariants():
    """Invariante 7: Projeção contextual preserva metas ativas e filtra por saliência de foco."""
    graph = InMemoryGraphAdapter()

    # Invariantes contextuais
    goal = Goal(id="goal_perf", statement="Atingir alta performance de IO", is_active=True)
    const = Constraint(id="const_budget", statement="Orçamento financeiro limitado", inviolable=True)

    # Nós específicos de domínio
    claim_security = Claim(
        id="c_sec",
        author_id="h1",
        statement="A criptografia de dados em trânsito com TLS 1.3 é mandatória",
        epistemic_type=EpistemicType.ASSUMPTION,
    )
    claim_cost = Claim(
        id="c_cost",
        author_id="h1",
        statement="O custo de servidores dedicados é excessivo",
        epistemic_type=EpistemicType.ASSUMPTION,
    )
    alt_cost = Alternative(
        id="alt_shared",
        title="Uso de infraestrutura compartilhada para reduzir custo",
        description="Ambiente multi-tenant de baixo custo",
    )

    for n in [goal, const, claim_security, claim_cost, alt_cost]:
        graph.add_node(n)

    graph.add_edge(Edge(source_id=alt_cost.id, target_id=claim_cost.id, relation=EdgeRelation.DEPENDS_ON))

    # Projeta com foco "custo"
    projection = ProjectionEngine.project(graph, focus="custo")

    salient_ids = {n.id for n in projection.salient_nodes}

    # Invariantes globais sempre presentes
    assert goal.id in salient_ids
    assert const.id in salient_ids

    # Nós relacionados a custo presentes
    assert claim_cost.id in salient_ids
    assert alt_cost.id in salient_ids

    # Nó de segurança (não relacionado) deve ser excluído da projeção saliente
    assert claim_security.id not in salient_ids


def test_synthesizer_detects_unverified_assumptions_and_blockers():
    """Sintetizador cognitivo identifica premissas vulneráveis e bloqueios de viabilidade."""
    graph = InMemoryGraphAdapter()

    alt = Alternative(id="alt_fast", title="Cache em Memória RAM", description="Velocidade máxima")
    assump = Claim(
        id="assump_ram",
        author_id="h1",
        statement="A máquina terá ao menos 64GB de memória RAM disponível",
        epistemic_type=EpistemicType.ASSUMPTION,
        lifecycle_status=LifecycleStatus.ACTIVE,
    )
    fact = Claim(
        id="fact_redis",
        author_id="h1",
        statement="Redis suporta persistência assíncrona RDB",
        epistemic_type=EpistemicType.VERIFIED_FACT,
        lifecycle_status=LifecycleStatus.ACTIVE,
    )

    graph.add_node(alt)
    graph.add_node(assump)
    graph.add_node(fact)

    graph.add_edge(Edge(source_id=alt.id, target_id=assump.id, relation=EdgeRelation.DEPENDS_ON))
    graph.add_edge(Edge(source_id=alt.id, target_id=fact.id, relation=EdgeRelation.DEPENDS_ON))

    # 1. Inspeciona dependências
    info = CognitiveSynthesizer.inspect_dependencies(graph, alt.id)
    assert len(info["active_assumptions"]) == 1
    assert info["active_assumptions"][0].id == "assump_ram"
    assert len(info["verified_facts"]) == 1

    # 2. Gera interpretação
    projection = ProjectionEngine.project(graph)
    text = CognitiveSynthesizer.generate_interpretation(graph, projection)
    assert "Essa escolha parece depender da premissa 'A máquina terá ao menos 64GB" in text

    # 3. Viabilidade inicial é verdadeira
    viable, _ = CognitiveSynthesizer.evaluate_viability(graph, alt.id)
    assert viable is True

    # 4. Invalida a suposição
    assump.lifecycle_status = LifecycleStatus.INVALIDATED
    graph.update_node(assump)

    # 5. Agora a viabilidade é falsa
    viable_after, reasons = CognitiveSynthesizer.evaluate_viability(graph, alt.id)
    assert viable_after is False
    assert any("INVALIDADA(S)" in r for r in reasons)
