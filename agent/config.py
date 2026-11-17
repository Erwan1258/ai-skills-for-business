"""Choix du fournisseur de LLM.

Tous les fournisseurs ci-dessous exposent une API compatible OpenAI : on utilise donc
un seul client (ChatOpenAI) et on change uniquement l'URL, la clé et le modèle.
Le fournisseur se choisit dans le fichier .env (voir .env.example).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


@dataclass(frozen=True)
class Provider:
    base_url: str
    default_model: str
    key_env: str | None  # None = pas de clé nécessaire (local)


PROVIDERS: dict[str, Provider] = {
    "groq": Provider("https://api.groq.com/openai/v1", "openai/gpt-oss-120b", "GROQ_API_KEY"),
    "gemini": Provider(
        "https://generativelanguage.googleapis.com/v1beta/openai/", "gemini-2.5-flash", "GEMINI_API_KEY"
    ),
    "mistral": Provider("https://api.mistral.ai/v1", "mistral-small-latest", "MISTRAL_API_KEY"),
    "ollama": Provider("http://localhost:11434/v1", "qwen2.5:7b", None),
    "openai": Provider("https://api.openai.com/v1", "gpt-4o-mini", "OPENAI_API_KEY"),
}


class ConfigError(RuntimeError):
    """Configuration du LLM absente ou invalide."""


def provider_name() -> str:
    return os.getenv("LLM_PROVIDER", "groq").strip().lower()


def get_llm(temperature: float = 0.2) -> ChatOpenAI:
    name = provider_name()
    if name not in PROVIDERS:
        raise ConfigError(f"LLM_PROVIDER inconnu : « {name} ». Valeurs possibles : {', '.join(PROVIDERS)}")
    provider = PROVIDERS[name]

    api_key = "ollama"  # Ollama ignore la clé, mais le client en exige une
    if provider.key_env:
        api_key = os.getenv(provider.key_env, "").strip()
        if not api_key:
            raise ConfigError(
                f"Clé manquante : ajoutez {provider.key_env}=... dans le fichier .env "
                f"(fournisseur sélectionné : {name})."
            )

    return ChatOpenAI(
        model=os.getenv("LLM_MODEL") or provider.default_model,
        base_url=os.getenv("LLM_BASE_URL") or provider.base_url,
        api_key=api_key,
        temperature=temperature,
        max_retries=2,
    )
