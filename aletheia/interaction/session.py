"""Sessão Interativa de Cognição Colaborativa (M1 & M2).

Conecta o Humano, o Cognitive Workspace, o Motor de Projeção e o Capability Runtime.
Garante a Invariante de Iniciativa Mista e execução controlada de capacidades.
"""

from typing import Any, Dict, List, Optional
from aletheia.cognition.capabilities import (
    CapabilityResult,
    CapabilityRegistry,
    CritiqueCapability,
    QuestionGenerationCapability,
    ViabilityReviewCapability,
)
from aletheia.cognition.reasoning.synthesizer import CognitiveSynthesizer
from aletheia.cognition.runtime import CapabilityRuntime
from aletheia.core.context.projection import CognitiveProjection, ProjectionEngine
from aletheia.core.context.workspace import CognitiveWorkspace
from aletheia.core.entities import (
    Alternative,
    Argument,
    ArgumentStance,
    Claim,
    CognitiveDecisionRecord,
    Constraint,
    DissentingView,
    EpistemicType,
    Evidence,
    Goal,
    HumanActor,
    LifecycleStatus,
    Question,
    ReversibilityType,
    SpecialistActor,
    Unknown,
    generate_id,
)
from aletheia.core.events.schemas import CognitiveEvent, EdgeRelation


