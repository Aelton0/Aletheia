# 08 — Avaliação de Observabilidade e Diagnóstico (Observability)

A observabilidade é a capacidade de inferir o estado interno de um sistema a partir de suas saídas externas (logs, métricas, rastreamentos e eventos).

---

## 1. Auditoria dos Pilares de Observabilidade

| Pilar | Estado Atual | Evidência no Código | Avaliação |
| :--- | :--- | :--- | :--- |
| **Logs Estruturados** | **INEXISTENTE** | Zero ocorrências de `import logging`, `structlog` ou bibliotecas similares em todo o pacote `aletheia`. Apenas instruções `print()` na CLI interativa. | **CRÍTICO** |
| **Métricas Operacionais** | **INEXISTENTE** | Não há coletores de métricas (`prometheus_client`, `statsd`), medidores de latência por endpoint, contadores de erros ou medidores de saturação de fila. | **ALTO** |
| **Rastreamento Distribuído (Tracing)** | **INEXISTENTE** | Não há suporte a OpenTelemetry, W3C TraceContext ou spans correlacionados entre chamadas e passos de raciocínio. | **MÉDIO** |
| **Health Checks / Probes** | **INEXISTENTE** | Não há endpoints ou funções para sondagem de vitalidade (*liveness*) ou prontidão (*readiness*). | **MÉDIO** |
| **Alertas & Dashboards** | **INEXISTENTE** | Nenhuma integração de alerta para falhas de validação de CDR, rejeições de injeção cognitiva ou suspensões anômalas em cascata. | **MÉDIO** |

---

## 2. Telemetria e Auditoria Existentes no Código

Embora não existam bibliotecas formais de observabilidade, o sistema implementa primitivos conceituais ricos em suas estruturas de dados:

1. **Proveniência Temporal e Autoral nas Entidades**:
   * Toda entidade herda de `CognitiveEntity`, contendo:
     * `id: str`: Identificador unívoco com prefixo semântico (ex: `claim_`, `alt_`, `cdr_`).
     * `created_at: datetime`: Carimbo de data/hora em UTC gerado na instanciação.
     * `metadata: Dict[str, Any]`: Dicionário aberto para metadados contextuais.
2. **Log Imutável de Eventos (`CognitiveEvent`)**:
   * O `InMemoryEventStore` registra atomicamente cada mutação com `event_id`, `timestamp` (UTC), `actor_id`, `event_type` e `payload`.
   * Permite reconstruir o histórico exato de quem fez o que e em qual sequência cronológica.
3. **Metadados de Resposta Probabilística (`LLMResponse`)**:
   * A porta de LLM prevê `usage` (contagem de tokens), `latency_ms` (tempo de resposta medido via `time.perf_counter()`) e `raw_response_hash` (hash SHA-256 da resposta bruta).
   * As entidades geradas pela `LLMCritiqueCapability` gravam em seus metadados o nome do modelo (`model`), confiança do modelo (`model_confidence`), suporte epistêmico conferido (`epistemic_support`), profundidade crítica (`critical_depth_assessed`) e taxa de alucinação (`rhr_score`).

---

## 3. Diagnóstico de Falhas: "Se este sistema quebrar agora, conseguimos descobrir o motivo?"

### Resposta: **CAPACIDADE DE DIAGNÓSTICO BAIXA (Low)**

* **No REPL do Terminal (`interactive.py`)**:
  * Erros inesperados são capturados pelo bloco `except Exception as e:` na linha 184 e exibidos como mensagem simplificada (`❌ Erro operacional: {e}`), sem stacktrace completa nem identificador de correlação.
* **Na Execução como Biblioteca / Background**:
  * Se o Aletheia for importado por outro serviço, qualquer falha não capturada gerará uma exceção Python não estruturada. Não há registro em arquivo de log, syslog ou stream JSON.
* **Diagnóstico Lógico de Conflitos e Invalidações**:
  * Para entender por que uma alternativa foi suspensa, é necessário inspecionar manualmente as arestas do grafo e os status dos nós dependentes através do `CognitiveSynthesizer.inspect_dependencies(graph, alt_id)`. Não há eventos de log ou emissão de alertas automáticos quando nós entram em suspensão.
