from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl

class Settings(BaseSettings):
    # Config Pydantic v2
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ---- App ----
    APP_NAME: str = "Shift Suite"
    APP_ENV: str = "dev"
    APP_TIMEZONE: str = "Europe/Rome"
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5173"

    # ---- DB ----
    DATABASE_URL: AnyUrl  # es: postgresql+asyncpg://shifts:shifts@db:5432/shifts

    # ---- SMTP ----
    SMTP_HOST: str = "mailhog"
    SMTP_PORT: int = 1025
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str = "no-reply@shifts.local"

    # ---- OIDC opzionale ----
    OIDC_ISSUER_URL: str | None = None
    OIDC_AUDIENCE: str | None = None


settings = Settings()
