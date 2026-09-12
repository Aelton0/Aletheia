# 15 — Registro de Decisões Arquiteturais Reconstruídas (ADRs)

Este documento reconstrói as decisões arquiteturais fundamentais tomadas durante o desenvolvimento do Aletheia, com base nas evidências comprovadas no código-fonte e histórico de commits.

---

### ADR-01: Adoção do Padrão Event Sourcing para o Cognitive Workspace
* **Decisão**: Modelar o `CognitiveWorkspace` como um estado derivado de um log append-only imutável de eventos (`CognitiveEvent`).
* **Contexto**: Sistemas de deliberação complexos sofrem com a perda do histórico de como uma decisão foi alcançada, impedindo auditorias e investigações de "quem propôs o que e com base em quais premissas".
* **Solução adotada**: Cada mutação produz um `CognitiveEvent` imutável gravado no `EventStorePort`. O estado do grafo é 100% reproduzível via `CognitiveWorkspace.replay(events)`.
* **Evidência**: [`aletheia/core/context/workspace.py:L76-85`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/context/workspace.py#L76-L85), [`aletheia/core/context/workspace.py:L226-282`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/context/workspace.py#L226-L282), commit `ba315a2`.
* **Motivação conhecida**: Garantir o Invariante de Reconstrução por Replay e auditabilidade determinística ponta a ponta.
* **Trade-offs**: Maior complexidade estrutural em comparação com um CRUD simples mutável; necessidade de manter schemas de eventos imutáveis e mapa de classes para deserialização (`ENTITY_CLASS_MAP`).
* **Consequências**: Histórico inalterável, capacidade de viajar no tempo e paridade determinística validada por testes.
* **Status**: **RATIFICADO E IMPLEMENTADO**.

---

### ADR-02: Separação Categórica entre Tipo Epistêmico e Status de Ciclo de Vida
* **Decisão**: Dissociar a natureza ontológica de uma afirmação (`epistemic_type`: HYPOTHESIS, ASSUMPTION, VERIFIED_FACT) do seu estado deliberativo momentâneo (`lifecycle_status`: ACTIVE, UNDER_REVIEW, SUPPORTED, INVALIDATED, SUSPENDED, CONFLICT).
* **Contexto**: Em agentes tradicionais, quando um modelo ou usuário "confirma" uma suposição, ela é frequentemente tratada erroneamente como verdade absoluta inquestionável.
* **Solução adotada**: Uma suposição corroborada recebe `lifecycle_status = SUPPORTED`, mas continua sendo ontologicamente uma `ASSUMPTION` sujeita a refutação futura (`SUPPORTED != VERIFIED_FACT`).
* **Evidência**: [`aletheia/core/entities/epistemic.py:L15-73`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/entities/epistemic.py#L15-L73), [`tests/test_entities.py:L29-44`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/tests/test_entities.py#L29-L44).
* **Motivação conhecida**: Aderência estrita à epistemologia falseacionista popperiana e prevenção de dogmatismo algorítmico.
* **Trade-offs**: Requer que os desenvolvedores e algoritmos verifiquem ambos os campos (tipo e status) ao raciocinar sobre premissas.
* **Consequências**: Elimina alucinações de certeza e permite suspensão em cascata elegante quando fatos novos contradizem suposições prévias.
* **Status**: **RATIFICADO E IMPLEMENTADO**.

---

### ADR-03: Autoridade Estritamente Consultiva (Advisory) para Capacidades de IA
* **Decisão**: Nenhuma capacidade analítica ou modelo de IA pode alterar o grafo ou o estado do sistema diretamente.
* **Contexto**: Agentes com permissão de escrita direta no grafo sofrem com corrupção de estado, introdução de alucinações irreversíveis e quebra de invariantes estruturais.
* **Solução adotada**: As capacidades recebem `CapabilityAuthority.ADVISORY`. Elas executam sua lógica sobre projeções e retornam um `CapabilityResult` contendo propostas estruturadas (`produced_entities`, `proposed_relations`, `human_action_request`). O Kernel valida, assegura proveniência e decide se grava ou não no Workspace.
* **Evidência**: [`aletheia/cognition/capabilities/base.py:L18-22`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/capabilities/base.py#L18-L22), [`aletheia/cognition/runtime/runtime.py:L104-122`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/runtime/runtime.py#L104-L122), commit `6d4a39a`.
* **Motivação conhecida**: Garantir a soberania humana e a integridade matemática do grafo epistêmico.
* **Trade-offs**: O Kernel necessita inspecionar e aplicar entidades passo a passo, exigindo mais código de orquestração no runtime.
* **Consequências**: Isolamento seguro contra agentes defeituosos ou alucinações destrutivas.
* **Status**: **RATIFICADO E IMPLEMENTADO**.

---

### ADR-04: Isolamento Contextual via Motor de Projeções (Invariante 7)
* **Decisão**: Capacidades cognitivas nunca recebem o grafo global do problema; recebem apenas uma projeção contextual mínima e suficiente.
* **Contexto**: Injetar o grafo inteiro no prompt ou contexto do modelo excede janelas de contexto, dilui a atenção do LLM e expõe premissas irrelevantes a ataques de injeção.
* **Solução adotada**: O `ProjectionEngine` extrai um subgrafo saliente contendo apenas metas e restrições ativas mais nós a 1 salto de distância do nó focal ou foco temático declarado.
* **Evidência**: [`aletheia/core/context/projection.py:L35-132`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/context/projection.py#L35-L132), [`tests/test_capability_runtime.py:L38-79`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/tests/test_capability_runtime.py#L38-L79).
* **Motivação conhecida**: Invariante 7 do projeto (Princípio da Necessidade e Suficiência Cognitiva).
* **Trade-offs**: Capacidades não conseguem enxergar correlações globais distantes fora do raio de projeção.
* **Consequências**: Prompts limpos, foco cirúrgico na análise crítica e redução substancial de tokens.
* **Status**: **RATIFICADO E IMPLEMENTADO**.

---

### ADR-05: Fronteira de Segurança Cognitiva em Dois Estágios para LLMs
* **Decisão**: Submeter todo output de LLM a validação estrutural e validação epistemológica antes da aceitação pelo Kernel.
* **Contexto**: Modelos probabilísticos alucinam identificadores e premissas inexistentes, e são vulneráveis a ataques de prompt injection contidos nos dados de entrada.
* **Solução adotada**: Pipeline de contenção com (1) `ProjectionPromptSerializer` demarcando dados vs comandos, (2) `StructuralValidator` purgando IDs alucinados e calculando RHR, e (3) `EpistemicValidator` calculando grounding (CGR) e calibrando suporte epistêmico real.
* **Evidência**: [`aletheia/cognition/capabilities/llm_critique.py:L76-109`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/capabilities/llm_critique.py#L76-L109), commit `e0b1978`.
* **Motivação conhecida**: Garantir que nenhum ID ou premissa espúria atravesse para o grafo epistêmico.
* **Trade-offs**: Custo computacional adicional de sanitização e validação Pydantic após a resposta do modelo.
* **Consequências**: Taxa de alucinação referencial comprovada de 0.0% no benchmark canônico.
* **Status**: **RATIFICADO E IMPLEMENTADO**.

---

### ADR-06: Tratamento Dialético de Contradições sem Auto-Invalidação
* **Decisão**: A identificação de uma inconsistência entre duas premissas não deve invalidar automaticamente nenhuma das partes.
* **Contexto**: Em processos reais de formulação de problemas ou investigações científicas, existem teses conflitantes válidas simultaneamente antes que a evidência empírica final seja produzida.
* **Solução adotada**: A função `register_contradiction` altera o status de ambos os nós para `CONFLICT` e cria uma aresta bidirecional `CONTRADICTS`, mantendo ambos no grafo até decisão humana.
* **Evidência**: [`aletheia/cognition/epistemic/conflicts.py:L15-55`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/epistemic/conflicts.py#L15-L55), [`tests/test_contradiction_policy.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/tests/test_contradiction_policy.py).
* **Motivação conhecida**: Preservar a dialética e evitar perda prematura de caminhos deliberativos.
* **Trade-offs**: O grafo pode permanecer em estado de conflito até que haja intervenção deliberada.
* **Consequências**: Tolerância a inconsistências controladas e preservação de pontos de atrito cognitivo.
* **Status**: **RATIFICADO E IMPLEMENTADO**.

---

### ADR-07: Adoção Provisória de Adaptadores em Memória
* **Decisão**: Utilizar `InMemoryGraphAdapter` e `InMemoryEventStore` nas fases M0–M3.
* **Contexto**: A prioridade inicial foi a formalização conceitual da ontologia e dos algoritmos do Kernel, sem introduzir complexidade acidental de infraestrutura ou dependências pesadas de bancos externos.
* **Solução adotada**: Implementações limpas em Python puro usando `dict` e `list`.
* **Evidência**: [`aletheia/adapters/in_memory_graph.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/adapters/in_memory_graph.py), [`aletheia/adapters/in_memory_event_store.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/adapters/in_memory_event_store.py).
* **Trade-offs**: Ausência total de durabilidade em disco e ausência de concorrência multithread.
* **Consequências**: Rapidez extrema na suíte de testes (0.12s), porém gera a principal dívida técnica do sistema (TD-01).
* **Status**: **PROVISÓRIO / DEVE SER EVOLUÍDO**.
