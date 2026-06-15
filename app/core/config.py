from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SECRET_KEY: str

    DATABASE_URL: str

    QDRANT_URL: str
    QDRANT_API_KEY: str

    OPENAI_API_KEY: str

    REDIS_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
