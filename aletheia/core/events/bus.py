"""Barramento de eventos síncrono para o Kernel Cognitivo."""

from collections import defaultdict
from typing import Callable, Dict, List
from aletheia.core.events.schemas import CognitiveEvent


EventHandler = Callable[[CognitiveEvent], None]


class EventBus:
    """Barramento de publicação e assinatura de eventos cognitivos."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._global_subscribers: List[EventHandler] = []

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Inscreve um handler em um tipo específico de evento."""
        self._subscribers[event_type].append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        """Inscreve um handler em todos os eventos do sistema."""
        self._global_subscribers.append(handler)

    def publish(self, event: CognitiveEvent) -> None:
        """Publica um evento para todos os ouvintes interessados."""
        for handler in self._global_subscribers:
            handler(event)
        for handler in self._subscribers.get(event.event_type, []):
            handler(event)
