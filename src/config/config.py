"""
Configuration management for RetrieveChat system
"""

import os
import json
from typing import List, Dict, Any
import autogen

class Config:
    """Configuration manager"""
    
    def __init__(self):
        self.llm_config = self._load_llm_config()
        self.app_config = self._load_app_config()
        
    def _load_llm_config(self) -> List[Dict]:
        """Load LLM configuration"""
        try:
            config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
            return config_list
        except Exception:
            # Fallback configuration
            return [{
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": "https://api.openai.com/v1"
            }]
    
    def _load_app_config(self) -> Dict[str, Any]:
        """Load application configuration"""
        return {
            "debug": os.getenv("DEBUG", "False").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "max_workers": int(os.getenv("MAX_WORKERS", "4")),
            "cache_ttl": int(os.getenv("CACHE_TTL", "3600"))
        }
