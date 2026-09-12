"""LLM Critique Capability: Capacidade cognitiva de crítica impulsionada por LLM.

Passa obrigatoriamente pela validação estrutural e epistêmica (Fronteira de Segurança Cognitiva).
"""

from typing import List, Optional
from aletheia.cognition.adapters.llm.epistemic_validator import (
    EpistemicValidator,
    ValidationStatus,
)
from aletheia.cognition.adapters.llm.schemas import LLMCritiquePayload
from aletheia.cognition.adapters.llm.serializer import ProjectionPromptSerializer
from aletheia.cognition.adapters.llm.structural_validator import StructuralValidator
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
    Argument,
    Capability,
    SpecialistActor,
    Unknown,
    generate_id,
)
from aletheia.core.events.schemas import EdgeRelation
from aletheia.ports.llm_port import LLMProviderPort


class LLMCritiqueCapability(CognitiveCapability):
    """Capacidade de crítica que utiliza um LLM para gerar argumentos e incertezas fundamentados."""

    def __init__(self, llm_provider: LLMProviderPort) -> None:
        self.llm_provider = llm_provider

    @property
    def contract(self) -> CapabilityContract:
        return CapabilityContract(
            identity="LLMCritiqueCapability",
            capability_type=Capability.CRITIQUE,
            perspective="Análise probabilística de riscos e vulnerabilidades estruturais via LLM",
            authority=CapabilityAuthority.ADVISORY,
            side_effects=False,
            input_types=["Alternative", "Claim"],
            output_types=["Argument", "Unknown"],
            trigger_condition="Alternativa ativa com suposições não verificadas sob análise crítica probabilística",
        )

    def can_handle(self, summary: CapabilityStateSummary) -> List[CapabilityTarget]:
        targets: List[CapabilityTarget] = []
        for alt_id in summary.active_alternatives_without_critique:
            targets.append(
                CapabilityTarget(
                    capability_name=self.contract.identity,
                    target_id=alt_id,
                    reason="Alternativa carece de avaliação crítica fundamentada por LLM",
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
        # 1. Serialização limpa da projeção autorizada (Invariante 7: nada de nós ocultos)
        prompt = ProjectionPromptSerializer.serialize_for_critique(projection, target_id)

        # 2. Invocação do modelo probabilístico através da porta
        llm_resp = self.llm_provider.generate_structured(
            prompt=prompt,
            response_schema=LLMCritiquePayload,
            system_instruction="Você é uma capacidade cognitiva especializada em ceticismo metodológico.",
            temperature=0.0,
        )
        raw_payload: LLMCritiquePayload = llm_resp.parsed_output

        # 3. CAMADA 1: Validação Estrutural (purga de IDs alucinados e conformidade de tipos)
        struct_res = StructuralValidator.validate(raw_payload, projection)
        if not struct_res.is_valid and not struct_res.purged_payload:
            return CapabilityResult(
                capability_name=self.contract.identity,
                specialist=specialist,
                target_ref=target_id,
                rationale=f"Rejeitado na Validação Estrutural: {struct_res.structural_errors}",
            )

        valid_payload = struct_res.purged_payload or raw_payload

        # 4. CAMADA 2: Validação Epistemológica (grounding, anti-injeção e suporte calibrado)
        epistemic_res = EpistemicValidator.validate(valid_payload, projection)
        if epistemic_res.status == ValidationStatus.REJECTED:
            return CapabilityResult(
                capability_name=self.contract.identity,
                specialist=specialist,
                target_ref=target_id,
                rationale=f"Rejeitado na Validação Epistêmica: {epistemic_res.audit_notes}",
            )

        # 5. Conversão em entidades tipadas da ontologia do Kernel
        produced_entities = []
        proposed_relations = []

        # Converte argumentos validados
        for arg_prop in valid_payload.arguments:
            arg_entity = Argument(
                id=generate_id("arg_llm_critique"),
                alternative_id=target_id,
                stance=arg_prop.stance,
                premise_refs=arg_prop.premise_refs,
                rationale=arg_prop.rationale,
                author_id=specialist.id,
                weight=1.2,
                metadata={
                    "model": llm_resp.model,
                    "model_confidence": valid_payload.model_confidence,
                    "epistemic_support": epistemic_res.epistemic_support.value,
                    "critical_depth_assessed": epistemic_res.critical_depth_assessed,
                    "rhr_score": struct_res.rhr_score,
                },
            )
            produced_entities.append(arg_entity)
            proposed_relations.append(
                ProposedRelation(
                    source_id=arg_entity.id,
                    target_id=target_id,
                    relation=EdgeRelation.OPPOSES if arg_prop.stance.value == "OPPOSE" else EdgeRelation.SUPPORTS,
                    metadata={"rationale": "Argumento gerado por LLMCritiqueCapability"},
                )
            )

        # Converte incertezas validadas
        for unk_prop in valid_payload.unknowns:
            unk_entity = Unknown(
                id=generate_id("unk_llm"),
                author_id=specialist.id,
                description=unk_prop.description,
                blocking=unk_prop.blocking,
                resolution_criteria=unk_prop.resolution_criteria,
            )
            produced_entities.append(unk_entity)
            if valid_payload.arguments and valid_payload.arguments[0].premise_refs:
                focal_premise = valid_payload.arguments[0].premise_refs[0]
                proposed_relations.append(
                    ProposedRelation(
                        source_id=unk_entity.id,
                        target_id=focal_premise,
                        relation=EdgeRelation.DEPENDS_ON,
                        metadata={"origin": "Incerteza derivada de crítica probabilística"},
                    )
                )

        # 6. Solicitação de Ação Humana Tipada
        action_req = HumanActionRequest(
            action_type=HumanActionType.REVIEW_CLAIM,
            target_ref=target_id,
            reason=f"Revisar os argumentos críticos emitidos com suporte epistêmico '{epistemic_res.epistemic_support.value}'.",
            required=False,
        )

        rationale = (
            f"Crítica formulada por {llm_resp.model} com suporte epistêmico "
            f"'{epistemic_res.epistemic_support.value}' (profundidade crítica {epistemic_res.critical_depth_assessed}/5). "
            f"Resumo: {valid_payload.reasoning_summary}"
        )

        return CapabilityResult(
            capability_name=self.contract.identity,
            specialist=specialist,
            target_ref=target_id,
            produced_entities=produced_entities,
            proposed_relations=proposed_relations,
            human_action_request=action_req,
            rationale=rationale,
        )
