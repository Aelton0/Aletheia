"""Adaptador append-only em memória para o Event Store."""

from typing import List
from aletheia.core.events.schemas import CognitiveEvent
from aletheia.ports.event_store_port import EventStorePort


class InMemoryEventStore(EventStorePort):
    """Implementação append-only simples e segura de EventStorePort."""

    def __init__(self) -> None:
        self._events: List[CognitiveEvent] = []

    def append(self, event: CognitiveEvent) -> None:
        self._events.append(event)

    def get_all_events(self) -> List[CognitiveEvent]:
        return list(self._events)

    def count(self) -> int:
        return len(self._events)
