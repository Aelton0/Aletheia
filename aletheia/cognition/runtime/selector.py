"""Seletor de Capacidades: Identifica e prioriza quais capacidades devem agir."""

from typing import List
from aletheia.cognition.capabilities.base import (
    CapabilityPriority,
    CapabilityStateSummary,
    CapabilityTarget,
)
from aletheia.cognition.capabilities.registry import CapabilityRegistry


PRIORITY_ORDER = {
    CapabilityPriority.CRITICAL: 0,
    CapabilityPriority.HIGH: 1,
    CapabilityPriority.NORMAL: 2,
    CapabilityPriority.LOW: 3,
}


class CapabilitySelector:
    """Seleciona alvos cognitivos aplicáveis a partir unicamente do CapabilityStateSummary."""

    @staticmethod
    def select(
        summary: CapabilityStateSummary, registry: CapabilityRegistry
    ) -> List[CapabilityTarget]:
        """Consulta as capacidades registradas e retorna alvos ordenados por prioridade."""
        all_targets: List[CapabilityTarget] = []

        for cap in registry.get_all():
            targets = cap.can_handle(summary)
            all_targets.extend(targets)

        # Ordena alvos por prioridade
        all_targets.sort(key=lambda t: PRIORITY_ORDER.get(t.priority, 99))
        return all_targets
