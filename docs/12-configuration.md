# 12 — Gestão de Configuração e Parâmetros (Configuration)

---

## 1. Arquivos de Configuração

O único arquivo formal de configuração existente no repositório é o [`pyproject.toml`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/pyproject.toml):
* Define configurações do sistema de build (`[build-system]`).
* Define metadados do projeto e dependências mínimas (`[project]`).
* Define dependências de desenvolvimento opcionais (`[project.optional-dependencies]`).
* Define configurações de descoberta de testes para o pytest (`[tool.pytest.ini_options]`).

---

## 2. Variáveis de Ambiente

* **FATO**: Não há **nenhuma leitura de variáveis de ambiente** em todo o código-fonte da aplicação (`aletheia`). Nem `os.environ` nem `os.getenv` são utilizados.
* Não há arquivos `.env`, `.env.example`, `.env.test` ou `.env.production`.
* Não há biblioteca de carregamento de ambiente (como `python-dotenv` ou `pydantic-settings`).

---

## 3. Parâmetros Operacionais e "Magic Numbers" Hardcoded

Como não há sistema centralizado de configuração, diversos parâmetros operacionais críticos estão fixados no código-fonte como valores padrão (*hardcoded*):

| Parâmetro / Valor | Localização no Código | Impacto Operacional |
| :--- | :--- | :--- |
| `safety_limit: int = 5` | [`runtime.py:L143`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/runtime/runtime.py#L143), [`session.py:L213`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/interaction/session.py#L213) | Limite máximo de ciclos autônomos no loop `run_policy`. Fixado em 5 steps; não configurável via arquivo. |
| `temperature: float = 0.0` | [`llm_port.py:L34`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/ports/llm_port.py#L34), [`llm_critique.py:L84`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/capabilities/llm_critique.py#L84) | Temperatura de amostragem do LLM fixada em 0.0 (determinismo máximo para análise crítica). |
| `weight = 1.5` | [`critique.py:L106`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/capabilities/critique.py#L106) | Peso atribuído ao argumento contrário gerado pela capacidade de crítica determinística. |
| `weight = 1.2` | [`llm_critique.py:L123`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/capabilities/llm_critique.py#L123) | Peso atribuído ao argumento contrário gerado pelo LLM. |
| `min_length = 3` | [`decision.py:L40`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/core/entities/decision.py#L40), [`cdr.py:L18`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/deliberation/cdr.py#L18) | Tamanho mínimo de caracteres para validação do `decision_scope`. |
| `INJECTION_PATTERNS` | [`epistemic_validator.py:L44-51`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/adapters/llm/epistemic_validator.py#L44-L51) | Lista de 6 strings estáticas para filtragem de injeção em texto de LLM. |
| `PRIORITY_ORDER` | [`selector.py:L12-17`](file:///home/Aelton0/Dev/Projeto%20AGI/Aletheia/aletheia/cognition/runtime/selector.py#L12-L17) | Mapeamento estático de prioridade: CRITICAL (0), HIGH (1), NORMAL (2), LOW (3). |
