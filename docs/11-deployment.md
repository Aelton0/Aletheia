# 11 — Processo de Implantação e Empacotamento (Deployment)

---

## 1. Ambientes Operacionais Existentes

Seguindo a regra de auditoria de registrar somente os ambientes comprovadamente existentes:

```text
Development (Workstation Local do Desenvolvedor)
    ↓
[Testing / Staging: INEXISTENTE]
    ↓
[Production: INEXISTENTE]
```

* **Development**: Único ambiente existente. Opera no sistema operacional local Linux do autor (`Aelton0`), utilizando o ambiente virtual Python `.venv`.
* **Testing / CI**: Não há ambiente de CI automatizado em nuvem. Os testes são rodados manualmente pelo desenvolvedor através do terminal.
* **Staging / Homologação**: Inexistente.
* **Production**: Inexistente.

---

## 2. Empacotamento e Distribuição

O projeto utiliza o padrão moderno de empacotamento Python baseado no `pyproject.toml` com o backend `hatchling.build`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "aletheia"
version = "0.1.0"
description = "Aletheia: Sistema de Cognição Colaborativa Humano-IA"
readme = "README.md"
requires-python = ">=3.11"
authors = [
    { name = "Aelton", email = "aelton@example.com" }
]
dependencies = [
    "pydantic>=2.0.0"
]
```

### Inconsistência Crítica de Empacotamento:
> **DOCUMENTAÇÃO ≠ IMPLEMENTAÇÃO**
>
> O arquivo `pyproject.toml` declara explicitamente na linha 9: `readme = "README.md"`.
> No entanto, o arquivo `README.md` **não existe no repositório** (*FATO* comprovado por listagem de diretório).
> **Impacto**: Qualquer tentativa de construir o pacote (`python -m build`) ou instalá-lo em modo editável/distribuível (`pip install .`) falhará imediatamente com erro de arquivo não encontrado (`FileNotFoundError: README.md`).

---

## 3. Procedimentos Operacionais Locais (Runbook)

Para executar o sistema no ambiente atual:

### 3.1. Execução dos Testes Automatizados
```bash
.venv/bin/pytest -v
```
Executa a suíte de 25 testes em ~0.12 segundos.

### 3.2. Execução do Benchmark Canônico (M3)
```bash
.venv/bin/python benchmarks/run_benchmark.py
```
Executa a comparação determinística vs LLM-backed nos 10 cenários e imprime a tabela consolidada de RHR, CGR e profundidade crítica.

### 3.3. Execução do Cenário Guiado de Demonstração
```bash
.venv/bin/python demo_scenario.py
```
Executa o fluxo de 10 passos do Milestone 1 no terminal.

### 3.4. Inicialização do Terminal Interativo (CLI REPL)
```bash
.venv/bin/python aletheia/interactive.py
```
Inicia o loop interativo da sessão cognitiva. Digite `/exit` para encerrar.
