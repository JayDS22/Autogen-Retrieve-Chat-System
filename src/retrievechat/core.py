# src/retrievechat/core.py
"""
Core RetrieveChat system implementation
"""

import logging
import time
from typing import Dict, List, Any, Optional

import autogen
from autogen import AssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

logger = logging.getLogger(__name__)

class RetrieveChatSystem:
    """Production RAG system using AutoGen RetrieveChat"""
    
    def __init__(self, config_list: List[Dict]):
        self.config_list = config_list
        self.assistant = None
        self.rag_agent = None
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize assistant and RAG proxy agents"""
        
        self.assistant = AssistantAgent(
            name="assistant",
            system_message="You are a helpful AI assistant specialized in providing accurate, contextual responses based on retrieved information.",
            llm_config={
                "timeout": 600,
                "cache_seed": 42,
                "config_list": self.config_list,
                "temperature": 0.1,
            },
        )
        
        logger.info("Assistant agent initialized successfully")
        
    def create_rag_agent(self, 
                        docs_path: List[str], 
                        task_type: str = "code",
                        collection_name: str = None,
                        custom_prompt: str = None) -> RetrieveUserProxyAgent:
        """Create RAG agent with specified configuration"""
        
        if collection_name is None:
            collection_name = f"autogen-{task_type}-{int(time.time())}"
            
        retrieve_config = {
            "task": task_type,
            "docs_path": docs_path,
            "chunk_token_size": 2000,
            "model": self.config_list[0]["model"],
            "vector_db": "chroma",
            "collection_name": collection_name,
            "chunk_mode": "multi_lines",
            "embedding_model": "all-MiniLM-L6-v2",
            "get_or_create": True,
            "overwrite": False,
        }
        
        if custom_prompt:
            retrieve_config["customized_prompt"] = custom_prompt
            retrieve_config["customized_answer_prefix"] = "Based on the analysis:"
        
        self.rag_agent = RetrieveUserProxyAgent(
            name="rag_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
            retrieve_config=retrieve_config,
            code_execution_config=False,
        )
        
        logger.info(f"RAG agent created with collection: {collection_name}")
        return self.rag_agent
    
    def execute_conversation(self, 
                           question: str, 
                           search_string: str = None,
                           n_results: int = 20) -> Dict[str, Any]:
        """Execute conversation between agents with performance monitoring"""
        
        if not self.rag_agent:
            raise ValueError("RAG agent not initialized. Call create_rag_agent() first.")
        
        start_time = time.time()
        
        self.assistant.reset()
        
        chat_result = self.rag_agent.initiate_chat(
            self.assistant,
            message=self.rag_agent.message_generator,
            problem=question,
            search_string=search_string,
            n_results=n_results
        )
        
        execution_time = time.time() - start_time
        
        metrics = {
            "execution_time": execution_time,
            "question": question,
            "response_length": len(str(chat_result.summary)) if chat_result.summary else 0,
            "conversation_turns": len(chat_result.chat_history) if hasattr(chat_result, 'chat_history') else 0
        }
        
        logger.info(f"Conversation completed in {execution_time:.2f}s")
        
        return {
            "result": chat_result,
            "metrics": metrics
        }
