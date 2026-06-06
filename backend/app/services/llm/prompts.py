"""Versioned prompt registry."""

import json
from collections.abc import Mapping
from pathlib import Path
from string import Template
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


class PromptMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length=1)


class PromptDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    description: str | None = None
    messages: list[PromptMessage] = Field(..., min_length=1)


class RenderedPrompt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    version: str
    messages: list[PromptMessage]


class PromptRegistry:
    def __init__(self, prompt_root: Path | None = None) -> None:
        self.prompt_root = prompt_root or Path(__file__).resolve().parents[3] / "prompts"

    def load(self, prompt_id: str, *, version: str = "v1") -> PromptDefinition:
        path = self.prompt_root / prompt_id / f"{version}.yaml"
        if not path.is_file():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return PromptDefinition.model_validate(data)

    def render(
        self,
        prompt_id: str,
        variables: Mapping[str, Any],
        *,
        version: str = "v1",
    ) -> RenderedPrompt:
        definition = self.load(prompt_id, version=version)
        template_vars = {key: self._template_value(value) for key, value in variables.items()}
        return RenderedPrompt(
            id=definition.id,
            version=definition.version,
            messages=[
                PromptMessage(
                    role=message.role,
                    content=Template(message.content).substitute(template_vars),
                )
                for message in definition.messages
            ],
        )

    @staticmethod
    def _template_value(value: Any) -> str:
        if isinstance(value, str):
            return value
        return json.dumps(value, default=str, ensure_ascii=False, sort_keys=True)
