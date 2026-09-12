"""Capacidade de Avaliação de Viabilidade: Audita alternativas com dependências comprometidas."""

from typing import List
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
from aletheia.core.context.projection import CognitiveProjection
from aletheia.core.entities import (
    Alternative,
    Capability,
    Claim,
    EpistemicType,
    LifecycleStatus,
    SpecialistActor,
    generate_id,
)
from aletheia.core.events.schemas import EdgeRelation


class ViabilityReviewCapability(CognitiveCapability):
    """Detecta alternativas com dependências sob revisão ou suspensas e emite Claims de inviabilidade."""

    @property
    def contract(self) -> CapabilityContract:
        return CapabilityContract(
            identity="ViabilityReviewCapability",
            capability_type=Capability.REASONING,
            perspective="Auditoria de viabilidade e consistência de alternativas operacionais",
            authority=CapabilityAuthority.ADVISORY,
            side_effects=False,
            input_types=["Alternative", "Claim"],
            output_types=["Claim"],
            trigger_condition="Alternativa cujas premissas de apoio foram marcadas como UNDER_REVIEW ou SUSPENDED",
        )

    def can_handle(self, summary: CapabilityStateSummary) -> List[CapabilityTarget]:
        targets: List[CapabilityTarget] = []
        for alt_id in summary.alternatives_with_suspended_dependencies:
            targets.append(
                CapabilityTarget(
                    capability_name=self.contract.identity,
                    target_id=alt_id,
                    reason="Alternativa depende de premissas comprometidas e precisa de avaliação de viabilidade",
                    priority=CapabilityPriority.CRITICAL,
                )
            )
        return targets

    def run(
        self,
        projection: CognitiveProjection,
        target_id: str,
        specialist: SpecialistActor,
    ) -> CapabilityResult:
        target_alt = next((n for n in projection.salient_nodes if n.id == target_id and isinstance(n, Alternative)), None)
        if not target_alt:
            return CapabilityResult(
                capability_name=self.contract.identity,
                specialist=specialist,
                target_ref=target_id,
                rationale=f"Alternativa '{target_id}' não encontrada na projeção.",
            )

        # Identifica premissas com status comprometido
        compromised_claims = [
            n for n in projection.salient_nodes
            if isinstance(n, Claim)
            and n.lifecycle_status in [LifecycleStatus.UNDER_REVIEW, LifecycleStatus.SUSPENDED, LifecycleStatus.INVALIDATED]
        ]

        if not compromised_claims:
            return CapabilityResult(
                capability_name=self.contract.identity,
                specialist=specialist,
                target_ref=target_id,
                rationale="Nenhuma premissa comprometida encontrada nesta projeção.",
            )

        focal_dep = compromised_claims[0]

        # Emite uma Claim formal de inviabilidade (sem inventar entidades fora da ontologia)
        viability_claim = Claim(
            id=generate_id("claim_viability"),
            author_id=specialist.id,
            statement=(
                f"A alternativa '{target_alt.title}' atualmente carece de viabilidade operacional "
                f"pois depende da premissa '{focal_dep.statement}', cujo status é '{focal_dep.lifecycle_status.value}'."
            ),
            epistemic_type=EpistemicType.HYPOTHESIS,
            lifecycle_status=LifecycleStatus.ACTIVE,
            rationale="Constatação estrutural emitida pela auditoria de viabilidade",
        )

        relation = ProposedRelation(
            source_id=viability_claim.id,
            target_id=target_id,
            relation=EdgeRelation.OPPOSES,
            metadata={"finding": "Inviabilidade estrutural por premissa comprometida"},
        )

        action_req = HumanActionRequest(
            action_type=HumanActionType.RESOLVE_CONFLICT,
            target_ref=target_id,
            reason=f"A alternativa '{target_alt.title}' depende de premissa suspensa/sob revisão e requer resolução deliberativa.",
            required=True,
        )

        return CapabilityResult(
            capability_name=self.contract.identity,
            specialist=specialist,
            target_ref=target_id,
            produced_entities=[viability_claim],
            proposed_relations=[relation],
            human_action_request=action_req,
            rationale=f"Emitida Claim de inviabilidade contra a alternativa '{target_id}'.",
        )
