"""Testes unitários para primitivos ontológicos e seus invariantes."""

import pytest
from pydantic import ValidationError
from aletheia.core.entities import (
    ActorRole,
    Capability,
    Claim,
    CognitiveDecisionRecord,
    DecisionStatus,
    DeltaType,
    DissentingView,
    EpistemicDelta,
    EpistemicType,
    Evidence,
    HumanActor,
    Inference,
    Lesson,
    LifecycleStatus,
    Question,
    QuestionStatus,
    ReversibilityType,
    SpecialistActor,
    Unknown,
)
from aletheia.core.entities.deliberation import ArgumentStance


def test_claim_epistemic_type_and_status_separation():
    """Invariante: Separação categórica entre epistemic_type e lifecycle_status."""
    claim = Claim(
        author_id="human_1",
        statement="O modelo opera em menos de 50ms",
        epistemic_type=EpistemicType.ASSUMPTION,
        lifecycle_status=LifecycleStatus.ACTIVE,
    )
    assert claim.epistemic_type == EpistemicType.ASSUMPTION
    assert claim.lifecycle_status == LifecycleStatus.ACTIVE

    # Invariante Falsificacionista: SUPPORTED != VERIFIED_FACT
    claim.lifecycle_status = LifecycleStatus.SUPPORTED
    assert claim.lifecycle_status == LifecycleStatus.SUPPORTED
    assert claim.epistemic_type == EpistemicType.ASSUMPTION  # Continua sendo assumption!


def test_inference_requires_non_empty_premises():
    """Invariante: Inference deve possuir premissas explícitas de sustentação."""
    with pytest.raises(ValidationError):
        Inference(
            author_id="spec_1",
            conclusion="Conclusão sem premissas",
            derivation_method="DEDUCTIVE",
            premise_ids=[],  # Vazio não é permitido
        )


def test_unknown_and_question_differentiation():
    """Invariante: Unknown é ausência de conhecimento; Question é ato de busca."""
    unknown = Unknown(
        author_id="spec_1",
        description="Qual a taxa de perda de pacotes sob carga?",
        blocking=True,
    )
    assert unknown.blocking is True

    question = Question(
        author_id="spec_1",
        question_text="Você possui medições de perda de pacotes?",
        target_unknown_id=unknown.id,
        asked_by="spec_1",
        addressed_to="human_1",
    )
    assert question.status == QuestionStatus.OPEN
    assert question.target_unknown_id == unknown.id


def test_cdr_requires_contextual_scope():
    """Invariante: CDR deve possuir decision_scope obrigatório e contextual."""
    with pytest.raises(ValidationError):
        CognitiveDecisionRecord(
            cdr_id="CDR-01",
            title="Decisão Inválida",
            decision_owner="human_1",
            decision_scope="",  # Não pode ser vazio
            chosen_alternative_ref="alt_1",
        )


def test_epistemic_delta_allows_no_lesson():
    """Invariante: Nem todo EpistemicDelta gera uma Lesson obrigatoriamente."""
    delta = EpistemicDelta(
        action_ref="act_1",
        outcome_ref="out_1",
        expected_state="Resposta em 40ms",
        observed_state="Resposta em 42ms",
        delta_type=DeltaType.NO_MEANINGFUL_LEARNING,
        discrepancy="Variação normal de rede de 2ms",
        lesson_generated=False,
    )
    assert delta.delta_type == DeltaType.NO_MEANINGFUL_LEARNING
    assert delta.lesson_generated is False


def test_specialist_capability_model():
    """Validação do Capability Model para atores especialistas."""
    critic = SpecialistActor(
        id="critic_01",
        name="Pragmatic Risk Critic",
        perspective="Mitigação de complexidade e risco operacional",
        capabilities=[Capability.CRITIQUE, Capability.REASONING],
        policies=["Rejeitar suposições sem critérios de falseabilidade"],
    )
    assert Capability.CRITIQUE in critic.capabilities
    assert critic.role == ActorRole.SPECIALIST
