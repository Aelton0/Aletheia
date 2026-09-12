"""Porta abstrata para o Event Store (Log Imutável de Eventos Cognitivos)."""

from abc import ABC, abstractmethod
from typing import List, Optional
from aletheia.core.events.schemas import CognitiveEvent


class EventStorePort(ABC):
    """Contrato formal para persistência append-only de eventos cognitivos."""

    @abstractmethod
    def append(self, event: CognitiveEvent) -> None:
        """Adiciona um novo evento imutável ao log."""
        pass

    @abstractmethod
    def get_all_events(self) -> List[CognitiveEvent]:
        """Retorna a sequência ordenada de todos os eventos registrados."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Retorna o número total de eventos armazenados."""
        pass
