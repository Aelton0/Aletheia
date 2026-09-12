"""Sessão Interativa de Cognição Colaborativa (M1).

Conecta o Humano, o Cognitive Workspace, o Motor de Projeção e o Raciocínio Estrutural.
Garante a Invariante de Iniciativa Mista sem reinício de sessão.
"""

from typing import Any, Dict, List, Optional
from aletheia.cognition.reasoning.synthesizer import CognitiveSynthesizer
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

        self.current_focus: Optional[str] = None

    def define_problem(
        self,
        statement: str,
        goals: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
    ) -> List[str]:
        """Passo 1 & 2: Humano expressa a intenção e Aletheia registra no contexto."""
        created_ids: List[str] = []

        # Meta principal
        main_goal = Goal(
            id=generate_id("goal"),
            statement=statement,
            success_criteria=goals or [],
            priority=1,
            is_active=True,
        )
        self.workspace.introduce_entity(main_goal, actor_id=self.human.id)
        created_ids.append(main_goal.id)

        # Restrições
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

        # Conecta às metas
        for gid in addresses_goal_ids or []:
            if self.workspace.graph.has_node(gid):
                self.workspace.connect(alt.id, gid, EdgeRelation.ADDRESSES, actor_id=actor)

        # Conecta às premissas das quais depende
        for cid in depends_on_claim_ids or []:
            if self.workspace.graph.has_node(cid):
                self.workspace.connect(alt.id, cid, EdgeRelation.DEPENDS_ON, actor_id=actor)

        return alt

    def challenge_premise(self, claim_id: str, rationale: str) -> List[str]:
        """Passo 4 & 5: Humano contesta uma premissa; Kernel suspende derivados."""
        return self.workspace.challenge(
            claim_id=claim_id,
            actor_id=self.human.id,
            rationale=rationale,
        )

    def change_direction(self, focus: str) -> CognitiveProjection:
        """Passo 6: Humano muda o foco cognitivo ('HumanDirectionChanged')."""
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
        """Passo 3: Aletheia apresenta sua interpretação estrutural do estado atual."""
        projection = self.get_projection()
        return CognitiveSynthesizer.generate_interpretation(
            graph=self.workspace.graph,
            projection=projection,
        )

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
        """Passo 9: Criação e ratificação do CDR contextual preservando dissidência."""
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
