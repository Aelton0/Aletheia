"""Suíte Canônica de 10 Cenários Deliberativos para Benchmark (M3).

Abrange 4 quadrantes do conhecimento:
- 3 Técnicos (Infraestrutura, Arquitetura, Segurança)
- 3 Negócios/Estratégia (Precificação, Priorização de Produto, Canais de Venda)
- 2 Pesquisa Científica (Hipótese de Fármaco, Arbitragem de Fontes Divergentes)
- 2 Aprendizagem/Cognição (Método de Estudo, Abordagem de Currículo)
"""

from typing import Any, Dict, List
from aletheia.core.context.workspace import CognitiveWorkspace
from aletheia.core.entities import (
    Alternative,
    Claim,
    Constraint,
    EpistemicType,
    Goal,
    HumanActor,
    LifecycleStatus,
)
from aletheia.core.events.schemas import EdgeRelation


def build_scenario_1_tech_persistence() -> CognitiveWorkspace:
    """1. Técnico: SQLite local vs Cluster vetorial gerenciado."""
    ws = CognitiveWorkspace()
    h = HumanActor.create_default("Aelton")
    ws.introduce_entity(h, actor_id=h.id)
    g = Goal(id="g_p1", statement="Definir persistência para assistente pessoal de conhecimento")
    c = Constraint(id="c_p1", statement="Deve operar totalmente offline em laptops comuns")
    ws.introduce_entity(g, actor_id=h.id)
    ws.introduce_entity(c, actor_id=h.id)

    assump = Claim(
        id="assump_p1",
        author_id=h.id,
        statement="A base de conhecimento local não ultrapassará 1GB nos primeiros 12 meses",
        epistemic_type=EpistemicType.ASSUMPTION,
    )
    ws.introduce_entity(assump, actor_id=h.id)

    alt = Alternative(
        id="alt_p1_sqlite",
        title="SQLite Híbrido com FTS5 e Embeddings Quantizados",
        description="Persistência local pura com busca híbrida embarcada",
    )
    ws.introduce_entity(alt, actor_id=h.id)
    ws.connect(alt.id, assump.id, EdgeRelation.DEPENDS_ON, actor_id=h.id)
    ws.connect(alt.id, g.id, EdgeRelation.ADDRESSES, actor_id=h.id)
    return ws


def build_scenario_2_tech_architecture() -> CognitiveWorkspace:
    """2. Técnico: Monólito modular vs Microsserviços."""
    ws = CognitiveWorkspace()
    h = HumanActor.create_default("Aelton")
    ws.introduce_entity(h, actor_id=h.id)
    g = Goal(id="g_p2", statement="Estruturar arquitetura de comunicação para equipe de 3 desenvolvedores")
    ws.introduce_entity(g, actor_id=h.id)

    assump = Claim(
        id="assump_p2",
        author_id=h.id,
        statement="A taxa de implantação diária não exigirá deploys independentes por serviço",
        epistemic_type=EpistemicType.ASSUMPTION,
    )
    ws.introduce_entity(assump, actor_id=h.id)

    alt = Alternative(
        id="alt_p2_mono",
        title="Monólito Modular com Domain-Driven Design",
        description="Único repositório e deploy único com limites de domínio rígidos em código",
    )
    ws.introduce_entity(alt, actor_id=h.id)
    ws.connect(alt.id, assump.id, EdgeRelation.DEPENDS_ON, actor_id=h.id)
    return ws


def build_scenario_3_tech_security() -> CognitiveWorkspace:
    """3. Técnico: Sessões server-side em memória vs JWT Stateless."""
    ws = CognitiveWorkspace()
    h = HumanActor.create_default("Aelton")
    ws.introduce_entity(h, actor_id=h.id)
    g = Goal(id="g_p3", statement="Autenticação segura de usuários com suporte a revogação instantânea")
    ws.introduce_entity(g, actor_id=h.id)

    assump = Claim(
        id="assump_p3",
        author_id=h.id,
        statement="O cluster web terá nós centralizados com acesso a Redis de baixa latência",
        epistemic_type=EpistemicType.ASSUMPTION,
    )
    ws.introduce_entity(assump, actor_id=h.id)

    alt = Alternative(
        id="alt_p3_session",
        title="Sessões Opaque Tokens em Redis",
        description="Identificador de sessão aleatório opaco validado no Redis a cada requisição",
    )
    ws.introduce_entity(alt, actor_id=h.id)
    ws.connect(alt.id, assump.id, EdgeRelation.DEPENDS_ON, actor_id=h.id)
    return ws


