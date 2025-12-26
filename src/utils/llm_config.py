"""
LLM configuration module for centralized Gemini client management.
Creates a single reusable ChatGoogleGenerativeAI client with the API key.
"""

import os
from functools import lru_cache
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv(override=True)


def get_api_key() -> str:
    """Get the Google API key from environment variables."""
    # Check for GOOGLE_API_KEY first, then GEMINI_API_KEY
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY in environment or .env file."
        )
    return api_key


@lru_cache(maxsize=4)
def get_llm(
    model_name: str = "gemini-2.5-pro", temperature: float = 0
) -> ChatGoogleGenerativeAI:
    """
    Get a cached ChatGoogleGenerativeAI instance.

    Args:
        model_name: Gemini model to use (default: gemini-1.5-flash for faster responses)
        temperature: Model temperature (default: 0 for deterministic outputs)

    Returns:
        ChatGoogleGenerativeAI instance configured with the API key
    """
    api_key = get_api_key()
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=api_key,
    )


# Default model for general use
DEFAULT_MODEL = "gemini-3-pro-preview"
