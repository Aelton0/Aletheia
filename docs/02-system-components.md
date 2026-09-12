# 02 — Inventário de Componentes do Sistema (System Components)

Este documento cataloga exaustivamente todos os componentes, módulos e subsistemas da base de código do Aletheia.

---

## 1. Núcleo Ontológico (Core Entities)

### 1.1. `aletheia.core.entities.base`
* **Responsabilidade**: Define primitivos de identificação (`generate_id`) e a classe base Pydantic para toda entidade no sistema (`CognitiveEntity`).
* **Localização**: [`aletheia/core/entities/base.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/entities/base.py)
* **Dependências internas**: Nenhuma.
* **Consumidores**: Todas as classes de entidades em `aletheia.core.entities.*`.
* **Dependências externas**: `pydantic` (`BaseModel`, `ConfigDict`, `Field`), `datetime`, `uuid`.
* **Estado**: Stateless (define schemas e gerador de IDs).
* **Entradas**: Configurações de modelo Pydantic (`extra="forbid"`, `validate_assignment=True`).
* **Saídas**: Instâncias tipadas de `CognitiveEntity` com `id`, `created_at` (UTC) e `metadata`.

### 1.2. `aletheia.core.entities.actors`
* **Responsabilidade**: Modela atores do ecossistema cognitivo e o modelo de capacidades atômicas.
* **Localização**: [`aletheia/core/entities/actors.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/entities/actors.py)
* **Dependências internas**: `CognitiveEntity`, `generate_id` de `base.py`.
* **Consumidores**: `aletheia.interaction.session`, `aletheia.cognition.runtime.runtime`, `aletheia.cognition.capabilities.base`.
* **Dependências externas**: `pydantic`, `enum`.
* **Estado**: Instâncias mantêm identificação, papel (`HUMAN` ou `SPECIALIST`), prerrogativas (`has_veto_power: bool`), lista de capacidades (`Capability`) e políticas.
* **Entradas**: Parâmetros de construtor (`name`, `perspective`, `capabilities`).
* **Saídas**: Entidades `HumanActor` e `SpecialistActor`.

### 1.3. `aletheia.core.entities.epistemic`
* **Responsabilidade**: Define os tipos ontológicos de conhecimento e ciclo de vida proposicional.
* **Localização**: [`aletheia/core/entities/epistemic.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/entities/epistemic.py)
* **Classes**: `EpistemicType` (HYPOTHESIS, ASSUMPTION, VERIFIED_FACT), `LifecycleStatus` (ACTIVE, UNDER_REVIEW, SUPPORTED, INVALIDATED, SUSPENDED, RESOLVED, CONFLICT), `DerivationMethod`, `QuestionStatus`, `Claim`, `Evidence`, `Inference`, `Unknown`, `Question`.
* **Dependências internas**: `CognitiveEntity` de `base.py`.
* **Consumidores**: Quase todos os módulos do sistema (TMS, Synthesizer, Runtime, Projeção).
* **Dependências externas**: `pydantic`, `enum`.
* **Estado**: Instâncias imutáveis ou mutáveis via validação Pydantic com proveniência (`author_id`).

### 1.4. `aletheia.core.entities.deliberation`
* **Responsabilidade**: Modela o espaço de decisão: Metas, Restrições invioláveis, Alternativas de solução, Argumentos e Recomendações.
* **Localização**: [`aletheia/core/entities/deliberation.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/entities/deliberation.py)
* **Classes**: `AlternativeStatus`, `ArgumentStance` (SUPPORT, OPPOSE), `Goal`, `Constraint`, `Alternative`, `Argument`, `Recommendation`.
* **Dependências internas**: `CognitiveEntity`, `LifecycleStatus`.
* **Consumidores**: `workspace.py`, `projection.py`, `synthesizer.py`, `capabilities.*`.

### 1.5. `aletheia.core.entities.decision`
* **Responsabilidade**: Define o registro formal de decisão cognitiva (`CognitiveDecisionRecord` — CDR), visões dissidentes (`DissentingView`), tipos de reversibilidade (`TYPE_1_IRREVERSIBLE`, `TYPE_2_REVERSIBLE`) e status.
* **Localização**: [`aletheia/core/entities/decision.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/entities/decision.py)
* **Dependências internas**: `CognitiveEntity`, `ArgumentStance`.
* **Consumidores**: `cdr.py`, `workspace.py`, `session.py`.

### 1.6. `aletheia.core.entities.experience`
* **Responsabilidade**: Modela o ciclo de ação pós-decisão, observação da realidade e aprendizado incremental.
* **Localização**: [`aletheia/core/entities/experience.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/entities/experience.py)
* **Classes**: `DeltaType`, `Action`, `Outcome`, `EpistemicDelta`, `Lesson`.
* **Dependências internas**: `CognitiveEntity`.
* **Consumidores**: Registrado em `ENTITY_CLASS_MAP` para replay.

---

## 2. Eventos e Barramento (Events & Bus)