def build_scenario_4_biz_pricing() -> CognitiveWorkspace:
    """4. Negócio: Assinatura fixa vs Freemium por consumo."""
    ws = CognitiveWorkspace()
    h = HumanActor.create_default("Aelton")
    ws.introduce_entity(h, actor_id=h.id)
    g = Goal(id="g_p4", statement="Monetização sustentável para software B2B de produtividade")
    ws.introduce_entity(g, actor_id=h.id)

    assump = Claim(
        id="assump_p4",
        author_id=h.id,
        statement="Clientes corporativos preferem previsibilidade orçamentária fixa a faturas variáveis de uso",
        epistemic_type=EpistemicType.ASSUMPTION,
    )
    ws.introduce_entity(assump, actor_id=h.id)

    alt = Alternative(
        id="alt_p4_flat",
        title="Assinatura por Assento Fixo Anual",
        description="Cobrança previsível por assento com contrato de 12 meses",
    )
    ws.introduce_entity(alt, actor_id=h.id)
    ws.connect(alt.id, assump.id, EdgeRelation.DEPENDS_ON, actor_id=h.id)
    return ws


def build_scenario_5_biz_roadmap() -> CognitiveWorkspace:
    """5. Negócio: Retenção B2B Enterprise vs Expansão B2C rápida."""
    ws = CognitiveWorkspace()
    h = HumanActor.create_default("Aelton")
    ws.introduce_entity(h, actor_id=h.id)
    g = Goal(id="g_p5", statement="Alocação de esforço de produto para os próximos 6 meses")
    ws.introduce_entity(g, actor_id=h.id)

    assump = Claim(
        id="assump_p5",
        author_id=h.id,
        statement="A taxa de retenção dos 10 maiores clientes enterprise garante o runway para todo o ano",
        epistemic_type=EpistemicType.ASSUMPTION,
    )
    ws.introduce_entity(assump, actor_id=h.id)

    alt = Alternative(
        id="alt_p5_enterprise",
        title="Foco em Recursos de Segurança e Governança Enterprise",
        description="Desenvolvimento de SSO, auditoria granular e relatórios de conformidade",
    )
    ws.introduce_entity(alt, actor_id=h.id)
    ws.connect(alt.id, assump.id, EdgeRelation.DEPENDS_ON, actor_id=h.id)
    return ws


def build_scenario_6_biz_channels() -> CognitiveWorkspace:
    """6. Negócio: Vendas diretas de alto ticket vs Autosserviço self-service."""
    ws = CognitiveWorkspace()
    h = HumanActor.create_default("Aelton")
    ws.introduce_entity(h, actor_id=h.id)
    g = Goal(id="g_p6", statement="Estratégia de aquisição de clientes com time de vendas reduzido")
    ws.introduce_entity(g, actor_id=h.id)

    assump = Claim(
        id="assump_p6",
        author_id=h.id,
        statement="O produto possui tempo de ativação (Time-to-Value) inferior a 5 minutos sem ajuda humana",
        epistemic_type=EpistemicType.ASSUMPTION,
    )
    ws.introduce_entity(assump, actor_id=h.id)

    alt = Alternative(
        id="alt_p6_plg",
        title="Product-Led Growth (PLG) com Autosserviço",
        description="Onboarding totalmente automatizado via cartão de crédito no navegador",
    )
    ws.introduce_entity(alt, actor_id=h.id)
    ws.connect(alt.id, assump.id, EdgeRelation.DEPENDS_ON, actor_id=h.id)
    return ws


def build_scenario_7_res_hypothesis() -> CognitiveWorkspace:
    """7. Pesquisa: Eficácia de novo composto com dados preliminares."""
    ws = CognitiveWorkspace()
    h = HumanActor.create_default("Aelton")
    ws.introduce_entity(h, actor_id=h.id)
    g = Goal(id="g_p7", statement="Validar eficácia preliminar de composto biológico antes de ensaio in vivo")
    ws.introduce_entity(g, actor_id=h.id)

    assump = Claim(
        id="assump_p7",
        author_id=h.id,
        statement="A taxa de inibição observada in vitro se traduz proporcionalmente em modelos murinos",
        epistemic_type=EpistemicType.ASSUMPTION,
    )
    ws.introduce_entity(assump, actor_id=h.id)

    alt = Alternative(
        id="alt_p7_invivo",
        title="Avanço Direto para Fase Pré-Clínica in vivo",
        description="Iniciar testes animais baseado nas placas in vitro",
    )
    ws.introduce_entity(alt, actor_id=h.id)
    ws.connect(alt.id, assump.id, EdgeRelation.DEPENDS_ON, actor_id=h.id)
    return ws


