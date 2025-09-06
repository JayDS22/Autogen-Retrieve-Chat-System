"""
Test suite for RetrieveChat system
Author: Jay Guwalani
"""

import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from retrievechat.core import RetrieveChatSystem
from config.config import Config

class TestRetrieveChatSystem:
    """Test cases for RetrieveChat system"""
    
    @pytest.fixture
    def system(self):
        """Setup test system"""
        config = Config()
        return RetrieveChatSystem(config.llm_config)
    
    @pytest.fixture
    def sample_docs(self):
        """Sample documentation paths"""
        return [
            "https://raw.githubusercontent.com/microsoft/FLAML/main/website/docs/Research.md"
        ]
    
    def test_system_initialization(self, system):
        """Test system initialization"""
        assert system is not None
        assert system.assistant is not None
        assert system.config_list is not None
    
    def test_rag_agent_creation(self, system, sample_docs):
        """Test RAG agent creation"""
        rag_agent = system.create_rag_agent(
            docs_path=sample_docs,
            task_type="qa",
            collection_name="test-collection"
        )
        
        assert rag_agent is not None
        assert system.rag_agent is not None
    
    def test_conversation_execution(self, system, sample_docs):
        """Test conversation execution"""
        system.create_rag_agent(
            docs_path=sample_docs,
            task_type="qa",
            collection_name="test-qa"
        )
        
        result = system.execute_conversation("Who are the authors of FLAML?")
        
        assert result is not None
        assert "result" in result
        assert "metrics" in result
        assert result["metrics"]["execution_time"] > 0
    
    def test_code_generation(self, system):
        """Test code generation capabilities"""
        docs_path = [
            "https://raw.githubusercontent.com/microsoft/FLAML/main/website/docs/Examples/Integrate%20-%20Spark.md"
        ]
        
        system.create_rag_agent(
            docs_path=docs_path,
            task_type="code",
            collection_name="test-code"
        )
        
        result = system.execute_conversation("Generate FLAML classification code")
        
        assert result is not None
        assert result["metrics"]["execution_time"] > 0
    
    def test_custom_prompt(self, system, sample_docs):
        """Test custom prompt functionality"""
        custom_prompt = "Answer concisely: {input_context}\nQ: {input_question}\nA:"
        
        system.create_rag_agent(
            docs_path=sample_docs,
            task_type="qa",
            collection_name="test-custom",
            custom_prompt=custom_prompt
        )
        
        result = system.execute_conversation("What is FLAML?")
        
        assert result is not None
        assert result["metrics"]["execution_time"] > 0
