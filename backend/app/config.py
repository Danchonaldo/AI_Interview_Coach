"""Runtime configuration, read from environment variables (optionally from backend/.env).

Secrets (API keys) are only ever read here, on the backend. They are never logged or
returned by the API.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent

# Load backend/.env if present. Real environment variables take precedence.
load_dotenv(BACKEND_DIR / ".env", override=False)


@dataclass(frozen=True)
class Settings:
    database_url: str
    llm_provider: str
    anthropic_model: str
    openai_model: str
    llm_timeout_seconds: float
    cors_origins: tuple[str, ...]


def get_settings() -> Settings:
    default_db = f"sqlite:///{(BACKEND_DIR / 'data' / 'interview_coach.db').as_posix()}"
    return Settings(
        database_url=os.getenv("DATABASE_URL", default_db),
        llm_provider=os.getenv("LLM_PROVIDER", "mock").strip().lower(),
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        llm_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "60")),
        cors_origins=tuple(
            o.strip()
            for o in os.getenv(
                "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
            ).split(",")
            if o.strip()
        ),
    )
