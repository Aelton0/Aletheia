# 16 — Relatório Consolidado de Auditoria Técnica (Audit Report)

**Projeto**: Aletheia: Sistema de Cognição Colaborativa Humano-IA  
**Data da Auditoria**: 12 de Setembro de 2026  
**Commit Analisado**: `e0b1978` (`feat(llm): implement LLM capability adapter, two-stage cognitive security boundary, and canonical benchmark (Milestone 3)`)  
**Papel do Auditor**: Arquiteto de Software Sênior, Auditor Técnico e Documentador de Sistemas  
**Marco Auditado**: **M3 ← LLM Capability** (em um programa mestre de 11 Milestones: M0 a M10)

---

## Contexto Estratégico do Roadmap (M0 a M10)

A auditoria esclarece que o sistema existente **não é a versão final do Aletheia**, mas sim a consolidação dos primeiros 4 marcos fundacionais de um roadmap estratégico composto por 11 etapas:

* `M0 ✅ Cognitive Kernel`: Núcleo ontológico, Event Sourcing e TMS.
* `M1 ✅ Interactive Workspace`: Sessão interativa Humano-IA e ratificação de CDRs.
* `M2 ✅ Capability Runtime`: Contratos de capacidades, isolamento e runtime consultivo.
* `M3 ← LLM Capability (ESTÁGIO ATUAL AUDITADO)`: Fronteira de segurança e benchmark canônico.
* `M4    Deliberation multi-capability`: Debate e deliberação entre múltiplos especialistas.
* `M5    Knowledge / RAG`: Integração do cofre de conhecimento (`Aletheia-Knowledge`).
* `M6    Memory`: Memória de longo prazo (episódica, semântica, procedimental).
* `M7    Learning`: Aprendizado e destilação de lições (já scaffoldado em `aletheia.core.entities.experience`).
* `M8    Tools / Action`: Execução de ferramentas e ações no mundo real.
* `M9    Cognitive Architecture`: Arquitetura cognitiva integrada de iniciativa mista.
* `M10   Unified Intelligence`: Inteligência unificada de colaboração simbiótica.

Essa contextualização explica por que primitivos como `Action`, `Outcome`, `EpistemicDelta` e `Lesson` já existem no núcleo (`aletheia.core.entities.experience`) e por que o repositório paralelo `Aletheia-Knowledge` já contém taxonomias e papers como o *CascadeDebate*.

---

## 1. Matriz de Confiança da Auditoria

Esta matriz qualifica o grau de certeza das conclusões deste relatório com base na solidez das evidências encontradas diretamente no código-fonte, testes e configurações:

| Área Auditada | Estado Atual | Confiança | Observação / Evidência Principal |
| :--- | :--- | :--- | :--- |
| **Arquitetura** | Reconstruída | **ALTA** | Estrutura limpa de 4 camadas (Hexagonal + Event Sourcing + Blackboard) comprovada em código e testes. |
| **Domínio & Ontologia** | Mapeado | **ALTA** | Entidades Pydantic ricas e com contratos de validação estritos (`aletheia/core/entities/`). |
| **Persistência / Banco** | Efêmero (In-Memory) | **ALTA** | Comprovada ausência de banco físico; operando em dicionários e listas Python puras. |
| **APIs e Interfaces** | Programática & CLI | **ALTA** | Inspecionados integralmente `InteractiveSession` e o REPL `interactive.py`. Ausência de HTTP/REST confirmada. |
| **Segurança Cognitiva** | Dois Estágios | **ALTA** | Código de `StructuralValidator` e `EpistemicValidator` auditado em detalhes, incluindo testes adversariais. |
| **Segurança Operacional** | Ausente | **ALTA** | Comprovada ausência de autenticação de atores, tokens de sessão e controle de acesso a chamadas de API. |
| **Infraestrutura & Deploy**| Local Dev Only | **ALTA** | Confirmada ausência de Docker, Kubernetes, CI/CD e ausência do arquivo `README.md` declarado no `pyproject.toml`. |
| **Testes & Benchmarks** | Concluídos (25/25) | **ALTA** | Suíte pytest executada localmente em 0.12s e benchmark dos 10 cenários canônicos verificado. |
| **Observabilidade** | Incipiente | **ALTA** | Confirmada ausência total de bibliotecas de logging (`import logging`), métricas ou traces. |

---

## 2. Inventário de Incertezas ("O que ainda não sabemos")

Seguindo a regra de não inventar informações ou preencher lacunas com suposições:

### Item 1: Qual o provedor de LLM pretendido para a primeira integração real em produção?
* **Pergunta**: A equipe planeja integrar prioritariamente modelos comerciais em nuvem (ex: OpenAI GPT-4o, Anthropic Claude 3.5 Sonnet, Google Gemini 2.0) ou modelos locais abertos (ex: Llama 3 via Ollama/vLLM)?
* **Por que não sabemos**: O repositório contém apenas a porta abstrata `LLMProviderPort` e o `MockLLMAdapter`. Não há menções a fornecedores específicos em comentários ou configurações. O único PDF na pasta de pesquisa `Aletheia-Knowledge` trata de *CascadeDebate* para cascatas de LLMs, mas não declara o fornecedor prioritário.
* **Qual evidência seria necessária**: Um ADR formal, issue de roadmap ou arquivo de configuração especificando o provedor e SDK alvo.
* **Impacto de permanecer desconhecido**: Risco de implementar um adaptador assíncrono para nuvem quando a intenção do usuário poderia ser execução offline em hardware local (ou vice-versa).

