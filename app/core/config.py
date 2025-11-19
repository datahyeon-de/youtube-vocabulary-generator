from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TOKENIZER_MODEL: str = "Qwen/Qwen2.5-14B-Instruct-AWQ"
    MAX_TOKEN_COUNT: int = 2000

settings = Settings()