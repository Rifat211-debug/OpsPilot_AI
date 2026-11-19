from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import SecretStr


class Settings(BaseSettings):

    APP_NAME: str = "OpsPilot AI"
    DEBUG: bool = False

    GROQ_API_KEY: SecretStr = SecretStr("")
    LLM_MODEL_ANSWER: str = "llama-3.3-70b-versatile"
    LLM_MODEL_GRADER: str = "llama-3.1-8b-instant"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "documents"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ops_pilot"

    UPSTASH_REDIS_URL: str = ""
    UPSTASH_REDIS_TOKEN: str =""

    CACHE_TTL_EMBEDDINGS: int = 604800
    CACHE_TTL_RAG: int = 3600
    CACHE_TTL_SQL_GEN: int = 86400
    CACHE_TTL_SQL_RESULT: int = 900
    CACHE_TTL_INTENT: int = 86400

    STORAGE_BACKEND: str = "local"
    S3_CACHE_BUCKET: str = "ops-pilot-cache"
    AWS_REGION: str = "us-east-1"

    TAVILY_API_KEY: str = ""

    JWT_SECRET: str = ""
    JWT_EXPIRATION_MINUTES: int = 60

    RATE_LIMIT_REQUESTS: int = 20
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    MAX_TOKENS_PER_USER_DAILY: int = 100000
    AUTH_LOGIN_RATE_LIMIT_PER_MIN: int = 5
    AUTH_REGISTER_RATE_LIMIT_PER_HOUR: int = 3

    MAX_INPUT_TOKENS: int = 3000
    RESERVED_CONTEXT_TOKENS: int = 1000
    RESERVED_OUTPUT_TOKENS: int = 1000

    PROMPT_INJECTION_THRESHOLD: float = 0.75
    TOXICITY_THRESHOLD: float = 0.75
    OUTPUT_TOXICITY_THRESHOLD: float = 0.5
    MAX_VALIDATION_RETRIES: float = 2

    HYDE_NUM_HYPOTHESES: int = 3
    HYDE_ENABLED_BY_DEFAULT: bool = False
    HYBRID_SEARCH_ENABLED: bool = True
    RRF_K: int = 60

    RERANKER_BACKEND: str = "local"
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    VOYAGE_API_KEY: str = ""
    VOYAGE_MODEL: str = "rerank-2.5"

    RERANKER_INITIAL_TOP_K: int = 20
    RERANKING_ENABLED_BY_DEFAULT: float = True
    CRAG_RELEVANCE_THRESHOLD: float = 0.7
    CRAG_AMBIGUOUS_THRESHOLD: float = 0.5
    CRAG_ENABLED_BY_DEFAULT: float = True
    REFLECTION_MIN_SCORE: float = 0.85
    MAX_REFLECTION_RETRIES: int = 2
    SELF_REFLECTIVE_ENABLED_BY_DEFAULT: bool = False

    VANNA_LLM_PROVIDER: str = "groq"
    VANNA_MODEL: str = "llama-3.3-70b-versatile"
    VANNA_TEMPERATURE: float = 0.0
    VANNA_SEED: int = 42
 
    LOG_JSON: bool = False
    LOG_LEVEL: str = "INFO"
    
    
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore"
    )
    

@lru_cache
def get_settings():
    return Settings()    