### Item 2: Qual a estratégia pretendida de persistência definitiva em disco?
* **Pergunta**: A persistência durável pretendida para o Event Store e Grafo será baseada em arquivos planos locais (ex: SQLite com FTS5 + JSONL) ou em banco cliente-servidor dedicado (ex: PostgreSQL com pgvector ou Neo4j)?
* **Por que não sabemos**: No script `demo_scenario.py`, o cenário simula a deliberação onde o SQLite local é escolhido como alternativa vencedora, mas no código de produção do Kernel ainda existem apenas os adaptadores em memória.
* **Qual evidência seria necessária**: Definição explícita no roadmap de arquitetura ou início de implementação de um adaptador de persistência concreto.
* **Impacto de permanecer desconhecido**: Dependência contínua de persistência efêmera em RAM com risco total de perda de dados.

### Item 3: Qual é o modelo pretendido de autenticação para os atores soberanos?
* **Pergunta**: Em ambiente multi-usuário ou exposto à rede, como o sistema garantirá que o `actor_id` de uma requisição pertence genuinamente a um humano com autoridade de veto?
* **Por que não sabemos**: O modelo de entidades prevê o atributo `has_veto_power: bool = True`, mas não há lógica de autenticação de credenciais, certificados mTLS ou assinaturas digitais.
* **Qual evidência seria necessária**: Especificação de segurança ou modelo de identidade planejado.
* **Impacto de permanecer desconhecido**: Falsificação trivial de identidade por agentes ou chamadas de código não autorizadas.

---

## 3. Principais Divergências: DOCUMENTAÇÃO ≠ IMPLEMENTAÇÃO

1. **`pyproject.toml` referencia `README.md` inexistente**:
   * *Declaração*: `readme = "README.md"` em `pyproject.toml:L9`.
   * *Realidade*: `README.md` não existe na raiz do repositório.
   * *Status*: `DOCUMENTAÇÃO ≠ IMPLEMENTAÇÃO` (Impede o build do pacote).
2. **`AGENTS.md` vazio**:
   * *Declaração*: Arquivo `AGENTS.md` criado no commit `ba315a2`.
   * *Realidade*: Arquivo possui 0 bytes de conteúdo.
   * *Status*: `DOCUMENTAÇÃO ≠ IMPLEMENTAÇÃO`.
3. **Blackboard Global vs Importação Direta de Cognição no Core**:
   * *Declaração Arquitetural*: O Core deve ser agnóstico e constituir a fundação neutra sobre a qual a Cognição opera.
   * *Realidade*: `aletheia.core.context.workspace` importa funções diretamente de `aletheia.cognition.deliberation.cdr` e `aletheia.cognition.epistemic.tms`.
   * *Status*: `DOCUMENTAÇÃO ≠ IMPLEMENTAÇÃO`.

---

## 4. Priorização de Recomendações Futuras

Aplicando a regra estrita contra *overengineering* (não recomendar Kubernetes, Kafka, microsserviços ou novas dependências complexas sem problema real):

### P0 — Necessário antes de continuar (Integridade e Funcionamento)
1. **[REC-01] Criar o arquivo `README.md` na raiz do projeto**:
   * *Problema Real Resolvido*: Corrige o erro imediato de build do `hatchling` e documenta as instruções essenciais de execução para outros desenvolvedores.
2. **[REC-02] Implementar adaptador mínimo de persistência em disco para o Event Store (`FileEventStoreAdapter` ou `SQLiteEventStoreAdapter`)**:
   * *Problema Real Resolvido*: Elimina o risco de perda total de dados a cada reinício do processo (RSK-01 / TD-01). Como o Aletheia já possui o método `replay(events)` 100% testado e funcional, basta salvar os eventos em um arquivo JSONL sequencial em disco para garantir durabilidade total com mínimo código.

### P1 — Deve ser resolvido (Qualidade e Segurança)
3. **[REC-03] Adicionar biblioteca padrão de logging (`logging`) nos pontos críticos**:
   * *Problema Real Resolvido*: Elimina a cegueira diagnóstica fora do console interativo, registrando eventos de publicação do bus, passos de execução de capacidades e decisões de segurança do validador epistêmico.
4. **[REC-04] Robustecer a validação contra prompt injection no `EpistemicValidator`**:
   * *Problema Real Resolvido*: Substituir a lista estática de 6 strings por verificação estrutural e tipagem rígida, impedindo contorno trivial de segurança por sinônimos ou outros idiomas.
5. **[REC-05] Desacoplar `workspace.py` do módulo `cognition`**:
   * *Problema Real Resolvido*: Elimina o acoplamento cíclico/indevido entre Core e Cognition através de injeção de dependências no construtor.

### P2 — Melhoria importante (Escalabilidade e Conectividade)
6. **[REC-06] Implementar o primeiro adaptador real de LLM (`LLMProviderPort`) com suporte a `async/await`**:
   * *Problema Real Resolvido*: Permite que o Aletheia seja testado com modelos de linguagem de ponta reais (ex: Claude 3.5 Sonnet ou Gemini 2.0) sem bloquear a execução síncrona da thread local.
7. **[REC-07] Adicionar ferramenta de medição de cobertura de testes (`pytest-cov`)**:
   * *Problema Real Resolvido*: Permitir que o time meça com precisão quais linhas de código estão ou não cobertas por testes automatizados.

### P3 — Melhoria futura (Otimizações de Longo Prazo)
8. **[REC-08] Mecanismo de Snapshot Periódico para o Grafo Epistêmico**:
   * *Problema Real Resolvido*: Evita que sessões com mais de 50.000 eventos exijam tempo excessivo de replay ao inicializar.
