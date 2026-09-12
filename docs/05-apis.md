# 05 — Interfaces e APIs do Sistema (APIs & Interfaces)

A auditoria confirma que o Aletheia **não expõe portas de rede, servidores HTTP (REST/FastAPI), gRPC ou WebSockets** (*FATO*). Toda a comunicação é realizada através de:
1. **API Programática em Python** (classes de orquestração e domínio);
2. **Interface de Linha de Comando Interativa (CLI REPL)** no terminal.

---

## 1. Mapeamento da API Programática: `InteractiveSession`

A classe `InteractiveSession` ([`aletheia/interaction/session.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/interaction/session.py)) constitui a fachada de alto nível (*Facade*) para consumo por desenvolvedores ou agentes.

| Método | Entradas | Validação Realizada | Efeitos Colaterais / Mutações | Saída |
| :--- | :--- | :--- | :--- | :--- |
| `define_problem(...)` | `statement: str`, `goals: Optional[List[str]]`, `constraints: Optional[List[str]]` | Pydantic em `Goal` e `Constraint` | Introduz nós `Goal` e `Constraint` no grafo; emite eventos `EntityIntroduced` | `List[str]` (IDs gerados) |
| `introduce_claim(...)` | `statement: str`, `epistemic_type: EpistemicType`, `author_id: Optional[str]`, `rationale: Optional[str]`, `invalidation_conditions: Optional[List[str]]` | Pydantic em `Claim` | Introduz nó `Claim` com status `ACTIVE`; emite evento | `Claim` |
| `introduce_unknown(...)` | `description: str`, `blocking: bool`, `author_id: Optional[str]` | Pydantic em `Unknown` | Introduz nó `Unknown` no grafo; emite evento | `Unknown` |
| `propose_alternative(...)` | `title: str`, `description: str`, `addresses_goal_ids: Optional[List[str]]`, `depends_on_claim_ids: Optional[List[str]]`, `author_id: Optional[str]` | Valida existência dos nós alvo antes de conectar | Introduz `Alternative`, conecta arestas `ADDRESSES` e `DEPENDS_ON`; emite múltiplos eventos | `Alternative` |
| `challenge_premise(...)` | `claim_id: str`, `rationale: str` | Verifica se o nó existe (KeyError se não) | Altera status para `UNDER_REVIEW`, suspende nós dependentes (`SUSPENDED`); emite evento | `List[str]` (IDs afetados) |
| `change_direction(...)` | `focus: str` | `strip()` no texto de foco | Atualiza `current_focus`; emite evento `HumanDirectionChanged` | `CognitiveProjection` |
| `get_projection()` | Nenhuma | Nenhuma | Calcula subgrafo saliente via `ProjectionEngine` | `CognitiveProjection` |
| `get_interpretation()` | Nenhuma | Nenhuma | Invoca `CognitiveSynthesizer.generate_interpretation()` | `str` (Markdown) |
| `step_capabilities(...)` | `capability_name: Optional[str]`, `target_id: Optional[str]` | `WorkspaceStateAnalyzer` + `CapabilitySelector` | Executa 1 capacidade, muta grafo com entidades/relações geradas; emite evento | `Optional[CapabilityResult]` |
| `run_capability_policy(...)` | `safety_limit: int = 5` | Loop com teto numérico de segurança | Executa passos até estabilidade ou atingir o teto | `List[CapabilityResult]` |
| `deliberate_and_decide(...)` | `title: str`, `chosen_alt_id: str`, `scope: str`, `underlying_assumptions: Optional[List[str]]`, `human_rationale: Optional[str]`, `dissenting_views: Optional[List[DissentingView]]`, `reversibility: ReversibilityType` | `validate_cdr_integrity` (escopo >= 3 caracteres, alternativa deve existir, supersedes deve existir) | Introduz `CDR`, conecta `SELECTS`, `SUPERSEDES`, `DEPENDS_ON`; emite eventos | `CognitiveDecisionRecord` |
| `get_cognitive_summary()` | Nenhuma | Nenhuma | Consulta estática e agregação de contagens do grafo | `Dict[str, Any]` |

---

## 2. Interface de Linha de Comando: CLI REPL (`interactive.py`)

A CLI em [`aletheia/interactive.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/interactive.py) roda no terminal via loop interativo com prompt dinâmico mostrando o foco ativo: `[Foco: Geral] aletheia> `.

### Comandos Suportados:
* `/problem <texto>`: Registra objetivo principal.
* `/claim <texto>`: Adiciona premissa/suposição (`EpistemicType.ASSUMPTION`).
* `/fact <texto>`: Adiciona fato verificado (`EpistemicType.VERIFIED_FACT`).
* `/alt <título> | <desc>`: Adiciona alternativa de solução.
* `/link <alt_id> <c_id>`: Cria aresta `DEPENDS_ON` da alternativa para a premissa.
* `/challenge <id> <motivo>`: Contesta uma premissa (iniciativa humana).
* `/step`: Dispara um passo atômico do `CapabilityRuntime`.
* `/think`: Executa o ciclo autônomo de capacidades até estabilização (limite de 5 passos).
* `/focus <tema>`: Altera o foco deliberativo da sessão.
* `/interpret`: Exibe a síntese cognitiva em linguagem natural da Aletheia.
* `/decide <alt_id> <escopo>`: Ratifica um `CognitiveDecisionRecord`.
* `/status`: Exibe contagens do Workspace.
* `/replay`: Executa o teste de replay determinístico na memória e valida paridade.
* `/exit`: Encerra o processo do terminal.

---

## 3. Problemas e Lacunas Identificadas nas Interfaces

1. **DOCUMENTAÇÃO ≠ IMPLEMENTAÇÃO (Contratos implícitos na CLI)**:
   * No comando `/alt <título> | <desc>`, se o usuário não incluir o separador `|`, o código faz fallback silencioso usando o mesmo texto para título e descrição (`alt = session.propose_alternative(body, body)`).
   * O comando `/link` não valida se os IDs fornecidos são realmente uma Alternativa e uma Premissa, permitindo ligar nós incompatíveis via `session.workspace.connect(alt_id, claim_id, "depends_on", ...)`.
2. **Tratamento de Erros Genérico na CLI**:
   * O loop da CLI captura `except Exception as e: print(f"❌ Erro operacional: {e}")`. Isso mascara erros de programação (bugs internos, bugs de estado do Pydantic) da mesma forma que erros de entrada do usuário.
3. **Falta de API REST / Externa**:
   * O sistema não possui adaptadores para ser integrado a frontends modernos (Next.js, Vue, React) ou ferramentas de chat (Slack, Discord, Telegram), restringindo seu uso ao terminal local ou a scripts Python diretos.
