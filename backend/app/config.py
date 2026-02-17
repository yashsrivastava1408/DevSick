"""Application configuration and environment settings."""
import os


class Settings:
    APP_NAME: str = "Devsick"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-Driven Application Support & Operations Platform"
    
    # Groq API
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = "llama3-8b-8192"
    
    # Correlation engine
    CORRELATION_WINDOW_SECONDS: int = 60
    MIN_EVENTS_FOR_INCIDENT: int = 2
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]


settings = Settings()