class InteractiveSession:
    """Orquestrador da sessão colaborativa contínua Humano-Aletheia."""

    def __init__(
        self,
        human_name: str = "Aelton",
        workspace: Optional[CognitiveWorkspace] = None,
        runtime: Optional[CapabilityRuntime] = None,
    ) -> None:
        self.workspace = workspace or CognitiveWorkspace()
        self.human = HumanActor.create_default(human_name)
        self.system_actor = SpecialistActor(
            id=generate_id("aletheia"),
            name="Aletheia Cognitive Assistant",
            perspective="Consistência epistêmica e facilitação deliberativa",
        )
        self.workspace.introduce_entity(self.human, actor_id=self.human.id)
        self.workspace.introduce_entity(self.system_actor, actor_id=self.system_actor.id)

        # Inicializa o Capability Runtime com as capacidades padrão do M2
        self.runtime = runtime or CapabilityRuntime()
        if not self.runtime.registry.get_all():
            self.runtime.registry.register(CritiqueCapability())
            self.runtime.registry.register(ViabilityReviewCapability())
            self.runtime.registry.register(QuestionGenerationCapability())

        self.current_focus: Optional[str] = None

    def define_problem(
        self,
        statement: str,
        goals: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
    ) -> List[str]:
        """Passo 1 & 2: Humano expressa a intenção e Aletheia registra no contexto."""
        created_ids: List[str] = []

        main_goal = Goal(
            id=generate_id("goal"),
            statement=statement,
            success_criteria=goals or [],
            priority=1,
            is_active=True,
        )
        self.workspace.introduce_entity(main_goal, actor_id=self.human.id)
        created_ids.append(main_goal.id)

        for c_stmt in constraints or []:
            const = Constraint(
                id=generate_id("const"),
                statement=c_stmt,
                inviolable=True,
            )
            self.workspace.introduce_entity(const, actor_id=self.human.id)
            created_ids.append(const.id)

        return created_ids

    def introduce_claim(
        self,
        statement: str,
        epistemic_type: EpistemicType = EpistemicType.ASSUMPTION,
        author_id: Optional[str] = None,
        rationale: Optional[str] = None,
        invalidation_conditions: Optional[List[str]] = None,
    ) -> Claim:
        """Introduz uma proposição (hipótese, suposição ou fato) no workspace."""
        actor = author_id or self.human.id
        claim = Claim(
            id=generate_id("claim"),
            author_id=actor,
            statement=statement,
            epistemic_type=epistemic_type,
            lifecycle_status=LifecycleStatus.ACTIVE,
            rationale=rationale,
            invalidation_conditions=invalidation_conditions or [],
        )
        self.workspace.introduce_entity(claim, actor_id=actor)
        return claim

    def introduce_unknown(
        self,
        description: str,
        blocking: bool = False,
        author_id: Optional[str] = None,
    ) -> Unknown:
        """Introduz uma incerteza explícita (Unknown) no workspace."""
        actor = author_id or self.human.id
        unknown = Unknown(
            id=generate_id("unk"),
            author_id=actor,
            description=description,
            blocking=blocking,
        )
        self.workspace.introduce_entity(unknown, actor_id=actor)
        return unknown

    def propose_alternative(
        self,
        title: str,
        description: str,
        addresses_goal_ids: Optional[List[str]] = None,
        depends_on_claim_ids: Optional[List[str]] = None,
        author_id: Optional[str] = None,
    ) -> Alternative:
        """Introduz uma alternativa e a ancora às metas e premissas declaradas."""
        actor = author_id or self.human.id
        alt = Alternative(
            id=generate_id("alt"),
            title=title,
            description=description,
            goal_refs=addresses_goal_ids or [],
        )
        self.workspace.introduce_entity(alt, actor_id=actor)

        for gid in addresses_goal_ids or []:
            if self.workspace.graph.has_node(gid):
                self.workspace.connect(alt.id, gid, EdgeRelation.ADDRESSES, actor_id=actor)

        for cid in depends_on_claim_ids or []:
            if self.workspace.graph.has_node(cid):
                self.workspace.connect(alt.id, cid, EdgeRelation.DEPENDS_ON, actor_id=actor)

        return alt

    def challenge_premise(self, claim_id: str, rationale: str) -> List[str]:
        """Humano contesta uma premissa; Kernel suspende derivados."""
        return self.workspace.challenge(
            claim_id=claim_id,
            actor_id=self.human.id,
            rationale=rationale,
        )

    def change_direction(self, focus: str) -> CognitiveProjection:
        """Humano muda o foco cognitivo ('HumanDirectionChanged')."""
        prev_focus = self.current_focus
        self.current_focus = focus.strip()

        event = CognitiveEvent(
            actor_id=self.human.id,
            event_type="HumanDirectionChanged",
            payload={
                "previous_focus": prev_focus,
                "new_focus": self.current_focus,
            },
        )
        self.workspace.event_store.append(event)
        self.workspace.bus.publish(event)

        return self.get_projection()

    def get_projection(self) -> CognitiveProjection:
        """Gera a projeção mínima e suficiente baseada no foco ativo atual."""
        return ProjectionEngine.project(
            graph=self.workspace.graph,
            focus=self.current_focus,
        )

    def get_interpretation(self) -> str:
        """Aletheia apresenta sua interpretação estrutural do estado atual."""
        projection = self.get_projection()
        return CognitiveSynthesizer.generate_interpretation(
            graph=self.workspace.graph,
            projection=projection,
        )

    def step_capabilities(
        self, capability_name: Optional[str] = None, target_id: Optional[str] = None
    ) -> Optional[CapabilityResult]:
        """Executa um step único de capacidade cognitiva pelo Runtime."""
        return self.runtime.step(self.workspace, capability_name, target_id)

    def run_capability_policy(self, safety_limit: int = 5) -> List[CapabilityResult]:
        """Executa steps sucessivos até estabilização ou atingir o limite de segurança."""
        return self.runtime.run_policy(self.workspace, safety_limit=safety_limit)

    def deliberate_and_decide(
        self,
        title: str,
        chosen_alt_id: str,
        scope: str,
        underlying_assumptions: Optional[List[str]] = None,
        human_rationale: Optional[str] = None,
        dissenting_views: Optional[List[DissentingView]] = None,
        reversibility: ReversibilityType = ReversibilityType.TYPE_2_REVERSIBLE,
    ) -> CognitiveDecisionRecord:
        """Criação e ratificação do CDR contextual preservando dissidência."""
        cdr = CognitiveDecisionRecord(
            cdr_id=generate_id("cdr"),
            title=title,
            decision_owner=self.human.id,
            decision_scope=scope,
            chosen_alternative_ref=chosen_alt_id,
            underlying_assumptions=underlying_assumptions or [],
            human_rationale=human_rationale,
            dissenting_views=dissenting_views or [],
            reversibility=reversibility,
        )
        self.workspace.ratify_decision(cdr, actor_id=self.human.id)
        return cdr

    def get_cognitive_summary(self) -> Dict[str, Any]:
        """Sumariza as métricas cognitivas do estado global do workspace."""
        all_nodes = self.workspace.graph.get_all_nodes()
        all_edges = self.workspace.graph.get_all_edges()

        claims = [n for n in all_nodes if isinstance(n, Claim)]
        alternatives = [n for n in all_nodes if isinstance(n, Alternative)]
        cdrs = [n for n in all_nodes if isinstance(n, CognitiveDecisionRecord)]

        return {
            "total_nodes": len(all_nodes),
            "total_edges": len(all_edges),
            "total_events": self.workspace.event_store.count(),
            "active_focus": self.current_focus,
            "claims_count": len(claims),
            "alternatives_count": len(alternatives),
            "cdrs_count": len(cdrs),
            "under_review_claims": [c.id for c in claims if c.lifecycle_status == LifecycleStatus.UNDER_REVIEW],
            "suspended_claims": [c.id for c in claims if c.lifecycle_status == LifecycleStatus.SUSPENDED],
        }
