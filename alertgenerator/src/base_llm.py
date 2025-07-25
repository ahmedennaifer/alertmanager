"""very basic llm component"""

from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.generators.openai import OpenAIGenerator
from haystack.utils import Secret

from haystack_integrations.components.generators.google_ai import (
    GoogleAIGeminiGenerator,
)

from dotenv import load_dotenv


def get_base_llm() -> GoogleAIGeminiGenerator:
    return GoogleAIGeminiGenerator(
        api_key=Secret.from_env_var("GOOGLE_API_KEY"), model="gemini-2.5-flash"
    )


def get_base_chat_llm(generation_kwargs: dict) -> OpenAIChatGenerator:
    """method to avoid rewriting the same snippet.
    very basic groq generator
    """
    return OpenAIChatGenerator(
        api_key=Secret.from_env_var("GROQ_KEY"),
        api_base_url="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile",
        generation_kwargs=generation_kwargs,
    )