### 2.1. `aletheia.core.events.schemas`
* **Responsabilidade**: Define as 14 relações semânticas formais do grafo (`EdgeRelation`) e o schema imutável dos eventos (`CognitiveEvent`), além dos payloads tipados.
* **Localização**: [`aletheia/core/events/schemas.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/events/schemas.py)
* **Dependências internas**: Nenhuma.
* **Consumidores**: `ports/graph_port.py`, `ports/event_store_port.py`, `workspace.py`.
* **Dependências externas**: `pydantic` (`ConfigDict(frozen=True)`), `uuid`, `datetime`.

### 2.2. `aletheia.core.events.bus`
* **Responsabilidade**: Barramento síncrono de publicação e subscrição de eventos cognitivos em memória.
* **Localização**: [`aletheia/core/events/bus.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/events/bus.py)
* **Dependências internas**: `CognitiveEvent` de `schemas.py`.
* **Consumidores**: `CognitiveWorkspace`, `InteractiveSession`.
* **Estado**: Stateful (`_subscribers: Dict[str, List[EventHandler]]`, `_global_subscribers`).
* **Limitação**: Totalmente síncrono; erros em handlers bloqueiam o fluxo chamador.

---

## 3. Contexto e Blackboard (Context)

### 3.1. `aletheia.core.context.workspace`
* **Responsabilidade**: Ponto central de coordenação do Blackboard. Mantém as instâncias de Grafo, EventStore e Bus. Centraliza mutações do estado e executa o **Replay Determinístico**.
* **Localização**: [`aletheia/core/context/workspace.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/context/workspace.py)
* **Dependências internas**: Entidades (`aletheia.core.entities`), `EventBus`, `CognitiveEvent`, `EdgeRelation`, Portas (`GraphStoragePort`, `EventStorePort`), Adaptadores padrão (`InMemoryGraphAdapter`, `InMemoryEventStore`), Cognição (`tms`, `conflicts`, `cdr`).
* **Consumidores**: `InteractiveSession`, `CapabilityRuntime`, benchmarks e testes.
* **Estado**: Stateful via portas injetadas.

### 3.2. `aletheia.core.context.projection`
* **Responsabilidade**: Motor de Projeção Contextual (`ProjectionEngine`). Gera subgrafos salientes autorizados (`CognitiveProjection`) baseados no foco de deliberação ou nó focal.
* **Localização**: [`aletheia/core/context/projection.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/context/projection.py)
* **Dependências internas**: Entidades (`Goal`, `Constraint`, `Alternative`, `Claim`, `Question`), `GraphStoragePort`, `Edge`.
* **Consumidores**: `InteractiveSession`, `CapabilityRuntime`, `ProjectionPromptSerializer`.
* **Estado**: Stateless (função de projeção pura sobre o grafo).

---

## 4. Portas e Adaptadores (Ports & Adapters)

### 4.1. `aletheia.ports.graph_port`
* **Responsabilidade**: Contrato abstrato (`GraphStoragePort`) e modelo de aresta direcionada (`Edge`).
* **Localização**: [`aletheia/ports/graph_port.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/ports/graph_port.py)

### 4.2. `aletheia.ports.event_store_port`
* **Responsabilidade**: Contrato formal para persistência append-only de eventos cognitivos (`EventStorePort`).
* **Localização**: [`aletheia/ports/event_store_port.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/ports/event_store_port.py)

### 4.3. `aletheia.ports.llm_port`
* **Responsabilidade**: Contrato formal para provedores de LLM (`LLMProviderPort`) e encapsulamento de resposta auditável (`LLMResponse`).
* **Localização**: [`aletheia/ports/llm_port.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/ports/llm_port.py)

### 4.4. `aletheia.adapters.in_memory_graph`
* **Responsabilidade**: Armazenamento do Grafo Epistêmico em dicionários Python (`_nodes`, `_outgoing`, `_incoming`).
* **Localização**: [`aletheia/adapters/in_memory_graph.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/adapters/in_memory_graph.py)

### 4.5. `aletheia.adapters.in_memory_event_store`
* **Responsabilidade**: Armazenamento sequencial em lista Python (`_events`).
* **Localização**: [`aletheia/adapters/in_memory_event_store.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/adapters/in_memory_event_store.py)

### 4.6. `aletheia.adapters.mock_llm_adapter`
* **Responsabilidade**: Emulador determinístico de LLM com suporte a fixtures e handlers dinâmicos para testes e benchmarks offline.
* **Localização**: [`aletheia/adapters/mock_llm_adapter.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/adapters/mock_llm_adapter.py)

---

## 5. Motor Cognitivo (Cognition)

### 5.1. `aletheia.cognition.epistemic.tms`
* **Responsabilidade**: Propagação de suspensão em cascata para dependentes lógicos (`invalidate_claim`, `challenge_claim`).
* **Localização**: [`aletheia/cognition/epistemic/tms.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/epistemic/tms.py)

### 5.2. `aletheia.cognition.epistemic.conflicts`
* **Responsabilidade**: Registro de contradições dialéticas (`register_contradiction`).
* **Localização**: [`aletheia/cognition/epistemic/conflicts.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/epistemic/conflicts.py)

