"""Cognitive Workspace: O espaço compartilhado e persistente da cognição colaborativa."""

from typing import Any, Dict, List, Optional, Type
from aletheia.adapters.in_memory_event_store import InMemoryEventStore
from aletheia.adapters.in_memory_graph import InMemoryGraphAdapter
from aletheia.cognition.deliberation.cdr import validate_cdr_integrity
from aletheia.cognition.epistemic.conflicts import register_contradiction
from aletheia.cognition.epistemic.tms import challenge_claim, invalidate_claim
from aletheia.core.entities import (
    Action,
    Alternative,
    Argument,
    Claim,
    CognitiveDecisionRecord,
    CognitiveEntity,
    Constraint,
    EpistemicDelta,
    Evidence,
    Goal,
    HumanActor,
    Inference,
    Lesson,
    Outcome,
    Question,
    Recommendation,
    SpecialistActor,
    Unknown,
)
from aletheia.core.events.bus import EventBus
from aletheia.core.events.schemas import (
    CognitiveEvent,
    EdgeRelation,
)
from aletheia.ports.event_store_port import EventStorePort
from aletheia.ports.graph_port import Edge, GraphStoragePort


ENTITY_CLASS_MAP: Dict[str, Type[CognitiveEntity]] = {
    "Claim": Claim,
    "Evidence": Evidence,
    "Inference": Inference,
    "Unknown": Unknown,
    "Question": Question,
    "Goal": Goal,
    "Constraint": Constraint,
    "Alternative": Alternative,
    "Argument": Argument,
    "Recommendation": Recommendation,
    "CognitiveDecisionRecord": CognitiveDecisionRecord,
    "HumanActor": HumanActor,
    "SpecialistActor": SpecialistActor,
    "Action": Action,
    "Outcome": Outcome,
    "EpistemicDelta": EpistemicDelta,
    "Lesson": Lesson,
}


