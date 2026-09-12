# 09 — Avaliação da Estratégia de Testes (Testing Assessment)

A auditoria da suíte de testes do Aletheia revela uma disciplina de engenharia incomum para projetos em estágio inicial, com forte ênfase na verificação formal de invariantes matemáticos e cognitivos.

---

## 1. Inventário da Suíte de Testes

* **Framework de Testes**: `pytest` 9.1.1 configurado em [`pyproject.toml`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/pyproject.toml#L23-L27).
* **Tempo de Execução**: ~0.12 segundos para toda a suíte de 25 testes (*FATO*).
* **Taxa de Sucesso**: 100% (25 aprovados, 0 falhas, 0 warnings).

| Arquivo de Teste | Quantidade de Testes | Foco / Invariantes Cobertos | Nível |
| :--- | :--- | :--- | :--- |
| [`test_entities.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/tests/test_entities.py) | 6 | Separação tipo/status; premissas não-vazias em inferências; diferenciação Unknown vs Question; obrigatoriedade de escopo em CDR; delta sem lição; modelo de ator especialista. | Unitário |
| [`test_cascade_suspension.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/tests/test_cascade_suspension.py) | 2 | TMS: Invalidação de premissa propaga `SUSPENDED` em cascata; contestação humana coloca em `UNDER_REVIEW` e suspende dependentes. | Integração |
| [`test_contradiction_policy.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/tests/test_contradiction_policy.py) | 1 | Contradição dialética não auto-invalida; gera status `CONFLICT` e aresta bidirecional `CONTRADICTS`. | Unitário |
| [`test_cdr.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/tests/test_cdr.py) | 3 | Validação de integridade de CDR; preservação de dissidência (`DissentingView`); falha com alternativa inexistente; falha com supersedes inexistente. | Unitário |
| [`test_workspace_and_replay.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/tests/test_workspace_and_replay.py) | 1 | **Milestone 0 Golden Scenario**: Ciclo completo de deliberação e reconstrução determinística de 100% do estado a partir do log de eventos (`Event Replay`). | Integração / E2E |
| [`test_interactive_session.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/tests/test_interactive_session.py) | 1 | **Milestone 1 Golden Scenario**: Sessão interativa em 10 passos (problema, premissas, contestação humana, mudança de foco, interpretação, CDR e replay). | Integração / E2E |
| [`test_projection_and_synthesizer.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/tests/test_projection_and_synthesizer.py) | 2 | Motor de Projeção Contextual: preservação de metas/restrições invariantes e filtragem por saliência de foco; sintetizador detecta suposições ativas e premissas invalidadas. | Unitário / Integração |
| [`test_capability_runtime.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/tests/test_capability_runtime.py) | 3 | **Milestone 2 Golden Scenario**: Cenário em 14 passos do runtime; isolamento adversarial (capacidade não tem acesso ao grafo global); QuestionGenerationCapability. | Integração |
| [`test_llm_security_boundary.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/tests/test_llm_security_boundary.py) | 2 | Validação Estrutural (purga de IDs alucinados pelo LLM); Validação Epistêmica (desacoplamento de confiança e suporte conferido pelo Kernel). | Integração |
| [`test_injection_defense.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/tests/test_injection_defense.py) | 2 | Serializador demarca dados proposicionais de instruções; validador epistêmico rejeita payload contaminado com comandos adversariais. | Integração |
| [`test_anti_invention_benchmark.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/tests/test_anti_invention_benchmark.py) | 1 | Auditoria contra alucinação de variáveis deliberadamente omitidas (modelo deve formular `Unknown` em vez de inventar premissas). | Integração |
| [`test_llm_critique_capability.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/tests/test_llm_critique_capability.py) | 1 | Ciclo ponta a ponta: Workspace $\to$ Analyzer $\to$ Selector $\to$ Projection $\to$ LLMCritique $\to$ Kernel Validation $\to$ Event Store $\to$ Replay. | E2E |

---

## 2. A Suíte Canônica de Benchmarks (M3)

Localizada em [`benchmarks/canonical_scenarios.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/benchmarks/canonical_scenarios.py) e executada via [`benchmarks/run_benchmark.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/benchmarks/run_benchmark.py), a suíte avalia 10 cenários deliberativos divididos em 4 quadrantes:
1. **Técnico (3 cenários)**: Persistência (SQLite vs Nuvem), Arquitetura (Monólito modular vs Microsserviços), Segurança (Sessão Redis vs JWT Stateless).
2. **Negócio / Estratégia (3 cenários)**: Precificação (Assento fixo vs Consumo), Roadmap (Enterprise vs B2C), Canais (PLG vs Vendas Diretas).
3. **Pesquisa Científica (2 cenários)**: Hipótese de Composto Biológico in vivo, Arbitragem de Satélites Conflitantes.
4. **Aprendizagem / Cognição (2 cenários)**: Método de Estudo Espaçado, Currículo Quântico Bottom-Up vs Top-Down.

### Métricas Avaliadas no Benchmark:
* **RHR (*Referential Hallucination Rate*)**: 0.0% (Meta 0.0% mantida nos 10 cenários).
* **CGR (*Claim Grounding Rate*)**: 100.0% (Meta $\ge$ 90% mantida nos 10 cenários).
* **Profundidade Crítica (Rubrica 0-5)**: Média de 3.0/5 para capacidades determinísticas vs 5.0/5 para capacidades impulsionadas por LLM (+67% de profundidade).

---

## 3. Lacunas e Casos Críticos Ausentes nos Testes

Apesar da alta qualidade lógica, foram identificadas as seguintes lacunas de teste:

1. **Ausência de Testes de Concorrência**: Não há testes com execução concorrente de steps ou acessos simultâneos ao `CognitiveWorkspace`.
2. **Ausência de Testes de Carga e Escala**: Todos os testes utilizam grafos minúsculos (2 a 10 nós). Não há testes validando o desempenho do algoritmo de TMS ou de Projeção em grafos com 10.000 ou 100.000 nós.
3. **Ausência de Testes com Provedores Reais de LLM**: Os testes do Milestone 3 utilizam exclusivamente o `MockLLMAdapter`. Não há testes de integração contra APIs reais (OpenAI, Gemini, Claude, Ollama) para verificar comportamento frente a latência de rede, timeouts, JSONs truncados ou variações linguísticas reais de prompt injection.
4. **Falta de Ferramenta de Cobertura de Código**: `pytest-cov` não está configurado no `pyproject.toml`, impedindo a medição precisa da porcentagem de linhas cobertas.
