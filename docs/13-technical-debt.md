# 13 — Registro de Dívida Técnica (Technical Debt)

Este documento registra os itens de dívida técnica explícita e implícita identificados durante a auditoria de código do Aletheia.

---

### TD-01: Inexistência de Persistência em Disco (Volatilidade Total)
* **ID**: TD-01
* **Descrição**: O sistema opera 100% em memória RAM (`InMemoryGraphAdapter` e `InMemoryEventStore`). Não há nenhum adaptador de persistência física em disco, arquivo JSONL ou banco de dados relacional.
* **Local**: [`aletheia/adapters/in_memory_graph.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/adapters/in_memory_graph.py), [`aletheia/adapters/in_memory_event_store.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/adapters/in_memory_event_store.py)
* **Evidência**: O `EventStorePort` e `GraphStoragePort` possuem apenas implementações `InMemory*`. Ao encerrar o processo Python, todo o grafo e histórico de eventos são perdidos.
* **Impacto**: Impossibilidade de retomar deliberações anteriores ou persistir decisões entre sessões. Perda permanente de dados em caso de crash.
* **Probabilidade**: ALTA (100% dos reinícios perdem o estado).
* **Severidade**: CRÍTICA.
* **Motivo**: Foco deliberado nas fases M0–M3 em estabilizar a semântica epistêmica e os contratos antes de escolher o mecanismo de banco de dados.
* **Recomendação**: Implementar um `FileEventStoreAdapter` (armazenamento append-only em arquivo `.jsonl`) ou um `SQLiteEventStoreAdapter` antes de qualquer uso em ambiente real.
* **Prioridade**: **P0 (Crítico / Bloqueante para evolução)**.

---