### 5.3. `aletheia.cognition.deliberation.cdr`
* **Responsabilidade**: Validação estrita de invariantes de Cognitive Decision Records (`validate_cdr_integrity`).
* **Localização**: [`aletheia/cognition/deliberation/cdr.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/deliberation/cdr.py)

### 5.4. `aletheia.cognition.reasoning.synthesizer`
* **Responsabilidade**: Análise determinística de viabilidade e geração de texto de interpretação em linguagem natural (`CognitiveSynthesizer`).
* **Localização**: [`aletheia/cognition/reasoning/synthesizer.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/reasoning/synthesizer.py)

---

## 6. Runtime e Capacidades (Capability Runtime & Model)

### 6.1. `aletheia.cognition.capabilities.base`
* **Responsabilidade**: Define os contratos e estruturas do Capability Model: `CapabilityContract`, `CapabilityAuthority`, `CapabilityStateSummary`, `CapabilityTarget`, `CapabilityResult`, `HumanActionRequest`, `CognitiveCapability`.
* **Localização**: [`aletheia/cognition/capabilities/base.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/capabilities/base.py)

### 6.2. `aletheia.cognition.capabilities.registry`
* **Responsabilidade**: Catálogo em memória de capacidades cognitivas registradas (`CapabilityRegistry`).
* **Localização**: [`aletheia/cognition/capabilities/registry.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/capabilities/registry.py)

### 6.3. Capacidades Puras Implementadas:
* `CritiqueCapability`: Ceticismo metódico sobre alternativas com suposições ativas. Local: [`aletheia/cognition/capabilities/critique.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/capabilities/critique.py).
* `ViabilityReviewCapability`: Auditoria de viabilidade para alternativas com premissas comprometidas. Local: [`aletheia/cognition/capabilities/viability.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/capabilities/viability.py).
* `QuestionGenerationCapability`: Conversão de Unknowns bloqueantes em perguntas estruturadas. Local: [`aletheia/cognition/capabilities/question.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/capabilities/question.py).
* `LLMCritiqueCapability`: Crítica probabilística com fronteira de segurança cognitiva. Local: [`aletheia/cognition/capabilities/llm_critique.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/capabilities/llm_critique.py).

### 6.4. `aletheia.cognition.runtime.analyzer`, `selector`, `runtime`
* `WorkspaceStateAnalyzer`: Inspeciona o grafo e extrai o `CapabilityStateSummary` sem expor o grafo às capacidades. Local: [`aletheia/cognition/runtime/analyzer.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/runtime/analyzer.py).
* `CapabilitySelector`: Prioriza alvos cognitivos baseando-se em `CRITICAL > HIGH > NORMAL > LOW`. Local: [`aletheia/cognition/runtime/selector.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/runtime/selector.py).
* `CapabilityRuntime`: Orquestra o ciclo de step, gerencia especialistas e aplica os resultados no workspace. Local: [`aletheia/cognition/runtime/runtime.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/runtime/runtime.py).

---

## 7. Fronteira de Segurança Cognitiva de LLM (LLM Security Boundary)

### 7.1. `aletheia.cognition.adapters.llm.schemas`
* **Responsabilidade**: Schemas Pydantic intermediários (`LLMCritiquePayload`, `LLMArgumentProposal`, `LLMUnknownProposal`).
* **Localização**: [`aletheia/cognition/adapters/llm/schemas.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/adapters/llm/schemas.py)

### 7.2. `aletheia.cognition.adapters.llm.serializer`
* **Responsabilidade**: `ProjectionPromptSerializer`: Demarcação textual estrita entre dados proposicionais e instruções, prevenindo prompt injection.
* **Localização**: [`aletheia/cognition/adapters/llm/serializer.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/adapters/llm/serializer.py)

### 7.3. `aletheia.cognition.adapters.llm.structural_validator`
* **Responsabilidade**: `StructuralValidator`: Inspeciona IDs de alvos e premissas citadas contra a projeção autorizada, purga alucinações e calcula a métrica RHR (*Referential Hallucination Rate*).
* **Localização**: [`aletheia/cognition/adapters/llm/structural_validator.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/adapters/llm/structural_validator.py)

### 7.4. `aletheia.cognition.adapters.llm.epistemic_validator`
* **Responsabilidade**: `EpistemicValidator`: Valida resistência a injeção adversarial, calcula CGR (*Claim Grounding Rate*), audita a profundidade crítica (escala 0 a 5) e desacopla a confiança autodeclarada do modelo do suporte epistemológico conferido pelo Kernel (`LOW`, `MEDIUM`, `HIGH`).
* **Localização**: [`aletheia/cognition/adapters/llm/epistemic_validator.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/adapters/llm/epistemic_validator.py)

---

## 8. Interação e Apresentação (Interaction Layer)

### 8.1. `aletheia.interaction.session`
* **Responsabilidade**: Orquestrador de alto nível (`InteractiveSession`) para condução de sessões colaborativas contínuas.
* **Localização**: [`aletheia/interaction/session.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/interaction/session.py)

### 8.2. `aletheia.interactive`
* **Responsabilidade**: Interface de linha de comando com REPL interativo no terminal.
* **Localização**: [`aletheia/interactive.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/interactive.py)
