"""very basic llm component"""

from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.generators.openai import OpenAIGenerator
from haystack.utils import Secret


def get_base_llm() -> OpenAIGenerator:
    """method to avoid rewriting the same snippet.
    very basic groq generator
    """
    return OpenAIGenerator(
        api_key=Secret.from_env_var("GROQ_KEY"),
        api_base_url="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile",
        generation_kwargs={"max_tokens": 2048},
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
