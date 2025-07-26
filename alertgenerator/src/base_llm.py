from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.utils import Secret

from haystack_integrations.components.generators.google_ai import (
    GoogleAIGeminiGenerator,
)


def get_base_llm(model: str = "gemini-2.5-flash") -> GoogleAIGeminiGenerator:
    return GoogleAIGeminiGenerator(
        api_key=Secret.from_env_var("GOOGLE_API_KEY"), model=model
    )


def get_base_chat_llm(generation_kwargs: dict) -> OpenAIChatGenerator:
    return OpenAIChatGenerator(
        api_key=Secret.from_env_var("GROQ_KEY"),
        api_base_url="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile",
        generation_kwargs=generation_kwargs,
    )
