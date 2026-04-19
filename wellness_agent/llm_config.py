"""
LLM configuration for the Wellness Agent.

Detects available API keys and selects the provider automatically:
  - GOOGLE_API_KEY  → native Gemini (default)
  - OPENAI_API_KEY  → OpenAI via LiteLLM

Override with LLM_PROVIDER / LLM_MODEL env vars for full control.
"""

import os
import logging
from typing import Union

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_MODEL_DEFAULTS = {
    "google": "gemini-2.0-flash",
    "openai": "gpt-4o-mini",
    "ollama": "llama3.2",
}


def _detect_provider() -> str:
    explicit = (os.getenv("LLM_PROVIDER") or "").lower().strip()
    if explicit:
        return explicit
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    return "google"


def create_model() -> Union["LiteLlm", str]:  # noqa: F821
    provider = _detect_provider()
    model = (os.getenv("LLM_MODEL") or "").strip() or _MODEL_DEFAULTS.get(provider, "gpt-4o-mini")
    api_base = (os.getenv("LLM_API_BASE") or "").strip() or None

    if provider == "google":
        logger.info("Using model: %s", model)
        return model

    from google.adk.models.lite_llm import LiteLlm

    litellm_model = model if "/" in model else f"{provider}/{model}"
    kwargs: dict = {"model": litellm_model}

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            kwargs["api_key"] = api_key
    elif api_key_env := os.getenv("LLM_API_KEY"):
        kwargs["api_key"] = api_key_env

    if api_base:
        kwargs["api_base"] = api_base

    logger.info("Using model: %s (provider=%s)", litellm_model, provider)
    return LiteLlm(**kwargs)
