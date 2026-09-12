"""Capability Runtime: Motor de execução e orquestração de capacidades cognitivas.

Garante o ciclo formal:
Workspace -> State Analyzer -> Selector -> Projection Engine -> Capability -> Kernel Validation -> Workspace Update
"""

from typing import Any, Dict, List, Optional
from aletheia.cognition.capabilities.base import (
    CapabilityResult,
    CapabilityTarget,
    CognitiveCapability,
)
from aletheia.cognition.capabilities.registry import CapabilityRegistry
from aletheia.cognition.runtime.analyzer import WorkspaceStateAnalyzer
from aletheia.cognition.runtime.selector import CapabilitySelector
from aletheia.core.context.projection import ProjectionEngine
from aletheia.core.context.workspace import CognitiveWorkspace
from aletheia.core.entities import Capability, SpecialistActor, generate_id
from aletheia.core.events.schemas import CognitiveEvent


class CapabilityRuntime:
    """Orquestrador do ciclo cognitivo de execução de capacidades sobre o Workspace."""

    def __init__(
        self,
        registry: Optional[CapabilityRegistry] = None,
        specialists: Optional[Dict[str, SpecialistActor]] = None,
    ) -> None:
        self.registry = registry or CapabilityRegistry()
        self._specialists = specialists or {}

    def register_specialist(self, capability_name: str, specialist: SpecialistActor) -> None:
        """Associa formalmente um SpecialistActor a uma capacidade para garantir autoria."""
        self._specialists[capability_name] = specialist

    def get_or_create_specialist(self, capability_name: str) -> SpecialistActor:
        """Recupera ou instancia o especialista responsável pela capacidade."""
        if capability_name in self._specialists:
            return self._specialists[capability_name]

        cap = self.registry.get(capability_name)
        perspective = cap.contract.perspective if cap else "Perspectiva analítica especializada"
        cap_type = cap.contract.capability_type if cap else Capability.REASONING

        specialist = SpecialistActor(
            id=generate_id(f"spec_{capability_name.lower()}"),
            name=f"{capability_name} Specialist",
            perspective=perspective,
            capabilities=[cap_type],
        )
        self._specialists[capability_name] = specialist
        return specialist

    def step(
        self,
        workspace: CognitiveWorkspace,
        capability_name: Optional[str] = None,
        target_id: Optional[str] = None,
    ) -> Optional[CapabilityResult]:
        """Executa exatamente UMA capacidade cognitiva sobre uma projeção autorizada.
        
        Retorna o CapabilityResult se executado, ou None se o sistema estiver quiescente.
        """
        # 1. State Analyzer deriva o CapabilityStateSummary (sem expor o grafo para as capabilities)
        summary = WorkspaceStateAnalyzer.analyze(workspace.graph)

        # 2. Selector identifica o alvo aplicável
        if capability_name and target_id:
            chosen_target = CapabilityTarget(
                capability_name=capability_name,
                target_id=target_id,
                reason="Execução manual explícita de step",
            )
        else:
            targets = CapabilitySelector.select(summary, self.registry)
            if not targets:
                return None  # Estado de equilíbrio (quiescente)
            chosen_target = targets[0]

        # 3. Recupera a capacidade
        capability = self.registry.get(chosen_target.capability_name)
        if not capability:
            raise KeyError(f"Capacidade '{chosen_target.capability_name}' não registrada.")

        # 4. Projeção Contextual mínima em torno do alvo (Invariante 7: a capacidade NUNCA vê o Workspace global)
        projection = ProjectionEngine.project(
            graph=workspace.graph,
            focal_node_id=chosen_target.target_id,
        )

        # 5. Obtém o especialista titular para proveniência
        specialist = self.get_or_create_specialist(chosen_target.capability_name)
        if not workspace.graph.has_node(specialist.id):
            workspace.introduce_entity(specialist, actor_id=specialist.id)

        # 6. Execução cognitiva pura: recebe projeção, emite CapabilityResult
        result = capability.run(
            projection=projection,
            target_id=chosen_target.target_id,
            specialist=specialist,
        )

        # 7. Kernel Validation & Workspace Mutation
        # A capacidade não muta o estado; o Kernel valida e aplica
        for entity in result.produced_entities:
            if not workspace.graph.has_node(entity.id):
                workspace.introduce_entity(entity, actor_id=specialist.id)

        for rel in result.proposed_relations:
            if workspace.graph.has_node(rel.source_id) and workspace.graph.has_node(rel.target_id):
                # Evita arestas duplicadas (idempotência)
                existing_edges = workspace.graph.get_outgoing_edges(rel.source_id, rel.relation)
                if not any(e.target_id == rel.target_id for e in existing_edges):
                    workspace.connect(
                        source_id=rel.source_id,
                        target_id=rel.target_id,
                        relation=rel.relation,
                        actor_id=specialist.id,
                        metadata=rel.metadata,
                    )

        # 8. Registra o evento de ciclo cognitivo
        event = CognitiveEvent(
            actor_id=specialist.id,
            event_type="CapabilityExecuted",
            payload={
                "capability": chosen_target.capability_name,
                "target_id": chosen_target.target_id,
                "produced_entities": [e.id for e in result.produced_entities],
                "proposed_relations": len(result.proposed_relations),
                "rationale": result.rationale,
            },
        )
        workspace.event_store.append(event)
        workspace.bus.publish(event)

        return result

    def run_policy(
        self,
        workspace: CognitiveWorkspace,
        safety_limit: int = 5,
    ) -> List[CapabilityResult]:
        """Executa steps sucessivos até que o estado se estabilize ou o safety_limit seja atingido."""
        executed_results: List[CapabilityResult] = []
        steps = 0

        while steps < safety_limit:
            result = self.step(workspace)
            if not result:
                break
            executed_results.append(result)
            steps += 1

        return executed_results
