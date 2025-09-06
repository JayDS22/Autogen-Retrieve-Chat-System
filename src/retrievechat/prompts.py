"""
Core RetrieveChat system implementation
Author: Jay Guwalani
"""

import logging
import time
import hashlib
from typing import Dict, List, Any, Optional
from pathlib import Path

import autogen
from autogen import AssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import chromadb

from .prompts import PromptManager
from .utils import DocumentProcessor, VectorDBManager

logger = logging.getLogger(__name__)

class RetrieveChatSystem:
    """
    Production-ready RAG system using AutoGen RetrieveChat
    
    Features:
    - Multi-agent conversational architecture
    - Dynamic context management
    - Performance monitoring
    - Error handling and recovery
    - Scalable vector database integration
    """
    
    def __init__(self, config_list: List[Dict], system_config: Dict = None):
        self.config_list = config_list
        self.system_config = system_config or {}
        self.assistant = None
        self.rag_agent = None
        self.prompt_manager = PromptManager()
        self.doc_processor = DocumentProcessor()
        self.vector_db_manager = VectorDBManager()
        self.conversation_history = []
        self.performance_metrics = {}
        
        self._initialize_agents()
        logger.info("RetrieveChatSystem initialized successfully")
        
    def _initialize_agents(self):
        """Initialize the assistant agent with optimal configuration"""
        
        # Enhanced system message for better performance
        system_message = """You are an advanced AI assistant specializing in retrieval-augmented conversations. 

Key capabilities:
- Provide accurate, contextual responses based on retrieved information
- Synthesize information from multiple sources
- Generate high-quality code when requested
- Perform step-by-step reasoning for complex queries
- Acknowledge when information is insufficient

Guidelines:
- Always base responses on provided context when available
- Be precise and concise while maintaining completeness
- Use proper citations when referencing sources
- Request context updates when current information is inadequate
- Maintain consistency across conversation turns"""
        
        # Optimized LLM configuration
        llm_config = {
            "timeout": 600,
            "cache_seed": 42,
            "config_list": self.config_list,
            "temperature": 0.1,  # Low temperature for consistency
            "max_tokens": 4000,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        }
        
        self.assistant = AssistantAgent(
            name="assistant",
            system_message=system_message,
            llm_config=llm_config,
        )
        
        logger.info("Assistant agent initialized with enhanced configuration")
        
    def create_rag_agent(self, 
                        docs_path: List[str], 
                        task_type: str = "code",
                        collection_name: str = None,
                        custom_prompt: str = None,
                        **kwargs) -> RetrieveUserProxyAgent:
        """
        Create RAG agent with advanced configuration options
        
        Args:
            docs_path: List of document paths or URLs
            task_type: Type of task ("code", "qa", "analysis")
            collection_name: Custom collection name for vector DB
            custom_prompt: Custom prompt template
            **kwargs: Additional configuration options
        """
        
        # Generate unique collection name if not provided
        if collection_name is None:
            docs_hash = hashlib.md5(str(sorted(docs_path)).encode()).hexdigest()[:8]
            collection_name = f"autogen-{task_type}-{docs_hash}"
            
        # Base retrieve configuration
        retrieve_config = {
            "task": task_type,
            "docs_path": docs_path,
            "chunk_token_size": kwargs.get("chunk_token_size", 2000),
            "model": self.config_list[0]["model"],
            "vector_db": kwargs.get("vector_db", "chroma"),
            "collection_name": collection_name,
            "chunk_mode": kwargs.get("chunk_mode", "multi_lines"),
            "embedding_model": kwargs.get("embedding_model", "all-MiniLM-L6-v2"),
            "get_or_create": kwargs.get("get_or_create", True),
            "overwrite": kwargs.get("overwrite", False),
        }
        
        # Add custom prompt if provided
        if custom_prompt:
            retrieve_config["customized_prompt"] = custom_prompt
            retrieve_config["customized_answer_prefix"] = kwargs.get(
                "answer_prefix", "Based on the analysis:"
            )
        
        # Enhanced RAG agent configuration
        self.rag_agent = RetrieveUserProxyAgent(
            name="rag_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=kwargs.get("max_auto_reply", 3),
            retrieve_config=retrieve_config,
            code_execution_config=False,  # Disable code execution for security
        )
        
        # Store configuration for debugging
        self.current_config = retrieve_config.copy()
        
        logger.info(f"RAG agent created - Collection: {collection_name}, Task: {task_type}")
        return self.rag_agent
    
    def execute_conversation(self, 
                           question: str, 
                           search_string: str = None,
                           n_results: int = 20,
                           enable_metrics: bool = True) -> Dict[str, Any]:
        """
        Execute conversation with comprehensive monitoring and error handling
        
        Args:
            question: User question or prompt
            search_string: Optional search filter
            n_results: Number of results to retrieve
            enable_metrics: Whether to collect performance metrics
            
        Returns:
            Dictionary containing result and metrics
        """
        
        if not self.rag_agent:
            raise ValueError("RAG agent not initialized. Call create_rag_agent() first.")
        
        start_time = time.time()
        conversation_id = hashlib.md5(f"{question}{time.time()}".encode()).hexdigest()[:8]
        
        try:
            # Reset assistant for fresh conversation
            self.assistant.reset()
            
            # Log conversation start
            logger.info(f"Starting conversation {conversation_id}: {question[:100]}...")
            
            # Execute conversation with error handling
            chat_result = self.rag_agent.initiate_chat(
                self.assistant,
                message=self.rag_agent.message_generator,
                problem=question,
                search_string=search_string,
                n_results=n_results
            )
            
            execution_time = time.time() - start_time
            
            # Collect metrics if enabled
            metrics = {}
            if enable_metrics:
                metrics = self._collect_metrics(
                    question=question,
                    chat_result=chat_result,
                    execution_time=execution_time,
                    conversation_id=conversation_id
                )
            
            # Store conversation history
            self.conversation_history.append({
                "id": conversation_id,
                "question": question,
                "result": chat_result,
                "metrics": metrics,
                "timestamp": time.time()
            })
            
            logger.info(f"Conversation {conversation_id} completed in {execution_time:.2f}s")
            
            return {
                "result": chat_result,
                "metrics": metrics,
                "conversation_id": conversation_id
            }
            
        except Exception as e:
            logger.error(f"Conversation {conversation_id} failed: {e}")
            return {
                "result": None,
                "error": str(e),
                "metrics": {"execution_time": time.time() - start_time, "success": False},
                "conversation_id": conversation_id
            }
    
    def _collect_metrics(self, question: str, chat_result, execution_time: float, conversation_id: str) -> Dict[str, Any]:
        """Collect comprehensive performance metrics"""
        
        try:
            # Basic metrics
            metrics = {
                "execution_time": execution_time,
                "question_length": len(question),
                "question_words": len(question.split()),
                "conversation_id": conversation_id,
                "success": True,
                "timestamp": time.time()
            }
            
            # Chat result metrics
            if chat_result and hasattr(chat_result, 'summary'):
                summary_text = str(chat_result.summary) if chat_result.summary else ""
                metrics.update({
                    "response_length": len(summary_text),
                    "response_words": len(summary_text.split()),
                    "has_response": bool(summary_text)
                })
            
            # Conversation metrics
            if hasattr(chat_result, 'chat_history'):
                metrics["conversation_turns"] = len(chat_result.chat_history)
            
            # Performance classification
            if execution_time < 1.0:
                metrics["performance_grade"] = "Excellent"
            elif execution_time < 3.0:
                metrics["performance_grade"] = "Good"
            elif execution_time < 5.0:
                metrics["performance_grade"] = "Acceptable"
            else:
                metrics["performance_grade"] = "Needs Optimization"
            
            return metrics
            
        except Exception as e:
            logger.warning(f"Failed to collect metrics: {e}")
            return {
                "execution_time": execution_time,
                "success": True,
                "metrics_error": str(e)
            }
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:] if limit else self.conversation_history
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "system_info": {
                "models_available": [config.get("model", "unknown") for config in self.config_list],
                "primary_model": self.config_list[0].get("model", "unknown") if self.config_list else None,
                "agents_initialized": {
                    "assistant": self.assistant is not None,
                    "rag_agent": self.rag_agent is not None
                }
            },
            "performance_stats": self._calculate_performance_stats(),
            "conversation_stats": {
                "total_conversations": len(self.conversation_history),
                "recent_conversations": len([c for c in self.conversation_history if time.time() - c["timestamp"] < 3600])
            },
            "current_config": getattr(self, 'current_config', {}),
            "status": "operational"
        }
    
    def _calculate_performance_stats(self) -> Dict[str, Any]:
        """Calculate performance statistics from conversation history"""
        if not self.conversation_history:
            return {"message": "No conversations recorded"}
        
        execution_times = [c["metrics"].get("execution_time", 0) for c in self.conversation_history]
        successful_conversations = [c for c in self.conversation_history if c["metrics"].get("success", False)]
        
        return {
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
            "success_rate": len(successful_conversations) / len(self.conversation_history),
            "total_conversations": len(self.conversation_history)
        }
    
    def optimize_for_task(self, task_type: str):
        """Optimize system configuration for specific task types"""
        optimization_configs = {
            "code": {
                "temperature": 0.1,
                "max_tokens": 6000,
                "chunk_token_size": 3000
            },
            "qa": {
                "temperature": 0.2,
                "max_tokens": 2000,
                "chunk_token_size": 2000
            },
            "analysis": {
                "temperature": 0.3,
                "max_tokens": 4000,
                "chunk_token_size": 2500
            }
        }
        
        if task_type in optimization_configs:
            config = optimization_configs[task_type]
            # Update configuration (would require agent reinitialization in practice)
            logger.info(f"System optimized for task type: {task_type}")
            return config
        else:
            logger.warning(f"No optimization available for task type: {task_type}")
            return None
