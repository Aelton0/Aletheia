"""Adaptador em memória para armazenamento do Grafo Epistêmico em Python puro."""

from collections import defaultdict
from typing import Dict, List, Optional
from aletheia.core.entities.base import CognitiveEntity
from aletheia.core.events.schemas import EdgeRelation
from aletheia.ports.graph_port import Edge, GraphStoragePort


class InMemoryGraphAdapter(GraphStoragePort):
    """Implementação limpa em memória de GraphStoragePort sem dependências externas."""

    def __init__(self) -> None:
        self._nodes: Dict[str, CognitiveEntity] = {}
        self._outgoing: Dict[str, List[Edge]] = defaultdict(list)
        self._incoming: Dict[str, List[Edge]] = defaultdict(list)

    def add_node(self, entity: CognitiveEntity) -> None:
        self._nodes[entity.id] = entity

    def get_node(self, node_id: str) -> Optional[CognitiveEntity]:
        return self._nodes.get(node_id)

    def update_node(self, entity: CognitiveEntity) -> None:
        if entity.id not in self._nodes:
            raise KeyError(f"Nó com ID '{entity.id}' não encontrado para atualização.")
        self._nodes[entity.id] = entity

    def has_node(self, node_id: str) -> bool:
        return node_id in self._nodes

    def add_edge(self, edge: Edge) -> None:
        if edge.source_id not in self._nodes:
            raise KeyError(f"Nó de origem '{edge.source_id}' não existe no grafo.")
        if edge.target_id not in self._nodes:
            raise KeyError(f"Nó de destino '{edge.target_id}' não existe no grafo.")

        # Evita arestas duplicadas com a mesma relação
        for existing in self._outgoing[edge.source_id]:
            if existing.target_id == edge.target_id and existing.relation == edge.relation:
                return

        self._outgoing[edge.source_id].append(edge)
        self._incoming[edge.target_id].append(edge)

    def get_outgoing_edges(
        self, source_id: str, relation: Optional[EdgeRelation] = None
    ) -> List[Edge]:
        edges = self._outgoing.get(source_id, [])
        if relation is None:
            return list(edges)
        return [e for e in edges if e.relation == relation]

    def get_incoming_edges(
        self, target_id: str, relation: Optional[EdgeRelation] = None
    ) -> List[Edge]:
        edges = self._incoming.get(target_id, [])
        if relation is None:
            return list(edges)
        return [e for e in edges if e.relation == relation]

    def get_all_nodes(self) -> List[CognitiveEntity]:
        return list(self._nodes.values())

    def get_all_edges(self) -> List[Edge]:
        all_edges = []
        for edges in self._outgoing.values():
            all_edges.extend(edges)
        return all_edges
