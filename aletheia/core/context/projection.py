"""Motor de Projeção Contextual: Projeção mínima e suficiente baseada em foco e saliência.

Invariante 7:
O Cognitive Workspace detém o estado global do problema; qualquer mecanismo
de raciocínio recebe apenas a projeção de contexto estritamente necessária e
suficiente para sua tarefa imediata.
"""

from typing import List, Optional, Set
from pydantic import BaseModel, Field
from aletheia.core.entities import (
    Alternative,
    Claim,
    CognitiveEntity,
    Constraint,
    Goal,
    LifecycleStatus,
    Question,
    QuestionStatus,
)
from aletheia.ports.graph_port import Edge, GraphStoragePort


class CognitiveProjection(BaseModel):
    """Subgrafo projetado com nós e arestas salientes para a tarefa e foco atuais."""
    active_focus: Optional[str] = None
    salient_nodes: List[CognitiveEntity] = Field(default_factory=list)
    salient_edges: List[Edge] = Field(default_factory=list)
    unresolved_assumptions: List[Claim] = Field(default_factory=list)
    active_conflicts: List[Claim] = Field(default_factory=list)
    open_questions: List[Question] = Field(default_factory=list)
    active_alternatives: List[Alternative] = Field(default_factory=list)


class ProjectionEngine:
    """Calcula projeções contextuais a partir do Grafo Epistêmico global."""

    @staticmethod
    def project(
        graph: GraphStoragePort,
        focus: Optional[str] = None,
        focal_node_id: Optional[str] = None,
    ) -> CognitiveProjection:
        """Gera uma projeção contextual mínima e suficiente baseada no foco ativo."""
        all_nodes = graph.get_all_nodes()
        all_edges = graph.get_all_edges()

        salient_node_ids: Set[str] = set()

        # 1. Metas e Restrições ativas são sempre invariantes contextuais
        for node in all_nodes:
            if isinstance(node, Goal) and node.is_active:
                salient_node_ids.add(node.id)
            elif isinstance(node, Constraint) and node.inviolable:
                salient_node_ids.add(node.id)

        # 2. Se houver um foco textual explícito (ex: "cost", "security", "speed")
        if focus and focus.strip():
            term = focus.strip().lower()
            for node in all_nodes:
                match = False
                # Busca no statement/title/description
                if hasattr(node, "statement") and term in node.statement.lower():
                    match = True
                elif hasattr(node, "title") and term in node.title.lower():
                    match = True
                elif hasattr(node, "description") and term in node.description.lower():
                    match = True
                elif hasattr(node, "rationale") and node.rationale and term in node.rationale.lower():
                    match = True

                if match:
                    salient_node_ids.add(node.id)
                    # Adiciona nós vizinhos imediatos (1-hop)
                    for edge in graph.get_outgoing_edges(node.id):
                        salient_node_ids.add(edge.target_id)
                    for edge in graph.get_incoming_edges(node.id):
                        salient_node_ids.add(edge.source_id)

        # 3. Se houver um nó focal especificado
        if focal_node_id and graph.has_node(focal_node_id):
            salient_node_ids.add(focal_node_id)
            for edge in graph.get_outgoing_edges(focal_node_id):
                salient_node_ids.add(edge.target_id)
            for edge in graph.get_incoming_edges(focal_node_id):
                salient_node_ids.add(edge.source_id)

        # 4. Se nenhum foco foi especificado, inclui nós ativos gerais de deliberação
        if not focus and not focal_node_id:
            for node in all_nodes:
                if isinstance(node, (Alternative, Claim, Question)):
                    salient_node_ids.add(node.id)

        # 5. Constrói coleções especializadas a partir dos nós salientes
        salient_nodes: List[CognitiveEntity] = []
        unresolved_assumptions: List[Claim] = []
        active_conflicts: List[Claim] = []
        open_questions: List[Question] = []
        active_alternatives: List[Alternative] = []

        for nid in salient_node_ids:
            node = graph.get_node(nid)
            if not node:
                continue
            salient_nodes.append(node)

            if isinstance(node, Claim):
                if node.lifecycle_status == LifecycleStatus.CONFLICT:
                    active_conflicts.append(node)
                elif node.epistemic_type.value == "ASSUMPTION" and node.lifecycle_status == LifecycleStatus.ACTIVE:
                    unresolved_assumptions.append(node)
            elif isinstance(node, Question) and node.status == QuestionStatus.OPEN:
                open_questions.append(node)
            elif isinstance(node, Alternative):
                active_alternatives.append(node)

        # 6. Filtra arestas cujos dois extremos estejam no subgrafo saliente
        salient_edges: List[Edge] = [
            e for e in all_edges
            if e.source_id in salient_node_ids and e.target_id in salient_node_ids
        ]

        return CognitiveProjection(
            active_focus=focus,
            salient_nodes=salient_nodes,
            salient_edges=salient_edges,
            unresolved_assumptions=unresolved_assumptions,
            active_conflicts=active_conflicts,
            open_questions=open_questions,
            active_alternatives=active_alternatives,
        )
