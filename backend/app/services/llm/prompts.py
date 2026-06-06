"""Versioned prompt registry."""

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


class PromptMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length=1)


class PromptDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    description: str | None = None
    model_preference: str | None = None
    output_format: str | None = None
    system_template: str = Field(..., min_length=1)
    human_template: str = Field(..., min_length=1)
    variables: list[str] = Field(default_factory=list)
    fallback_output: dict[str, Any] = Field(default_factory=dict)


class RenderedPrompt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    version: str
    model_preference: str | None = None
    messages: list[PromptMessage]


class PromptRegistry:
    def __init__(self, prompt_root: Path | None = None) -> None:
        self.prompt_root = prompt_root or Path(__file__).resolve().parents[3] / "prompts"

    def load(self, prompt_name: str, *, version: str = "v1") -> PromptDefinition:
        path = self.prompt_root / prompt_name / f"{version}.yaml"
        if not path.is_file():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return PromptDefinition.model_validate(data)

    def render(
        self,
        prompt_name: str,
        variables: Mapping[str, Any],
        *,
        version: str = "v1",
    ) -> RenderedPrompt:
        definition = self.load(prompt_name, version=version)
        template_vars = {key: self._template_value(value) for key, value in variables.items()}
        return RenderedPrompt(
            name=definition.name,
            version=definition.version,
            model_preference=definition.model_preference,
            messages=[
                PromptMessage(
                    role="system",
                    content=definition.system_template.format_map(template_vars),
                ),
                PromptMessage(
                    role="user",
                    content=definition.human_template.format_map(template_vars),
                ),
            ],
        )

    @staticmethod
    def _template_value(value: Any) -> str:
        if isinstance(value, str):
            return value
        return json.dumps(value, default=str, ensure_ascii=False, sort_keys=True)
