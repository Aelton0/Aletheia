"""Módulo de exportação de capacidades cognitivas da Aletheia."""

from aletheia.cognition.capabilities.base import (
    CapabilityAuthority,
    CapabilityContract,
    CapabilityPriority,
    CapabilityResult,
    CapabilityStateSummary,
    CapabilityTarget,
    CognitiveCapability,
    HumanActionRequest,
    HumanActionType,
    ProposedRelation,
)
from aletheia.cognition.capabilities.critique import CritiqueCapability
from aletheia.cognition.capabilities.question import QuestionGenerationCapability
from aletheia.cognition.capabilities.registry import CapabilityRegistry
from aletheia.cognition.capabilities.viability import ViabilityReviewCapability

__all__ = [
    "CapabilityAuthority",
    "CapabilityContract",
    "CapabilityPriority",
    "CapabilityResult",
    "CapabilityStateSummary",
    "CapabilityTarget",
    "CognitiveCapability",
    "HumanActionRequest",
    "HumanActionType",
    "ProposedRelation",
    "CapabilityRegistry",
    "CritiqueCapability",
    "ViabilityReviewCapability",
    "QuestionGenerationCapability",
]
