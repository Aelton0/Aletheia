# 14 — Matriz e Registro de Riscos Técnicos (Risk Register)

Este documento prioriza os riscos que podem causar perda de dados, vulnerabilidades de segurança, indisponibilidade, corrupção de estado, falhas operacionais ou dificuldade crítica de manutenção.

---

## 1. Matriz de Riscos

| ID | Risco | Evidência | Impacto | Probabilidade | Severidade | Prioridade |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-01** | **Perda Irreversível de Dados por Falta de Persistência em Disco** | [`in_memory_event_store.py:L12`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/adapters/in_memory_event_store.py#L12) | Perda de todo o histórico de deliberações, decisões (CDRs) e premissas a cada reinicialização ou crash. | **ALTA** | **CRÍTICA** | **P0** |
| **RSK-02** | **Falha de Build / Instalação do Pacote por Arquivo Ausente** | [`pyproject.toml:L9`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/pyproject.toml#L9) | `pip install .` e `hatchling build` falham imediatamente procurando `README.md`. | **ALTA** | **ALTA** | **P0** |
| **RSK-03** | **Bypass da Fronteira de Segurança por Prompt Injection Semântico** | [`epistemic_validator.py:L44`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/adapters/llm/epistemic_validator.py#L44) | Injeção de instruções de controle adversariais que utilizam sinônimos ou outros idiomas passa despercebida. | **ALTA** | **ALTA** | **P1** |
| **RSK-04** | **Falsificação de Soberania e Poder de Veto Humano** | [`actors.py:L31-39`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/entities/actors.py#L31-L39) | Qualquer agente de software ou chamada de código pode instanciar `actor_id="human"` e forçar vetos ou ratificações não autorizadas. | **MÉDIA** | **ALTA** | **P1** |
| **RSK-05** | **Bloqueio de Thread e Indisponibilidade Operacional por I/O Síncrono** | [`llm_port.py:L29-37`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/ports/llm_port.py#L29-L37) | Integrações futuras com provedores de rede (OpenAI/Gemini) bloquearão o processo por 2 a 10 segundos por inferência. | **ALTA** | **MÉDIA** | **P1** |
| **RSK-06** | **Cegueira Operacional por Ausência de Logs Estruturados** | Todo o pacote `aletheia/` | Impossibilidade de investigar a causa raiz de exceções ou anomalias fora do console interativo. | **ALTA** | **MÉDIA** | **P1** |
| **RSK-07** | **Degradação de Desempenho e Esgotamento de Memória por Event Stream Infinito** | [`workspace.py:L226`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/context/workspace.py#L226) | Replays cada vez mais lentos e consumo contínuo de RAM em execuções de longa duração. | **MÉDIA** | **MÉDIA** | **P2** |
| **RSK-08** | **Corrupção de Estado do Grafo sob Concorrência Multithread** | [`in_memory_graph.py:L14`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/adapters/in_memory_graph.py#L14) | Modificações concorrentes sem locks levarão a dicionários inconsistentes ou perda de arestas. | **BAIXA** (monothread) / **ALTA** (se exposto a API web) | **ALTA** | **P2** |

---

## 2. Planos de Mitigação Sugeridos

1. **Para RSK-01 (Perda de Dados)**: Criar um adaptador simples baseado em append-only em arquivo `.jsonl` no disco local (ex: `~/.aletheia/workspace.jsonl`), preservando o replay determinístico.
2. **Para RSK-02 (README Ausente)**: Criar `README.md` na raiz do projeto com apresentação técnica e guia de execução.
3. **Para RSK-03 (Bypass de Segurança)**: Robustecer o `EpistemicValidator` para verificar tokens demarcados e rejeitar estruturas sintáticas imperativas fora dos tipos Pydantic esperados.
4. **Para RSK-04 (Autenticação)**: Adicionar camada de assinatura criptográfica (ex: HMAC ou par de chaves assimétricas) nos eventos originados por atores humanos.
5. **Para RSK-05 (Bloqueio Síncrono)**: Planejar a migração das portas de I/O para `async/await` com timeouts configuráveis.
