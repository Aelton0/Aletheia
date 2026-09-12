"""Módulo de exportação de primitivos ontológicos da Aletheia."""

from aletheia.core.entities.base import CognitiveEntity, generate_id
from aletheia.core.entities.actors import (
    Actor,
    ActorRole,
    Capability,
    HumanActor,
    SpecialistActor,
)
from aletheia.core.entities.epistemic import (
    Claim,
    DerivationMethod,
    EpistemicObject,
    EpistemicType,
    Evidence,
    Inference,
    LifecycleStatus,
    Question,
    QuestionStatus,
    Unknown,
)
from aletheia.core.entities.deliberation import (
    Alternative,
    AlternativeStatus,
    Argument,
    ArgumentStance,
    Constraint,
    Goal,
    Recommendation,
)
from aletheia.core.entities.decision import (
    CognitiveDecisionRecord,
    DecisionStatus,
    DissentingView,
    ReversibilityType,
)
from aletheia.core.entities.experience import (
    Action,
    DeltaType,
    EpistemicDelta,
    Lesson,
    Outcome,
)

__all__ = [
    "CognitiveEntity",
    "generate_id",
    "Actor",
    "ActorRole",
    "Capability",
    "HumanActor",
    "SpecialistActor",
    "EpistemicObject",
    "EpistemicType",
    "LifecycleStatus",
    "DerivationMethod",
    "Claim",
    "Evidence",
    "Inference",
    "Unknown",
    "Question",
    "QuestionStatus",
    "Goal",
    "Constraint",
    "Alternative",
    "AlternativeStatus",
    "Argument",
    "ArgumentStance",
    "Recommendation",
    "CognitiveDecisionRecord",
    "DecisionStatus",
    "ReversibilityType",
    "DissentingView",
    "Action",
    "Outcome",
    "EpistemicDelta",
    "DeltaType",
    "Lesson",
]
