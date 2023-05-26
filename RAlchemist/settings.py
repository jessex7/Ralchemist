from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SQLA_ECHO: bool

    class Config:
        env_file = "dev.env", "prod.env"


settings = Settings()  # type: ignore