class CognitiveWorkspace:
    """O Blackboard dinâmico e auditável onde ocorrem a deliberação e o raciocínio."""

    def __init__(
        self,
        graph: Optional[GraphStoragePort] = None,
        event_store: Optional[EventStorePort] = None,
        bus: Optional[EventBus] = None,
    ) -> None:
        self.graph = graph or InMemoryGraphAdapter()
        self.event_store = event_store or InMemoryEventStore()
        self.bus = bus or EventBus()

    def introduce_entity(self, entity: CognitiveEntity, actor_id: str) -> None:
        """Introduz uma nova entidade no grafo e registra o evento imutável."""
        self.graph.add_node(entity)

        event = CognitiveEvent(
            actor_id=actor_id,
            event_type="EntityIntroduced",
            payload={
                "entity_type": entity.__class__.__name__,
                "entity_data": entity.model_dump(mode="json"),
            },
        )
        self.event_store.append(event)
        self.bus.publish(event)

    def connect(
        self,
        source_id: str,
        target_id: str,
        relation: EdgeRelation,
        actor_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Conecta dois nós do grafo com uma relação semântica tipada."""
        edge = Edge(
            source_id=source_id,
            target_id=target_id,
            relation=relation,
            metadata=metadata or {},
        )
        self.graph.add_edge(edge)

        event = CognitiveEvent(
            actor_id=actor_id,
            event_type="RelationConnected",
            payload={
                "source_id": source_id,
                "target_id": target_id,
                "relation": relation.value,
                "metadata": metadata or {},
            },
        )
        self.event_store.append(event)
        self.bus.publish(event)

    def challenge(
        self, claim_id: str, actor_id: str, rationale: str
    ) -> List[str]:
        """Iniciativa Humana: contesta uma premissa, colocando-a UNDER_REVIEW e suspendendo derivados."""
        affected = challenge_claim(self.graph, claim_id, actor_id, rationale)

        event = CognitiveEvent(
            actor_id=actor_id,
            event_type="PremiseChallenged",
            payload={
                "target_claim_id": claim_id,
                "rationale": rationale,
                "suspended_dependent_ids": affected,
            },
        )
        self.event_store.append(event)
        self.bus.publish(event)
        return affected

    def invalidate(
        self, claim_id: str, actor_id: str, evidence_id: Optional[str] = None
    ) -> List[str]:
        """Falsificação empírica: invalida a premissa e suspende toda a cadeia descendente."""
        affected = invalidate_claim(self.graph, claim_id, evidence_id)

        event = CognitiveEvent(
            actor_id=actor_id,
            event_type="PremiseInvalidated",
            payload={
                "target_claim_id": claim_id,
                "evidence_id": evidence_id,
                "suspended_dependent_ids": affected,
            },
        )
        self.event_store.append(event)
        self.bus.publish(event)
        return affected

    def declare_contradiction(
        self,
        claim_a_id: str,
        claim_b_id: str,
        actor_id: str,
        rationale: Optional[str] = None,
    ) -> None:
        """Registra inconsistência mútua entre proposições sem auto-invalidação arbitrária."""
        register_contradiction(self.graph, claim_a_id, claim_b_id, rationale)

        event = CognitiveEvent(
            actor_id=actor_id,
            event_type="ContradictionRegistered",
            payload={
                "claim_a_id": claim_a_id,
                "claim_b_id": claim_b_id,
                "rationale": rationale,
            },
        )
        self.event_store.append(event)
        self.bus.publish(event)

    def ratify_decision(
        self, cdr: CognitiveDecisionRecord, actor_id: str
    ) -> List[str]:
        """Ratifica um CDR contextual no workspace, preservando dissidência e amarrações."""
        warnings = validate_cdr_integrity(cdr, self.graph)

        self.introduce_entity(cdr, actor_id=actor_id)

        # Conecta a decisão à alternativa escolhida
        self.connect(
            source_id=cdr.id,
            target_id=cdr.chosen_alternative_ref,
            relation=EdgeRelation.SELECTS,
            actor_id=actor_id,
        )

        # Conecta a decisão substituída se houver
        if cdr.supersedes_ref:
            self.connect(
                source_id=cdr.id,
                target_id=cdr.supersedes_ref,
                relation=EdgeRelation.SUPERSEDES,
                actor_id=actor_id,
            )

        # Conecta as suposições subjacentes
        for claim_id in cdr.underlying_assumptions:
            if self.graph.has_node(claim_id):
                self.connect(
                    source_id=cdr.id,
                    target_id=claim_id,
                    relation=EdgeRelation.DEPENDS_ON,
                    actor_id=actor_id,
                )

        event = CognitiveEvent(
            actor_id=actor_id,
            event_type="DecisionRatified",
            payload={
                "cdr_id": cdr.cdr_id,
                "decision_owner": cdr.decision_owner,
                "chosen_alternative_ref": cdr.chosen_alternative_ref,
                "scope": cdr.decision_scope,
            },
        )
        self.event_store.append(event)
        self.bus.publish(event)
        return warnings

    @classmethod
    def replay(cls, events: List[CognitiveEvent]) -> "CognitiveWorkspace":
        """Invariante de Reconstrução: reconstrói todo o estado a partir do log imutável de eventos."""
        reconstructed = cls()

        for event in events:
            evt_type = event.event_type
            payload = event.payload

            if evt_type == "EntityIntroduced":
                entity_type_name = payload["entity_type"]
                entity_cls = ENTITY_CLASS_MAP.get(entity_type_name)
                if not entity_cls:
                    raise ValueError(f"Classe desconhecida no replay: {entity_type_name}")
                entity = entity_cls.model_validate(payload["entity_data"])
                reconstructed.graph.add_node(entity)

            elif evt_type == "RelationConnected":
                edge = Edge(
                    source_id=payload["source_id"],
                    target_id=payload["target_id"],
                    relation=EdgeRelation(payload["relation"]),
                    metadata=payload.get("metadata", {}),
                )
                reconstructed.graph.add_edge(edge)

            elif evt_type == "PremiseChallenged":
                challenge_claim(
                    reconstructed.graph,
                    payload["target_claim_id"],
                    event.actor_id,
                    payload["rationale"],
                )

            elif evt_type == "PremiseInvalidated":
                invalidate_claim(
                    reconstructed.graph,
                    payload["target_claim_id"],
                    payload.get("evidence_id"),
                )

            elif evt_type == "ContradictionRegistered":
                register_contradiction(
                    reconstructed.graph,
                    payload["claim_a_id"],
                    payload["claim_b_id"],
                    payload.get("rationale"),
                )

            elif evt_type == "DecisionRatified":
                pass  # A entidade CDR e suas relações já foram introduzidas pelos eventos anteriores

            # Grava no event_store reconstruído
            reconstructed.event_store.append(event)

        return reconstructed
