import json

from typing import List, Optional

from haystack import Pipeline, component
from haystack.components.builders import PromptBuilder


from base_llm import get_base_llm
from prompt import prompt as few_shot


@component
class AlertGenerator:
    def __init__(self, prompt: Optional[str] = few_shot):
        self.alert_generation_prompt = prompt
        if prompt is None:
            self.alert_generation_prompt = prompt
        builder = PromptBuilder(
            self.alert_generation_prompt,  # pyright: ignore
            required_variables=["number"],
        )
        llm = get_base_llm()
        self.pipeline = Pipeline()
        self.pipeline.add_component(name="builder", instance=builder)
        self.pipeline.add_component(name="llm", instance=llm)
        self.pipeline.connect("builder", "llm")

    @component.output_types(alerts=List[dict])
    def run(self, number: int = 5):
        result = self.pipeline.run({"builder": {"number": number}})
        generated_alerts = json.loads(result["llm"]["replies"][0])
        return {"alerts": generated_alerts}
