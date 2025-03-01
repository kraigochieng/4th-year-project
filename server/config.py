from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ml_model_path: str
    encoders_path: str
    access_secret_key: str
    refresh_secret_key: str
    access_algorithm: str
    refresh_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
