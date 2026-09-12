"""Capacidade de Crítica: Avalia alternativas e aponta vulnerabilidades em premissas."""

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
    Argument,
    ArgumentStance,
    Capability,
    Claim,
    EpistemicType,
    LifecycleStatus,
    SpecialistActor,
    Unknown,
    generate_id,
)
from aletheia.core.events.schemas import EdgeRelation


class CritiqueCapability(CognitiveCapability):
    """Analisa alternativas e gera argumentos contrários com base em suposições não testadas."""

    @property
    def contract(self) -> CapabilityContract:
        return CapabilityContract(
            identity="CritiqueCapability",
            capability_type=Capability.CRITIQUE,
            perspective="Ceticismo metódico e identificação de pontos de falha em premissas",
            authority=CapabilityAuthority.ADVISORY,
            side_effects=False,
            input_types=["Alternative", "Claim"],
            output_types=["Argument", "Unknown"],
            trigger_condition="Alternativa ativa com suposições não verificadas e sem argumentos de oposição",
        )

    def can_handle(self, summary: CapabilityStateSummary) -> List[CapabilityTarget]:
        targets: List[CapabilityTarget] = []
        for alt_id in summary.active_alternatives_without_critique:
            targets.append(
                CapabilityTarget(
                    capability_name=self.contract.identity,
                    target_id=alt_id,
                    reason="Alternativa depende de premissas não verificadas e carece de escrutínio crítico",
                    priority=CapabilityPriority.HIGH,
                )
            )
        return targets

    def run(
        self,
        projection: CognitiveProjection,
        target_id: str,
        specialist: SpecialistActor,
    ) -> CapabilityResult:
        # 1. Localiza a alternativa na projeção
        target_alt = next((n for n in projection.salient_nodes if n.id == target_id and isinstance(n, Alternative)), None)
        if not target_alt:
            return CapabilityResult(
                capability_name=self.contract.identity,
                specialist=specialist,
                target_ref=target_id,
                rationale=f"Alternativa alvo '{target_id}' não encontrada na projeção.",
            )

        # 2. Localiza suposições ativas associadas
        assumptions = [
            n for n in projection.salient_nodes
            if isinstance(n, Claim)
            and n.epistemic_type == EpistemicType.ASSUMPTION
            and n.lifecycle_status == LifecycleStatus.ACTIVE
        ]

        if not assumptions:
            return CapabilityResult(
                capability_name=self.contract.identity,
                specialist=specialist,
                target_ref=target_id,
                rationale="Nenhuma suposição não verificada encontrada para criticar.",
            )

        focal_assumption = assumptions[0]

        # 3. Gera Argumento contrário (OPPOSE)
        arg = Argument(
            id=generate_id("arg_critique"),
            alternative_id=target_id,
            stance=ArgumentStance.OPPOSE,
            premise_refs=[focal_assumption.id],
            rationale=(
                f"A alternativa '{target_alt.title}' assume que '{focal_assumption.statement}', "
                "o que carece de evidência empírica formal e constitui vulnerabilidade operacional."
            ),
            author_id=specialist.id,
            weight=1.5,
        )

        # 4. Gera Unknown explícito formalizando a incerteza
        unk = Unknown(
            id=generate_id("unk_risk"),
            author_id=specialist.id,
            description=f"Qual é o plano de contingência se a suposição '{focal_assumption.statement}' for refutada?",
            blocking=False,
        )

        # 5. Relações propostas
        relations = [
            ProposedRelation(
                source_id=arg.id,
                target_id=target_id,
                relation=EdgeRelation.OPPOSES,
                metadata={"reason": "Crítica estrutural de dependência vulnerável"},
            ),
            ProposedRelation(
                source_id=unk.id,
                target_id=focal_assumption.id,
                relation=EdgeRelation.DEPENDS_ON,
                metadata={"reason": "Incerteza gerada pela premissa sob escrutínio"},
            ),
        ]

        # 6. Solicitação de julgamento humano tipada
        action_req = HumanActionRequest(
            action_type=HumanActionType.REVIEW_CLAIM,
            target_ref=focal_assumption.id,
            reason=f"Validar ou contestar a suposição '{focal_assumption.statement}' antes de avançar.",
            required=False,
        )

        return CapabilityResult(
            capability_name=self.contract.identity,
            specialist=specialist,
            target_ref=target_id,
            produced_entities=[arg, unk],
            proposed_relations=relations,
            human_action_request=action_req,
            rationale=f"Emitida objeção fundamentada na suposição vulnerável '{focal_assumption.id}'.",
        )
