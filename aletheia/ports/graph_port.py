"""Porta abstrata para armazenamento e consulta do Grafo Epistêmico."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from aletheia.core.entities.base import CognitiveEntity
from aletheia.core.events.schemas import EdgeRelation


class Edge(BaseModel):
    """Aresta direcionada e tipada no Grafo Epistêmico."""
    source_id: str
    target_id: str
    relation: EdgeRelation
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphStoragePort(ABC):
    """Contrato abstrato de armazenamento do Grafo Epistêmico (Hexagonal Port)."""

    @abstractmethod
    def add_node(self, entity: CognitiveEntity) -> None:
        """Adiciona um nó ao grafo."""
        pass

    @abstractmethod
    def get_node(self, node_id: str) -> Optional[CognitiveEntity]:
        """Recupera um nó pelo identificador."""
        pass

    @abstractmethod
    def update_node(self, entity: CognitiveEntity) -> None:
        """Atualiza os dados de um nó existente."""
        pass

    @abstractmethod
    def has_node(self, node_id: str) -> bool:
        """Verifica se um nó existe no grafo."""
        pass

    @abstractmethod
    def add_edge(self, edge: Edge) -> None:
        """Adiciona uma aresta direcionada entre dois nós."""
        pass

    @abstractmethod
    def get_outgoing_edges(
        self, source_id: str, relation: Optional[EdgeRelation] = None
    ) -> List[Edge]:
        """Retorna arestas que partem do nó fornecido."""
        pass

    @abstractmethod
    def get_incoming_edges(
        self, target_id: str, relation: Optional[EdgeRelation] = None
    ) -> List[Edge]:
        """Retorna arestas que chegam ao nó fornecido."""
        pass

    @abstractmethod
    def get_all_nodes(self) -> List[CognitiveEntity]:
        """Retorna todos os nós cadastrados."""
        pass

    @abstractmethod
    def get_all_edges(self) -> List[Edge]:
        """Retorna todas as arestas cadastradas."""
        pass
