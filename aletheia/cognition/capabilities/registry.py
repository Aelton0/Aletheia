"""Registro de capacidades cognitivas da Aletheia."""

from typing import Dict, List, Optional
from aletheia.cognition.capabilities.base import CognitiveCapability


class CapabilityRegistry:
    """Repositório desacoplado para descoberta e registro de capacidades."""

    def __init__(self) -> None:
        self._capabilities: Dict[str, CognitiveCapability] = {}

    def register(self, capability: CognitiveCapability) -> None:
        """Registra uma capacidade pelo seu identificador formal de contrato."""
        identity = capability.contract.identity
        self._capabilities[identity] = capability

    def get(self, name: str) -> Optional[CognitiveCapability]:
        """Recupera uma capacidade pelo nome."""
        return self._capabilities.get(name)

    def get_all(self) -> List[CognitiveCapability]:
        """Retorna todas as capacidades registradas."""
        return list(self._capabilities.values())