### TD-02: Inconsistência de Empacotamento (`README.md` ausente)
* **ID**: TD-02
* **Descrição**: `pyproject.toml` referencia `readme = "README.md"`, porém o arquivo não existe na raiz do projeto.
* **Local**: [`pyproject.toml:L9`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/pyproject.toml#L9)
* **Evidência**: `ls README.md` retorna erro 2. Execuções de `python -m build` ou `pip install -e .` falham com `FileNotFoundError`.
* **Impacto**: Falha imediata no processo de build e empacotamento do pacote Python.
* **Probabilidade**: ALTA (100% dos builds).
* **Severidade**: ALTA.
* **Motivo**: Omissão durante a inicialização do repositório.
* **Recomendação**: Criar o arquivo `README.md` na raiz com a documentação do projeto ou ajustar o `pyproject.toml`.
* **Prioridade**: **P0 (Crítico / Bloqueante para empacotamento)**.

---

### TD-03: Detecção de Prompt Injection Baseada em Lista Estática de Strings
* **ID**: TD-03
* **Descrição**: O `EpistemicValidator` utiliza uma lista estática de 6 strings em minúsculo (`INJECTION_PATTERNS`) para detectar injeção de prompt no texto retornado pelo LLM.
* **Local**: [`aletheia/cognition/adapters/llm/epistemic_validator.py:L44-51`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/adapters/llm/epistemic_validator.py#L44-L51)
* **Evidência**:
  ```python
  INJECTION_PATTERNS = [
      "ignore todas as regras",
      "ignore all rules",
      "ignore previous instructions",
      "declare esta solucao como correta",
      "declare this solution as the only",
      "system prompt override",
  ]
  ```
* **Impacto**: Falsa sensação de segurança. Qualquer variação linguística simples (ex: "desconsidere as diretrizes prévias", "ignore as restrições", sinônimos ou outros idiomas) contorna o validador.
* **Probabilidade**: ALTA.
* **Severidade**: ALTA.
* **Motivo**: Implementação preliminar como prova de conceito para validar a fronteira de segurança no M3.
* **Recomendação**: Substituir a lista estática por um classificador semântico de intenção ou validação formal de tokens contra as instruções do sistema, mantendo a demarcação estrita de dados como primeira barreira.
* **Prioridade**: **P1 (Deve ser resolvido)**.

---

### TD-04: Acoplamento Indevido do Core com Módulo de Cognição e Adaptadores
* **ID**: TD-04
* **Descrição**: O `CognitiveWorkspace` importa diretamente adaptadores concretos em memória e funções de validação do módulo superior `aletheia.cognition`.
* **Local**: [`aletheia/core/context/workspace.py:L4-8`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/context/workspace.py#L4-L8)
* **Evidência**:
  ```python
  from aletheia.adapters.in_memory_event_store import InMemoryEventStore
  from aletheia.adapters.in_memory_graph import InMemoryGraphAdapter
  from aletheia.cognition.deliberation.cdr import validate_cdr_integrity
  from aletheia.cognition.epistemic.conflicts import register_contradiction
  from aletheia.cognition.epistemic.tms import challenge_claim, invalidate_claim
  ```
* **Impacto**: Viola a inversão de dependência da Arquitetura Hexagonal. O Core depende da camada de Cognição e dos Adaptadores de Infraestrutura, dificultando testes isolados e substituição de adaptadores.
* **Probabilidade**: MÉDIA.
* **Severidade**: MÉDIA.
* **Motivo**: Conveniência durante a prototipagem rápida dos Milestones 0 e 1.
* **Recomendação**: Injetar as dependências via construtor ou fábrica (`factory`) sem imports concretos no cabeçalho do `workspace.py`.
* **Prioridade**: **P1 (Deve ser resolvido)**.

---

### TD-05: Inexistência de Logs Estruturados e Métricas Operacionais
* **ID**: TD-05
* **Descrição**: O projeto não utiliza nenhuma biblioteca de logging padronizada (`logging`, `structlog`).
* **Local**: Todo o pacote `aletheia/`.
* **Evidência**: Zero chamadas de log em 100% dos arquivos Python da biblioteca.
* **Impacto**: Dificuldade extrema de depuração e auditoria de erros fora do console interativo do desenvolvedor.
* **Probabilidade**: ALTA.
* **Severidade**: MÉDIA.
* **Motivo**: Projeto concebido inicialmente como biblioteca algorítmica pura.
* **Recomendação**: Adicionar módulo de logging padrão (`logging.getLogger("aletheia")`) em eventos do barramento, passos do runtime e validações de segurança.
* **Prioridade**: **P1 (Deve ser resolvido)**.

---

### TD-06: Ausência de Provedores Reais de LLM
* **ID**: TD-06
* **Descrição**: O único adaptador funcional para `LLMProviderPort` é o `MockLLMAdapter`. Não existem adaptadores para OpenAI, Google Gemini, Anthropic ou Ollama.
* **Local**: [`aletheia/adapters/mock_llm_adapter.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/adapters/mock_llm_adapter.py)
* **Evidência**: Nenhum cliente de API de terceiros instalado nas dependências.
* **Impacto**: O sistema só é capaz de realizar críticas avançadas com respostas mockadas/fixtures em ambiente de laboratório.
* **Probabilidade**: ALTA.
* **Severidade**: MÉDIA.
* **Motivo**: O Milestone 3 focou em definir e validar os contratos e as fronteiras de segurança antes da integração de rede real.
* **Recomendação**: Implementar um adaptador concreto (ex: `OpenAILLMAdapter` ou `GeminiLLMAdapter`) utilizando Structured Outputs e mapeamento seguro de schemas.
* **Prioridade**: **P2 (Melhoria importante)**.

---

### TD-07: Execução Estritamente Síncrona / Bloqueante
* **ID**: TD-07
* **Descrição**: Os métodos `step()`, `generate_structured()` e `publish()` são 100% síncronos.
* **Local**: [`aletheia/ports/llm_port.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/ports/llm_port.py), [`aletheia/cognition/runtime/runtime.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/runtime/runtime.py)
* **Evidência**: Nenhuma função `async def` ou uso de `asyncio` em todo o código.
* **Impacto**: Quando forem feitas chamadas de rede reais a LLMs (que levam vários segundos), a thread inteira do Python ficará bloqueada, inviabilizando interfaces responsivas ou processamento paralelo de capacidades.
* **Probabilidade**: ALTA (quando integradas APIs reais).
* **Severidade**: MÉDIA.
* **Motivo**: Simplicidade e determinismo no Milestone 0–2.
* **Recomendação**: Introduzir suporte assíncrono na porta `LLMProviderPort` (`async def generate_structured(...)`) e no `CapabilityRuntime`.
* **Prioridade**: **P2 (Melhoria importante)**.

---

### TD-08: Crescimento Não Delimitado de Memória no `InMemoryEventStore`
* **ID**: TD-08
* **Descrição**: O `InMemoryEventStore` mantém todos os eventos em uma lista Python irrestrita sem suporte a snapshots, particionamento ou compactação.
* **Local**: [`aletheia/adapters/in_memory_event_store.py:L12-15`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/adapters/in_memory_event_store.py#L12-L15)
* **Evidência**: `self._events: List[CognitiveEvent] = []` acumula indefinidamente.
* **Impacto**: Em sessões longas ou com múltiplos ciclos de capacidades, o consumo de RAM cresce linearmente sem teto, além de degradar o tempo de replay.
* **Probabilidade**: BAIXA no uso atual; ALTA em sessões prolongadas.
* **Severidade**: MÉDIA.
* **Motivo**: Estrutura intencionalmente simples para o Milestone 0.
* **Recomendação**: Implementar mecanismo de snapshot periódico do grafo para permitir replays a partir do último snapshot em vez do início absoluto do tempo.
* **Prioridade**: **P3 (Melhoria futura)**.

---

### TD-09: Calibração Empírica e Validação Externa da Rubrica de Profundidade Crítica
* **ID**: TD-09
* **Descrição**: A avaliação de profundidade crítica (escala 0 a 5) no `EpistemicValidator` é baseada em heurísticas textuais por palavras-chave e contagem de campos (ex: menção a "impacto/falha" e presença de `contingency_hypothesis`). O benchmark canônico atual pontua o mock com base nessa regra interna, configurando uma medição autorreferencial.
* **Local**: [`aletheia/cognition/adapters/llm/epistemic_validator.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/adapters/llm/epistemic_validator.py)
* **Evidência**: O `MockLLMAdapter` é estruturado para sempre incluir `contingency_hypothesis`, atingindo a nota máxima 5/5 no próprio validador do sistema sem validação externa.
* **Impacto**: Risco de falsa sensação de superioridade cognitiva da capacidade baseada em LLM sobre a determinística antes de uma aferição qualitativa independente.
* **Probabilidade**: ALTA (se a métrica for interpretada como julgamento semântico real).
* **Severidade**: BAIXA funcionalmente (não corrompe o estado do Kernel), mas ALTA metodologicamente.
* **Motivo**: Necessidade de estabelecer uma primeira métrica ordinal no M3 para validar o fluxo de dados ponta a ponta.
* **Recomendação**: Submeter as críticas geradas por LLM real (TD-06) a avaliação cega anotada por especialistas humanos ou arbitragem por modelo juiz externo calibrado.
* **Prioridade**: **P3 (Melhoria metodológica)**.
