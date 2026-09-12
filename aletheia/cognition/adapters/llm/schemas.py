"""Schemas intermediários de saída estruturada para capacidades LLM."""

from typing import List, Optional
from pydantic import BaseModel, Field
from aletheia.core.entities import ArgumentStance


class LLMArgumentProposal(BaseModel):
    """Proposta de argumento emitida pelo modelo probabilístico."""
    alternative_id: str = Field(..., description="ID da alternativa alvo referenciada")
    stance: ArgumentStance = Field(default=ArgumentStance.OPPOSE, description="Postura: OPPOSE ou SUPPORT")
    premise_refs: List[str] = Field(default_factory=list, description="IDs de premissas/suposições da projeção que fundamentam o argumento")
    rationale: str = Field(..., description="Texto da fundamentação crítica ou de sustentação")
    critical_depth_score: int = Field(default=3, ge=0, le=5, description="Autoavaliação de profundidade analítica de 0 a 5")


class LLMUnknownProposal(BaseModel):
    """Proposta de incerteza explícita formulada pelo modelo."""
    description: str = Field(..., description="Enunciado claro da lacuna de conhecimento")
    blocking: bool = Field(default=False, description="Se a incerteza impede a adoção segura da alternativa")
    resolution_criteria: Optional[str] = Field(default=None, description="Critério pelo qual esta incerteza pode ser dirimida")


class LLMCritiquePayload(BaseModel):
    """Payload completo estruturado de crítica emitido pelo LLM (Untrusted)."""
    target_alternative_id: str = Field(..., description="ID da alternativa alvo sob exame")
    arguments: List[LLMArgumentProposal] = Field(default_factory=list)
    unknowns: List[LLMUnknownProposal] = Field(default_factory=list)
    model_confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Grau de certeza probabilística autodeclarado pelo modelo")
    reasoning_summary: str = Field(..., description="Resumo do racional analítico da crítica")
    contingency_hypothesis: Optional[str] = Field(default=None, description="Hipótese de contingência caso a premissa falhe")
