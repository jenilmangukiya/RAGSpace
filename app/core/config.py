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

    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    STRIPE_PRO_MONTHLY_PRICE_ID: str
    STRIPE_PRO_YEARLY_PRICE_ID: str
    STRIPE_PREMIUM_MONTHLY_PRICE_ID: str
    STRIPE_PREMIUM_YEARLY_PRICE_ID: str

    class Config:
        env_file = ".env"


settings = Settings()