def build_scenario_8_res_conflict() -> CognitiveWorkspace:
    """8. Pesquisa: Arbitragem de fontes contraditórias sobre desmatamento."""
    ws = CognitiveWorkspace()
    h = HumanActor.create_default("Aelton")
    ws.introduce_entity(h, actor_id=h.id)
    g = Goal(id="g_p8", statement="Estimar a perda líquida florestal de um bioma entre 2020 e 2025")
    ws.introduce_entity(g, actor_id=h.id)

    assump = Claim(
        id="assump_p8",
        author_id=h.id,
        statement="A metodologia de sensoriamento óptico do satélite A é imune a cobertura persistente de nuvens",
        epistemic_type=EpistemicType.ASSUMPTION,
    )
    ws.introduce_entity(assump, actor_id=h.id)

    alt = Alternative(
        id="alt_p8_sat_a",
        title="Adoção Exclusiva da Série Histórica do Satélite A",
        description="Ignorar dados de radar e utilizar apenas imagens ópticas",
    )
    ws.introduce_entity(alt, actor_id=h.id)
    ws.connect(alt.id, assump.id, EdgeRelation.DEPENDS_ON, actor_id=h.id)
    return ws


def build_scenario_9_learn_method() -> CognitiveWorkspace:
    """9. Aprendizagem: Prática deliberada espaçada vs Imersão contínua em bloco."""
    ws = CognitiveWorkspace()
    h = HumanActor.create_default("Aelton")
    ws.introduce_entity(h, actor_id=h.id)
    g = Goal(id="g_p9", statement="Aquisição de proficiência avançada em um novo idioma em 6 meses")
    ws.introduce_entity(g, actor_id=h.id)

    assump = Claim(
        id="assump_p9",
        author_id=h.id,
        statement="O estudante manterá disciplina ininterrupta de 45 minutos diários durante 180 dias",
        epistemic_type=EpistemicType.ASSUMPTION,
    )
    ws.introduce_entity(assump, actor_id=h.id)

    alt = Alternative(
        id="alt_p9_spaced",
        title="Cronograma de Repetição Espaçada Anki com Micro-Sessões",
        description="Revisão ativa diária de flashcards e conversação de 30 minutos",
    )
    ws.introduce_entity(alt, actor_id=h.id)
    ws.connect(alt.id, assump.id, EdgeRelation.DEPENDS_ON, actor_id=h.id)
    return ws


def build_scenario_10_learn_curriculum() -> CognitiveWorkspace:
    """10. Aprendizagem: Abordagem Bottom-Up formal vs Top-Down por projetos."""
    ws = CognitiveWorkspace()
    h = HumanActor.create_default("Aelton")
    ws.introduce_entity(h, actor_id=h.id)
    g = Goal(id="g_p10", statement="Aprender computação quântica para aplicação em algoritmos de otimização")
    ws.introduce_entity(g, actor_id=h.id)

    assump = Claim(
        id="assump_p10",
        author_id=h.id,
        statement="Dominar álgebra linear e análise funcional é pré-requisito indispensável antes de rodar o primeiro circuito no Qiskit",
        epistemic_type=EpistemicType.ASSUMPTION,
    )
    ws.introduce_entity(assump, actor_id=h.id)

    alt = Alternative(
        id="alt_p10_formal",
        title="Trilha Formal Bottom-Up: Álgebra Linear Rigorosa $\\to$ Circuitos",
        description="Completar 3 meses de teoria matemática pura antes de tocar em código quântico",
    )
    ws.introduce_entity(alt, actor_id=h.id)
    ws.connect(alt.id, assump.id, EdgeRelation.DEPENDS_ON, actor_id=h.id)
    return ws


CANONICAL_SCENARIO_BUILDERS = {
    "TECH_PERSISTENCE": build_scenario_1_tech_persistence,
    "TECH_ARCHITECTURE": build_scenario_2_tech_architecture,
    "TECH_SECURITY": build_scenario_3_tech_security,
    "BIZ_PRICING": build_scenario_4_biz_pricing,
    "BIZ_ROADMAP": build_scenario_5_biz_roadmap,
    "BIZ_CHANNELS": build_scenario_6_biz_channels,
    "RES_HYPOTHESIS": build_scenario_7_res_hypothesis,
    "RES_CONFLICT": build_scenario_8_res_conflict,
    "LEARN_METHOD": build_scenario_9_learn_method,
    "LEARN_CURRICULUM": build_scenario_10_learn_curriculum,
}
