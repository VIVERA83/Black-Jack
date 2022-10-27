from pydantic import BaseModel, BaseSettings

__all__ = ["Config"]


class Postgres(BaseModel):
    db: str
    user: str
    password: str
    host: str
    port: int

    @property
    def dsn(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class Config(BaseSettings):
    session_key: str
    postgres: Postgres

    class Config:
        env_nested_delimiter = "__"
