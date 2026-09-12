"""Mock LLM Adapter: Provedor determinístico e reprodutível para testes e benchmarks offline."""

import hashlib
import json
import time
from typing import Any, Callable, Dict, Optional, Type
from pydantic import BaseModel
from aletheia.ports.llm_port import LLMProviderPort, LLMResponse


class MockLLMAdapter(LLMProviderPort):
    """Adaptador de LLM determinístico com suporte a fixtures e respostas customizadas."""

    def __init__(self) -> None:
        self._fixtures: Dict[str, BaseModel] = {}
        self._handlers: Dict[str, Callable[[str], BaseModel]] = {}
        self.call_history: list[Dict[str, Any]] = []

    def register_fixture(self, prompt_keyword: str, response: BaseModel) -> None:
        """Registra uma resposta padrão quando uma palavra-chave estiver contida no prompt."""
        self._fixtures[prompt_keyword.lower()] = response

    def register_handler(self, prompt_keyword: str, handler: Callable[[str], BaseModel]) -> None:
        """Registra uma função geradora dinâmica para um padrão de prompt."""
        self._handlers[prompt_keyword.lower()] = handler

    def generate_structured(
        self,
        prompt: str,
        response_schema: Type[BaseModel],
        system_instruction: Optional[str] = None,
        temperature: float = 0.0,
    ) -> LLMResponse:
        start_time = time.perf_counter()
        prompt_lower = prompt.lower()

        # 1. Verifica handlers dinâmicos
        selected_output: Optional[BaseModel] = None
        for kw, handler in self._handlers.items():
            if kw in prompt_lower:
                selected_output = handler(prompt)
                break

        # 2. Verifica fixtures estáticas
        if not selected_output:
            for kw, fix in self._fixtures.items():
                if kw in prompt_lower:
                    selected_output = fix
                    break

        # 3. Fallback: Se nenhuma fixture foi registrada, constrói resposta mínima compatível
        if not selected_output:
            # Tenta instanciar schema com valores dummy caso suporte
            try:
                selected_output = response_schema.model_construct(
                    target_alternative_id="alt_default",
                    arguments=[],
                    unknowns=[],
                    model_confidence=0.85,
                    reasoning_summary="Análise crítica padrão do mock",
                )
            except Exception:
                raise ValueError(f"MockLLMAdapter: Nenhuma fixture registrada para o prompt e fallback falhou.")

        latency_ms = (time.perf_counter() - start_time) * 1000
        output_json = selected_output.model_dump_json()
        raw_hash = hashlib.sha256(output_json.encode("utf-8")).hexdigest()

        prompt_tokens = len(prompt.split())
        completion_tokens = len(output_json.split())
        response = LLMResponse(
            parsed_output=selected_output,
            model="mock-deterministic-v1",
            provider="mock",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            latency_ms=round(latency_ms, 2),
            finish_reason="stop",
            raw_response_hash=raw_hash,
        )

        self.call_history.append({"prompt": prompt, "response": response})
        return response
