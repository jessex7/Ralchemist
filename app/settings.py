from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = "dev.env", "prod.env"


settings = Settings()  # type: ignore
