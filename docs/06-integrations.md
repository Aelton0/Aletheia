# 06 — Mapa de Integrações Externas (Integrations)

Este documento audita todas as integrações externas existentes, contratos de fornecedores e lacunas de conectividade do sistema Aletheia.

---

## 1. Mapeamento de Integrações Reais

| Integração / Serviço | Tipo | Status de Implementação | Localização no Código | Observação Técnica |
| :--- | :--- | :--- | :--- | :--- |
| **Provedores de LLM** | Porta Hexagonal (`LLMProviderPort`) | **PARCIAL (MOCK ONLY)** | [`aletheia/ports/llm_port.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/ports/llm_port.py), [`aletheia/adapters/mock_llm_adapter.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/adapters/mock_llm_adapter.py) | Existe a porta abstrata e o mock determinístico. Nenhum provedor real de API (OpenAI, Anthropic, Gemini, Ollama) está implementado. |
| **Bancos de Dados Relacionais / NoSQL** | Persistência externa | **INEXISTENTE** | N/A | Nenhum driver instalado (`psycopg2`, `asyncpg`, `sqlite3`, `pymongo`). |
| **Bancos Vetoriais / Índices Semânticos** | Busca vetorial | **INEXISTENTE** | N/A | Nenhum cliente de busca vetorial (`qdrant-client`, `pinecone`, `chromadb`, `faiss`). |
| **Filas / Mensageria** | Barramento distribuído | **INEXISTENTE** | N/A | O barramento é um pub/sub síncrono em memória Python puro (`EventBus`). Sem Kafka, RabbitMQ, Redis. |
| **Armazenamento de Objetos / Nuvem** | Arquivos externos | **INEXISTENTE** | N/A | Nenhum SDK de nuvem (`boto3`, `google-cloud-storage`, `azure-storage`). |
| **Sistemas de Identidade / Auth** | SSO / OAuth | **INEXISTENTE** | N/A | Atores são objetos puramente conceituais no grafo. |

---

## 2. Auditoria da Porta de LLM (`LLMProviderPort`)

O contrato formal de integração com Modelos de Linguagem Probabilísticos está especificado em [`aletheia/ports/llm_port.py`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/ports/llm_port.py):

```python
class LLMResponse(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    parsed_output: Any
    model: str
    provider: str
    usage: Dict[str, int] = Field(default_factory=dict)
    latency_ms: float
    finish_reason: Optional[str] = None
    request_id: Optional[str] = None
    raw_response_hash: Optional[str] = None


class LLMProviderPort(ABC):
    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_schema: Type[BaseModel],
        system_instruction: Optional[str] = None,
        temperature: float = 0.0,
    ) -> LLMResponse:
        pass
```

### 2.1. Pontos Fortes do Design da Porta:
1. **Tipagem Estrita com Schemas Pydantic**: A porta exige um `response_schema: Type[BaseModel]`, forçando que qualquer provedor real utilize capacidades de *Structured Outputs* (ex: OpenAI Structured Outputs via `response_format`, Gemini `response_schema` ou Pydantic-based validation).
2. **Auditoria de Custo e Latência**: `LLMResponse` já prevê campos de observabilidade para consumo de tokens (`usage`), latência (`latency_ms`) e hash criptográfico da resposta original (`raw_response_hash`).

### 2.2. Lacunas e Riscos da Porta:
1. **Ausência de Suporte Assíncrono (`async/await`)**: O método `generate_structured` é estritamente síncrono/bloqueante. Quando um adaptador real de rede (ex: OpenAI API ou Gemini API) for conectado, cada chamada de inferência (que leva tipicamente de 500ms a 5000ms) bloqueará a thread inteira do Python, impedindo qualquer concorrência.
2. **Falta de Políticas de Resiliência (Timeout, Retry, Circuit Breaker)**: O contrato da porta não aceita parâmetros de timeout nem especifica exceções tipadas de rede (`ProviderTimeoutError`, `RateLimitExceededError`, `AuthenticationError`), transferindo a responsabilidade do tratamento para o chamador.
