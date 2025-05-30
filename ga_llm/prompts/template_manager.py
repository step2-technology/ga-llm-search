# File: ga_llm/prompts/template_manager.py
# Author: Jonas Lin, Jacky Cen
# Version: 0.2
# Description: Prompt manager for template formatting and reuse

class PromptTemplateManager:
    """Centralized manager for prompt templates."""

    def __init__(self, templates: dict):
        self.templates = templates

    def get(self, name: str) -> str:
        if name not in self.templates:
            raise ValueError(f"Template '{name}' not found.")
        return self.templates[name]

    def render(self, name: str, **kwargs) -> str:
        template = self.get(name)
        return template.format(**kwargs)
