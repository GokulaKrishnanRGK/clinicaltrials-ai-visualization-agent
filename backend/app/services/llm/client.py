"""Small LiteLLM wrapper for graph-node structured outputs."""

import json
import os
from collections.abc import Awaitable, Callable, Mapping
from typing import Any, TypeVar

from litellm import acompletion
from pydantic import TypeAdapter, ValidationError

from app.services.llm.prompts import PromptRegistry

ResponseModelT = TypeVar("ResponseModelT")
CompletionFn = Callable[..., Awaitable[Any]]


class LLMClientError(RuntimeError):
    """Raised when an LLM call or structured response validation fails."""


class LLMClient:
    def __init__(
        self,
        *,
        registry: PromptRegistry | None = None,
        completion_fn: CompletionFn = acompletion,
        model: str | None = None,
        temperature: float = 0,
        max_tokens: int = 2000,
    ) -> None:
        self.registry = registry or PromptRegistry()
        self.completion_fn = completion_fn
        self.model = model or os.getenv("CLINICAL_TRIALS_LLM_MODEL", "gpt-4o-mini")
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def complete_structured(
        self,
        *,
        prompt_id: str,
        response_model: Any,
        variables: Mapping[str, Any],
        version: str = "v1",
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ResponseModelT:
        prompt = self.registry.render(prompt_id, variables, version=version)
        response = await self.completion_fn(
            model=model or prompt.model_preference or self.model,
            messages=[message.model_dump() for message in prompt.messages],
            temperature=self.temperature if temperature is None else temperature,
            max_tokens=self.max_tokens if max_tokens is None else max_tokens,
            response_format={"type": "json_object"},
        )
        content = self._extract_content(response)
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMClientError(f"LLM response was not valid JSON: {exc}") from exc
        try:
            return TypeAdapter(response_model).validate_python(payload)
        except ValidationError as exc:
            message = f"LLM response failed {self._response_model_name(response_model)} validation"
            raise LLMClientError(message) from exc

    @staticmethod
    def _extract_content(response: Any) -> str:
        try:
            content = response.choices[0].message.content
        except (AttributeError, IndexError, KeyError, TypeError) as exc:
            raise LLMClientError("LLM response did not include message content") from exc
        if not isinstance(content, str) or not content.strip():
            raise LLMClientError("LLM response content was empty")
        return content

    @staticmethod
    def _response_model_name(response_model: Any) -> str:
        return getattr(response_model, "__name__", repr(response_model))
