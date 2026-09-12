"""Módulo de cognição epistemológica (TMS e gestão de contradições)."""

from aletheia.cognition.epistemic.conflicts import register_contradiction
from aletheia.cognition.epistemic.tms import challenge_claim, invalidate_claim

__all__ = [
    "register_contradiction",
    "invalidate_claim",
    "challenge_claim",
]
