from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str

    DATABASE_URL: str

    QDRANT_URL: str
    QDRANT_API_KEY: str

    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
