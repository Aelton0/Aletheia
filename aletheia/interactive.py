"""CLI Interativa da Aletheia: Sentar à mesa e pensar junto.

Permite experimentar o Cognitive Workspace interativo diretamente pelo terminal.
"""

import os
import sys

# Garante que o diretório raiz do projeto esteja no path para importação limpa
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from aletheia.core.entities import (
    ArgumentStance,
    DissentingView,
    EpistemicType,
)
from aletheia.interaction.session import InteractiveSession


def print_banner() -> None:
    print("=" * 70)
    print("  ALETHEIA — Cognitive Kernel v0.1 (Interactive Mode)")
    print("  Sistema de Cognição Colaborativa Humano-IA")
    print("=" * 70)
    print("Comandos disponíveis:")
    print("  /problem <texto>      - Define o problema ou meta principal")
    print("  /claim <texto>        - Adiciona uma premissa/suposição")
    print("  /fact <texto>         - Adiciona um fato verificado")
    print("  /alt <título> | <desc>- Propõe uma alternativa de solução")
    print("  /link <alt_id> <c_id> - Conecta alternativa a uma premissa de dependência")
    print("  /challenge <id> <motivo>- Contesta uma premissa (HumanInitiative)")
    print("  /focus <tema>         - Muda o foco da deliberação (HumanDirectionChanged)")
    print("  /interpret            - Solicita a interpretação cognitiva da Aletheia")
    print("  /decide <alt_id> <escopo> - Ratifica um CDR")
    print("  /status               - Exibe o resumo do grafo cognitivo")
    print("  /replay               - Testa o replay determinístico da sessão")
    print("  /exit                 - Encerra a sessão")
    print("=" * 70)


def run_cli() -> None:
    print_banner()
    session = InteractiveSession(human_name="Humano")

    while True:
        try:
            prompt = f"\n[Foco: {session.current_focus or 'Geral'}] aletheia> "
            user_input = input(prompt).strip()
            if not user_input:
                continue

            if user_input.startswith("/exit"):
                print("Encerrando sessão cognitiva. Até logo!")
                break

            elif user_input.startswith("/problem"):
                stmt = user_input[len("/problem"):].strip()
                if stmt:
                    gids = session.define_problem(stmt)
                    print(f"🎯 Meta registrada [{gids[0]}]: '{stmt}'")
                else:
                    print("Uso: /problem <descrição do problema>")

            elif user_input.startswith("/claim"):
                stmt = user_input[len("/claim"):].strip()
                if stmt:
                    c = session.introduce_claim(stmt, epistemic_type=EpistemicType.ASSUMPTION)
                    print(f"💡 Premissa/Suposição registrada [{c.id}]: '{stmt}'")
                else:
                    print("Uso: /claim <afirmação>")

            elif user_input.startswith("/fact"):
                stmt = user_input[len("/fact"):].strip()
                if stmt:
                    c = session.introduce_claim(stmt, epistemic_type=EpistemicType.VERIFIED_FACT)
                    print(f"📘 Fato verificado registrado [{c.id}]: '{stmt}'")
                else:
                    print("Uso: /fact <afirmação>")

            elif user_input.startswith("/alt"):
                body = user_input[len("/alt"):].strip()
                if "|" in body:
                    title, desc = body.split("|", 1)
                    alt = session.propose_alternative(title.strip(), desc.strip())
                    print(f"🌱 Alternativa proposta [{alt.id}]: '{title.strip()}'")
                elif body:
                    alt = session.propose_alternative(body, body)
                    print(f"🌱 Alternativa proposta [{alt.id}]: '{body}'")
                else:
                    print("Uso: /alt <título> | <descrição>")

            elif user_input.startswith("/link"):
                parts = user_input[len("/link"):].strip().split()
                if len(parts) >= 2:
                    alt_id, claim_id = parts[0], parts[1]
                    session.workspace.connect(alt_id, claim_id, "depends_on", session.human.id)
                    print(f"🔗 Alternativa '{alt_id}' agora depende de '{claim_id}'")
                else:
                    print("Uso: /link <alt_id> <claim_id>")

            elif user_input.startswith("/challenge"):
                parts = user_input[len("/challenge"):].strip().split(maxsplit=1)
                if len(parts) == 2:
                    cid, rat = parts[0], parts[1]
                    affected = session.challenge_premise(cid, rat)
                    print(f"⚡ Premissa [{cid}] contestada: colocada UNDER_REVIEW.")
                    if affected:
                        print(f"   ⚠️ Dependentes suspensos automaticamente em cascata: {affected}")
                else:
                    print("Uso: /challenge <claim_id> <motivo>")

            elif user_input.startswith("/focus"):
                theme = user_input[len("/focus"):].strip()
                if theme:
                    session.change_direction(theme)
                    print(f"🔄 Foco alterado para: '{theme}'. Projeção contextual recalculada.")
                else:
                    print("Uso: /focus <tema>")

            elif user_input.startswith("/interpret"):
                interpretation = session.get_interpretation()
                print("\n" + "=" * 50)
                print(interpretation)
                print("=" * 50)

            elif user_input.startswith("/decide"):
                parts = user_input[len("/decide"):].strip().split(maxsplit=1)
                if len(parts) == 2:
                    alt_id, scope = parts[0], parts[1]
                    cdr = session.deliberate_and_decide(
                        title=f"Decisão sobre {alt_id}",
                        chosen_alt_id=alt_id,
                        scope=scope,
                        human_rationale="Decidido interativamente via CLI",
                    )
                    print(f"✅ CDR ratificado [{cdr.cdr_id}]: Alternativa escolhida: '{alt_id}'")
                else:
                    print("Uso: /decide <alt_id> <escopo_contextual>")

            elif user_input.startswith("/status"):
                summary = session.get_cognitive_summary()
                print("\n📊 Resumo do Cognitive Workspace:")
                for k, v in summary.items():
                    print(f"   {k}: {v}")

            elif user_input.startswith("/replay"):
                events = session.workspace.event_store.get_all_events()
                replayed = session.workspace.replay(events)
                orig_nodes = len(session.workspace.graph.get_all_nodes())
                rep_nodes = len(replayed.graph.get_all_nodes())
                print(f"🔁 Replay determinístico concluído: {rep_nodes}/{orig_nodes} nós perfeitamente reconstruídos a partir de {len(events)} eventos.")

            else:
                print(f"Comando não reconhecido. Digite /problem, /claim, /alt, /challenge, /focus, /interpret ou /exit.")

        except KeyboardInterrupt:
            print("\nSessão interrompida pelo usuário.")
            break
        except Exception as e:
            print(f"❌ Erro operacional: {e}")


if __name__ == "__main__":
    run_cli()
