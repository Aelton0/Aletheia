"""Capacidade de Geração de Perguntas: Transforma Unknowns em pedidos formais de clarificação."""

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
    Capability,
    Question,
    QuestionStatus,
    SpecialistActor,
    Unknown,
    generate_id,
)
from aletheia.core.events.schemas import EdgeRelation


class QuestionGenerationCapability(CognitiveCapability):
    """Converte lacunas e incertezas explícitas (Unknowns) em perguntas estruturadas ao humano."""

    @property
    def contract(self) -> CapabilityContract:
        return CapabilityContract(
            identity="QuestionGenerationCapability",
            capability_type=Capability.EXPLANATION,
            perspective="Elucidação metódica de lacunas de conhecimento mediante diálogo direcionado",
            authority=CapabilityAuthority.ADVISORY,
            side_effects=False,
            input_types=["Unknown"],
            output_types=["Question"],
            trigger_condition="Unknown bloqueante ativo sem pergunta de clarificação associada",
        )

    def can_handle(self, summary: CapabilityStateSummary) -> List[CapabilityTarget]:
        targets: List[CapabilityTarget] = []
        for unk_id in summary.unresolved_blocking_unknowns:
            targets.append(
                CapabilityTarget(
                    capability_name=self.contract.identity,
                    target_id=unk_id,
                    reason="Incerteza bloqueante que carece de pergunta direcionada para elucidação",
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
        target_unk = next((n for n in projection.salient_nodes if n.id == target_id and isinstance(n, Unknown)), None)
        if not target_unk:
            return CapabilityResult(
                capability_name=self.contract.identity,
                specialist=specialist,
                target_ref=target_id,
                rationale=f"Unknown '{target_id}' não encontrado na projeção.",
            )

        # Formula a pergunta direcionada
        q = Question(
            id=generate_id("q_clarify"),
            author_id=specialist.id,
            question_text=f"A respeito da incerteza '{target_unk.description}', qual critério ou evidência você adotaria para elucidá-la?",
            target_unknown_id=target_unk.id,
            asked_by=specialist.id,
            addressed_to="Human",
            status=QuestionStatus.OPEN,
        )

        relation = ProposedRelation(
            source_id=q.id,
            target_id=target_unk.id,
            relation=EdgeRelation.ADDRESSES,
            metadata={"purpose": "Esclarecimento de incerteza bloqueante"},
        )

        action_req = HumanActionRequest(
            action_type=HumanActionType.ANSWER_QUESTION,
            target_ref=q.id,
            reason=f"Fornecer resposta ou orientação para a dúvida '{target_unk.description}'.",
            required=True,
        )

        return CapabilityResult(
            capability_name=self.contract.identity,
            specialist=specialist,
            target_ref=target_id,
            produced_entities=[q],
            proposed_relations=[relation],
            human_action_request=action_req,
            rationale=f"Formulada Question '{q.id}' endereçada ao humano para elucidar '{target_unk.id}'.",
        )
