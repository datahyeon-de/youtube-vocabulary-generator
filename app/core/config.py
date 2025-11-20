from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 자막 Chunk 생성 설정
    TOKENIZER_MODEL: str = "Qwen/Qwen2.5-14B-Instruct-AWQ"
    MAX_TOKEN_COUNT: int = 2000

    # vLLM 서버 설정
    VLLM_SERVER_URL: str = "http://tc-server-gpu:8000"
    VLLM_SERVER_ENDPOINT: str = "/v1/chat/completions"
    VLLM_SERVER_MODEL: str = "Qwen/Qwen2.5-14B-Instruct-AWQ"
    VLLM_SERVER_TIMEOUT: int = 60
    VLLM_SERVER_MAX_RETRIES: int = 3
    VLLM_SERVER_RETRY_DELAY: int = 3
    
settings = Settings()