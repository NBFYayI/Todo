from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://todo_user:1222@localhost:5432/tododb"
    SECRET_KEY: str = "CHANGE_ME_SECRET_KEY"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
