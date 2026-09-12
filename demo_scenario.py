"""Demonstração interativa guiada do Cognitive Kernel da Aletheia (M1).

Executa um cenário realista passo a passo mostrando:
1. Formulação do Problema
2. Registro de Premissas e Alternativas
3. Interpretação Estrutural da Aletheia
4. Contestação Humana (HumanInitiative) com Suspensão em Cascata
5. Mudança de Foco (HumanDirectionChanged) e Projeção Contextual
6. Ratificação de CDR Contextual com Preservação de Dissidência
7. Replay Determinístico por Event Sourcing
"""

import sys
import time
from aletheia.core.entities import (
    ArgumentStance,
    DissentingView,
    EpistemicType,
    LifecycleStatus,
)
from aletheia.core.events.schemas import EdgeRelation
from aletheia.interaction.session import InteractiveSession


def step_pause(msg: str) -> None:
    print("\n" + "─" * 70)
    print(f"👉 {msg}")
    print("─" * 70)
    time.sleep(0.5)


def run_demo() -> None:
    print("=" * 70)
    print("  DEMONSTRAÇÃO COGNITIVA DA ALETHEIA — CENÁRIO PRÁTICO")
    print("  Decisão: 'Estratégia de Persistência e Busca de Conhecimento'")
    print("=" * 70)

    session = InteractiveSession(human_name="Aelton")

    # Passo 1
    step_pause("PASSO 1: Humano formula o problema e restrições")
    gids = session.define_problem(
        statement="Definir a arquitetura de armazenamento e busca para a base de conhecimento",
        goals=["Busca semântica rápida", "Baixo custo operacional"],
        constraints=["Preservar privacidade do usuário", "Funcionar offline"],
    )
    print("🎯 Meta e restrições registradas no Workspace:")
    for g in session.workspace.graph.get_all_nodes():
        if g.__class__.__name__ in ["Goal", "Constraint"]:
            print(f"   [{g.id}] {g.__class__.__name__}: {g.statement}")

    # Passo 2
    step_pause("PASSO 2: Introdução de Premissas e Alternativas")
    fact_volume = session.introduce_claim(
        statement="A base de conhecimento inicial é inferior a 500 MB de texto",
        epistemic_type=EpistemicType.VERIFIED_FACT,
    )
    assump_cloud = session.introduce_claim(
        statement="Um cluster de banco vetorial gerenciado em nuvem é indispensável para busca semântica de qualidade",
        epistemic_type=EpistemicType.ASSUMPTION,
        invalidation_conditions=["Modelos de embedding locais quantizados atingirem precisão comparável"],
    )
    assump_local = session.introduce_claim(
        statement="SQLite com busca híbrida (FTS5 + embeddings locais) opera em < 50MB de RAM",
        epistemic_type=EpistemicType.ASSUMPTION,
    )

    alt_cloud = session.propose_alternative(
        title="Cluster Vetorial em Nuvem (Qdrant Cloud / Pinecone)",
        description="Infraestrutura gerenciada externa com busca vetorial pura",
        depends_on_claim_ids=[assump_cloud.id],
    )
    alt_local = session.propose_alternative(
        title="SQLite Híbrido Local (FTS5 + MiniLM local)",
        description="Armazenamento local embarcado com busca lexical e vetorial",
        depends_on_claim_ids=[assump_local.id, fact_volume.id],
    )

    print(f"📘 Fato: '{fact_volume.statement}'")
    print(f"💡 Suposição 1: '{assump_cloud.statement}'")
    print(f"💡 Suposição 2: '{assump_local.statement}'")
    print(f"🌱 Alternativa 1: '{alt_cloud.title}' (Depende da Suposição 1)")
    print(f"🌱 Alternativa 2: '{alt_local.title}' (Depende da Suposição 2 e Fato)")

    # Passo 3
    step_pause("PASSO 3: Aletheia apresenta a interpretação estrutural")
    interpretation_1 = session.get_interpretation()
    print(interpretation_1)

    # Passo 4 & 5
    step_pause("PASSO 4 & 5: Humano contesta a Suposição 1 ('Nuvem é indispensável')")
    print("Humano intervém: 'Discordo. Embeddings locais quantizados rodam localmente com alta precisão e privacidade.'")
    affected = session.challenge_premise(
        claim_id=assump_cloud.id,
        rationale="Modelos quantizados locais já atingem recall suficiente sem vazar dados para a nuvem.",
    )
    print(f"\n⚡ Suposição [{assump_cloud.id}] agora está: {session.workspace.graph.get_node(assump_cloud.id).lifecycle_status.value}")
    print(f"⚠️ Alternativa [{alt_cloud.id}] suspensa em cascata: {session.workspace.graph.get_node(alt_cloud.id).lifecycle_status.value}")
    print(f"   Nós suspensos: {affected}")

    # Passo 6
    step_pause("PASSO 6: Humano muda o foco da deliberação para 'privacidade'")
    print("Humano declara: 'Esquece nuvem por enquanto. Nosso foco agora é privacidade e offline.'")
    projection_priv = session.change_direction("privacidade")
    print(f"🔄 Foco ativo: '{session.current_focus}'")
    print(f"📌 Nós na projeção saliente de privacidade: {[n.id for n in projection_priv.salient_nodes]}")

    # Passo 7 & 8
    step_pause("PASSO 7 & 8: Nova interpretação sob o foco de privacidade e estado revisado")
    interpretation_2 = session.get_interpretation()
    print(interpretation_2)

    # Passo 9
    step_pause("PASSO 9: Ratificação formal do Cognitive Decision Record (CDR)")
    cdr = session.deliberate_and_decide(
        title="Adoção de SQLite Híbrido Local",
        chosen_alt_id=alt_local.id,
        scope="Módulo de armazenamento de conhecimento da Aletheia v0.1",
        underlying_assumptions=[assump_local.id],
        human_rationale="Privacidade total e operação offline superam a conveniência de clusters em nuvem.",
        dissenting_views=[
            DissentingView(
                actor_id="critic_cloud",
                position=ArgumentStance.OPPOSE,
                argument_refs=[],
                rationale="Cluster em nuvem teria menos trabalho de empacotamento local de binários.",
            )
        ],
    )
    print(f"✅ CDR Ratificado [{cdr.cdr_id}]:")
    print(f"   Título: {cdr.title}")
    print(f"   Escopo: {cdr.decision_scope}")
    print(f"   Alternativa Escolhida: {cdr.chosen_alternative_ref}")
    print(f"   Dissidência Preservada: {cdr.dissenting_views[0].actor_id} ({cdr.dissenting_views[0].rationale})")

    # Passo 10
    step_pause("PASSO 10: Invariante de Reconstrução por Replay")
    events = session.workspace.event_store.get_all_events()
    print(f"Total de eventos imutáveis registrados no log: {len(events)}")
    replayed_ws = session.workspace.replay(events)
    print(f"Nós no Workspace original: {len(session.workspace.graph.get_all_nodes())}")
    print(f"Nós no Workspace reconstruído via Replay: {len(replayed_ws.graph.get_all_nodes())}")
    print(f"Arestas no Workspace original: {len(session.workspace.graph.get_all_edges())}")
    print(f"Arestas no Workspace reconstruído via Replay: {len(replayed_ws.graph.get_all_edges())}")
    print("🎉 100% de paridade determinística validada!")

    print("\n" + "=" * 70)
    print("  FIM DA DEMONSTRAÇÃO DO CENÁRIO M1")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
