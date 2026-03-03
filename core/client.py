from __future__ import annotations

import os
from openai import OpenAI


BUILTIN_PROVIDERS = {
    "openai": {
        "base_url": None,
        "api_key_env": "OPENAI_API_KEY",
    },
    "huggingface": {
        "base_url": "https://router.huggingface.co/v1",
        "api_key_env": "HF_TOKEN",
    },
}


def get_client(provider: str, custom_providers: dict | None = None) -> OpenAI:
    providers = {**BUILTIN_PROVIDERS, **(custom_providers or {})}

    config = providers.get(provider)
    if not config:
        raise ValueError(
            f"Unknown provider: '{provider}'. "
            f"Add it under 'providers' in models.yaml or use one of: "
            f"{', '.join(providers)}"
        )

    api_key = os.getenv(config["api_key_env"])
    if not api_key:
        raise EnvironmentError(
            f"Missing API key: set {config['api_key_env']} in your .env"
        )

    kwargs = {"api_key": api_key}
    if config.get("base_url"):
        kwargs["base_url"] = config["base_url"]

    return OpenAI(**kwargs)


def call_model(
    client: OpenAI, model_id: str, system_prompt: str, user_prompt: str
) -> str:
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content
