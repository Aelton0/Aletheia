"""Motor de Síntese e Raciocínio Estrutural sobre o Grafo Epistêmico.

Opera sem LLMs nesta fase, inspecionando dependências, premissas de sustentação,
contradições dialéticas e viabilidade de alternativas para gerar interpretações cognitivas.
"""

from typing import Any, Dict, List, Tuple
from aletheia.core.context.projection import CognitiveProjection
from aletheia.core.entities import (
    Alternative,
    Claim,
    EpistemicType,
    Goal,
    LifecycleStatus,
)
from aletheia.core.events.schemas import EdgeRelation
from aletheia.ports.graph_port import GraphStoragePort


class CognitiveSynthesizer:
    """Sintetiza diagnósticos e interpretações determinísticas a partir do estado do grafo."""

    @staticmethod
    def inspect_dependencies(
        graph: GraphStoragePort, alt_id: str
    ) -> Dict[str, Any]:
        """Inspeciona as premissas das quais uma alternativa depende."""
        alt = graph.get_node(alt_id)
        if not alt:
            raise KeyError(f"Alternativa '{alt_id}' não encontrada no grafo.")

        # Busca arestas de dependência e suporte
        dep_edges = graph.get_outgoing_edges(alt_id, EdgeRelation.DEPENDS_ON)
        support_edges = graph.get_incoming_edges(alt_id, EdgeRelation.SUPPORTS)

        direct_claim_ids = [e.target_id for e in dep_edges] + [e.source_id for e in support_edges]

        active_assumptions: List[Claim] = []
        under_review_claims: List[Claim] = []
        invalidated_claims: List[Claim] = []
        verified_facts: List[Claim] = []

        for cid in set(direct_claim_ids):
            node = graph.get_node(cid)
            if isinstance(node, Claim):
                if node.lifecycle_status == LifecycleStatus.INVALIDATED:
                    invalidated_claims.append(node)
                elif node.lifecycle_status == LifecycleStatus.UNDER_REVIEW:
                    under_review_claims.append(node)
                elif node.lifecycle_status == LifecycleStatus.SUSPENDED:
                    under_review_claims.append(node)
                elif node.epistemic_type == EpistemicType.VERIFIED_FACT:
                    verified_facts.append(node)
                elif node.epistemic_type == EpistemicType.ASSUMPTION:
                    active_assumptions.append(node)

        return {
            "alternative_id": alt_id,
            "active_assumptions": active_assumptions,
            "under_review_claims": under_review_claims,
            "invalidated_claims": invalidated_claims,
            "verified_facts": verified_facts,
        }

    @staticmethod
    def evaluate_viability(
        graph: GraphStoragePort, alt_id: str
    ) -> Tuple[bool, List[str]]:
        """Avalia se a alternativa é viável à luz do estado atual de suas premissas."""
        info = CognitiveSynthesizer.inspect_dependencies(graph, alt_id)
        reasons: List[str] = []

        if info["invalidated_claims"]:
            reasons.append(
                f"Possui {len(info['invalidated_claims'])} premissa(s) INVALIDADA(S): "
                + ", ".join(c.statement for c in info["invalidated_claims"])
            )
        if info["under_review_claims"]:
            reasons.append(
                f"Possui {len(info['under_review_claims'])} premissa(s) SOB REVISÃO/SUSPENSAS: "
                + ", ".join(c.statement for c in info["under_review_claims"])
            )

        is_viable = len(reasons) == 0
        return is_viable, reasons

    @staticmethod
    def generate_interpretation(
        graph: GraphStoragePort, projection: CognitiveProjection
    ) -> str:
        """Gera uma interpretação cognitiva clara em linguagem natural a partir da projeção."""
        lines: List[str] = []

        if projection.active_focus:
            lines.append(f"📌 **Foco Ativo de Deliberação**: '{projection.active_focus}'")

        # Metas na projeção
        goals = [n for n in projection.salient_nodes if isinstance(n, Goal)]
        if goals:
            lines.append(f"🎯 **Metas Salientes**: {', '.join(g.statement for g in goals)}")

        # Alternativas salientes e suas dependências críticas
        for alt in projection.active_alternatives:
            lines.append(f"\n💡 **Alternativa Sob Análise**: '{alt.title}' ({alt.id})")
            info = CognitiveSynthesizer.inspect_dependencies(graph, alt.id)

            if info["invalidated_claims"]:
                for inv in info["invalidated_claims"]:
                    lines.append(f"   ⚠️ **BLOQUEIO**: Depende da premissa INVALIDADA: '{inv.statement}'")

            if info["under_review_claims"]:
                for ur in info["under_review_claims"]:
                    lines.append(f"   ⏳ **ATENÇÃO**: Depende de nó SOB REVISÃO/SUSPENSO: '{ur.statement}'")

            if info["active_assumptions"]:
                for asm in info["active_assumptions"]:
                    lines.append(f"   🔍 **Premissa Subjacente**: Essa escolha parece depender da premissa '{asm.statement}'. Quer examiná-la?")

            if not info["active_assumptions"] and not info["invalidated_claims"] and not info["under_review_claims"]:
                lines.append("   ✅ Nenhuma dependência vulnerável detectada nesta projeção.")

        # Conflitos dialéticos
        if projection.active_conflicts:
            lines.append("\n⚔️ **Conflitos Epistêmicos Detectados**:")
            for conf in projection.active_conflicts:
                lines.append(f"   - Conflito pendente: '{conf.statement}' ({conf.id})")

        # Perguntas abertas
        if projection.open_questions:
            lines.append("\n❓ **Perguntas em Aberto**:")
            for q in projection.open_questions:
                lines.append(f"   - {q.question_text} (endereçada a: {q.addressed_to})")

        return "\n".join(lines)
