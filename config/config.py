"""
Configuration management for AutoGen RetrieveChat system
Author: Jay Guwalani
"""

import os
import json
from typing import List, Dict, Any, Optional
import autogen
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for the RetrieveChat system"""
    
    def __init__(self):
        self.llm_config = self._load_llm_config()
        self.app_config = self._load_app_config()
        self.database_config = self._load_database_config()
        self._validate_config()
        
    def _load_llm_config(self) -> List[Dict]:
        """Load LLM configuration from various sources"""
        config_list = []
        
        # Try to load from OAI_CONFIG_LIST file
        try:
            config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
            logger.info(f"Loaded {len(config_list)} configurations from OAI_CONFIG_LIST")
            return config_list
        except Exception as e:
            logger.warning(f"Could not load OAI_CONFIG_LIST: {e}")
        
        # Fallback to environment variables
        openai_config = self._create_openai_config()
        if openai_config:
            config_list.append(openai_config)
            
        anthropic_config = self._create_anthropic_config()
        if anthropic_config:
            config_list.append(anthropic_config)
            
        if not config_list:
            logger.warning("No LLM configurations found. Using default GPT-4 config.")
            config_list = [{
                "model": "gpt-4",
                "api_key": "your-api-key-here",
                "base_url": "https://api.openai.com/v1"
            }]
            
        return config_list
    
    def _create_openai_config(self) -> Optional[Dict]:
        """Create OpenAI configuration from environment"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
            
        return {
            "model": os.getenv("OPENAI_MODEL", "gpt-4"),
            "api_key": api_key,
            "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "api_type": "openai",
            "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
            "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "4000"))
        }
    
    def _create_anthropic_config(self) -> Optional[Dict]:
        """Create Anthropic configuration from environment"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return None
            
        return {
            "model": os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
            "api_key": api_key,
            "base_url": os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
            "api_type": "anthropic",
            "temperature": float(os.getenv("ANTHROPIC_TEMPERATURE", "0.1")),
            "max_tokens": int(os.getenv("ANTHROPIC_MAX_TOKENS", "4000"))
        }
    
    def _load_app_config(self) -> Dict[str, Any]:
        """Load application configuration"""
        return {
            "debug": os.getenv("DEBUG", "False").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "max_workers": int(os.getenv("MAX_WORKERS", "4")),
            "cache_ttl": int(os.getenv("CACHE_TTL", "3600")),
            "api_host": os.getenv("API_HOST", "0.0.0.0"),
            "api_port": int(os.getenv("API_PORT", "8000")),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "secret_key": os.getenv("SECRET_KEY", "dev-secret-key"),
            "rate_limit": os.getenv("RATE_LIMIT", "100/hour"),
            "cors_origins": os.getenv("CORS_ORIGINS", "*").split(",")
        }
    
    def _load_database_config(self) -> Dict[str, Any]:
        """Load database configuration"""
        return {
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "postgres_url": os.getenv("POSTGRES_URL", "postgresql://postgres:password@localhost:5432/retrievechat"),
            "chroma_host": os.getenv("CHROMA_HOST", "localhost"),
            "chroma_port": int(os.getenv("CHROMA_PORT", "8001")),
            "chroma_persist_directory": os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db"),
            "vector_db_type": os.getenv("VECTOR_DB_TYPE", "chroma"),
            "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            "chunk_size": int(os.getenv("CHUNK_SIZE", "2000")),
            "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", "200"))
        }
    
    def _validate_config(self):
        """Validate configuration completeness and correctness"""
        # Validate LLM config
        if not self.llm_config:
            raise ValueError("No LLM configurations available")
        
        # Validate required environment variables for production
        if self.app_config["environment"] == "production":
            required_vars = ["SECRET_KEY"]
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        logger.info("Configuration validation passed")
    
    def get_model_names(self) -> List[str]:
        """Get list of available model names"""
        return [config.get("model", "unknown") for config in self.llm_config]
    
    def get_primary_model_config(self) -> Dict:
        """Get the primary model configuration"""
        return self.llm_config[0] if self.llm_config else {}
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.app_config["environment"] == "production"
