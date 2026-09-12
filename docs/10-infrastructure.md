# 10 — Infraestrutura e Ambiente Operacional (Infrastructure)

Em estrito cumprimento à regra de auditoria de documentar **exclusivamente a infraestrutura realmente existente** sem inventar suposições:

---

## 1. Inventário de Infraestrutura Real

| Elemento de Infraestrutura | Estado Real | Evidência / Observação |
| :--- | :--- | :--- |
| **Containers (Docker / Podman)** | **INEXISTENTE** | Nenhum `Dockerfile`, `.dockerignore` ou `docker-compose.yml` encontrado na raiz do repositório. |
| **Orquestração (Kubernetes / Helm)** | **INEXISTENTE** | Nenhum manifesto YAML de Pod, Deployment, Service ou Chart Helm. |
| **Infraestrutura como Código (IaC)** | **INEXISTENTE** | Nenhum arquivo Terraform (`.tf`), Pulumi, CloudFormation ou Ansible. |
| **Servidores / Instâncias de Nuvem** | **INEXISTENTE** | Não há vinculação configurada a instâncias AWS (EC2), GCP (Compute Engine) ou Azure. |
| **Rede / Balanceadores de Carga** | **INEXISTENTE** | Não há Nginx, Traefik, ALB ou regras de firewall configuradas no repositório. |
| **Armazenamento Persistente / Volumes**| **INEXISTENTE** | Não há montagem de volumes persistentes, discos EBS ou buckets S3 configurados. |
| **Rotinas de Backup Automatizado** | **INEXISTENTE** | Não há cron jobs, scripts de dump ou rotinas de snapshot agendadas. |
| **Pipelines de CI/CD** | **INEXISTENTE** | O diretório `.github/workflows/` **não existe** (*FATO*). Não há pipelines de integração contínua configurados no GitLab CI, CircleCI ou GitHub Actions. |

---

## 2. Ambiente de Execução Concreto

O sistema é atualmente executado **diretamente no ambiente do host do desenvolvedor** com a seguinte configuração:

* **Sistema Operacional**: Linux x86_64 (Kernel 6.13+ com suporte a Btrfs).
* **Runtime**: CPython 3.14.7.
* **Ambiente Virtual**: Diretório local `.venv/` contendo o binário do interpretador Python e as bibliotecas compiladas.
* **Dependências de Build**: `hatchling` (backend de compilação PEP 517/518 declarado em `pyproject.toml`).
* **Dependências de Runtime Instaladas**:
  * `pydantic` (versão 2.13.5)
  * `pydantic_core` (versão 2.46.5)
  * `typing_extensions` (versão 4.16.0)
  * `typing-inspection` (versão 0.4.4)
  * `annotated-types` (versão 0.8.0)
* **Dependências de Desenvolvimento Instaladas**:
  * `pytest` (versão 9.1.1)
  * `pluggy` (versão 1.6.0)
  * `iniconfig` (versão 2.3.0)
  * `packaging` (versão 26.3)
  * `Pygments` (versão 2.21.0)

---

## 3. Gestão de Recuperação e Rollback

O único mecanismo de recuperação disponível no código é a reconstituição em memória baseada em eventos (`Event Sourcing Replay`):
* Se uma lista de instâncias de `CognitiveEvent` for mantida em memória ou reinjetada via código, a função `CognitiveWorkspace.replay(events)` reconstitui o grafo de forma idêntica.
* **Limitação Operacional**: Como não há escrita em disco do stream de eventos, não há suporte a recuperação após encerramento do processo (`process kill` ou reinicialização da máquina).
