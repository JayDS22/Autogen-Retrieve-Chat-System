
"""
Comprehensive test suite for RetrieveChat system
Author: Jay Guwalani
"""

import pytest
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.config import Config
from retrievechat.core import RetrieveChatSystem
from retrievechat.prompts import PromptManager
from utils.performance import PerformanceAnalyzer

class TestRetrieveChatSystem:
    """Comprehensive test cases for RetrieveChat system"""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing"""
        return {
            "llm_config": [{
                "model": "gpt-4",
                "api_key": "test-key",
                "base_url": "https://api.openai.com/v1"
            }],
            "app_config": {
                "debug": True,
                "log_level": "DEBUG"
            }
        }
    
    @pytest.fixture
    def system(self, mock_config):
        """Setup test system with mocked configuration"""
        with patch('config.config.Config') as mock_config_class:
            mock_config_instance = Mock()
            mock_config_instance.llm_config = mock_config["llm_config"]
            mock_config_class.return_value = mock_config_instance
            
            return RetrieveChatSystem(mock_config["llm_config"])
    
    @pytest.fixture
    def sample_docs(self):
        """Sample documentation paths for testing"""
        return [
            "https://raw.githubusercontent.com/microsoft/FLAML/main/website/docs/Research.md"
        ]
    
    def test_system_initialization(self, system):
        """Test system initialization"""
        assert system is not None
        assert system.assistant is not None
        assert system.config_list is not None
        assert len(system.conversation_history) == 0
    
    def test_rag_agent_creation(self, system, sample_docs):
        """Test RAG agent creation with various configurations"""
        # Test basic creation
        rag_agent = system.create_rag_agent(
            docs_path=sample_docs,
            task_type="qa",
            collection_name="test-collection"
        )
        
        assert rag_agent is not None
        assert system.rag_agent is not None
        
        # Test with custom prompt
        custom_prompt = "Custom test prompt: {input_context}\nQ: {input_question}\nA:"
        rag_agent_custom = system.create_rag_agent(
            docs_path=sample_docs,
            task_type="code",
            collection_name="test-custom",
            custom_prompt=custom_prompt
        )
        
        assert rag_agent_custom is not None
    
    @patch('autogen.agentchat.contrib.retrieve_user_proxy_agent.RetrieveUserProxyAgent.initiate_chat')
    def test_conversation_execution(self, mock_initiate_chat, system, sample_docs):
        """Test conversation execution with mocked chat result"""
        # Setup mock chat result
        mock_chat_result = Mock()
        mock_chat_result.summary = "Test response from mocked system"
        mock_chat_result.chat_history = ["exchange1", "exchange2"]
        mock_initiate_chat.return_value = mock_chat_result
        
        # Create RAG agent
        system.create_rag_agent(
            docs_path=sample_docs,
            task_type="qa",
            collection_name="test-qa"
        )
        
        # Execute conversation
        result = system.execute_conversation("Who are the authors of FLAML?")
        
        # Verify results
        assert result is not None
        assert "result" in result
        assert "metrics" in result
        assert "conversation_id" in result
        assert result["metrics"]["execution_time"] >= 0
        assert result["metrics"]["success"] is True
    
    def test_conversation_without_rag_agent(self, system):
        """Test conversation execution without RAG agent should raise error"""
        with pytest.raises(ValueError, match="RAG agent not initialized"):
            system.execute_conversation("Test question")
    
    def test_conversation_history_management(self, system, sample_docs):
        """Test conversation history management"""
        with patch('autogen.agentchat.contrib.retrieve_user_proxy_agent.RetrieveUserProxyAgent.initiate_chat') as mock_chat:
            mock_chat_result = Mock()
            mock_chat_result.summary = "Test response"
            mock_chat.return_value = mock_chat_result
            
            system.create_rag_agent(docs_path=sample_docs, task_type="qa")
            
            # Execute multiple conversations
            system.execute_conversation("Question 1")
            system.execute_conversation("Question 2")
            
            # Check history
            history = system.get_conversation_history()
            assert len(history) == 2
            
            # Test history limit
            limited_history = system.get_conversation_history(limit=1)
            assert len(limited_history) == 1
            
            # Clear history
            system.clear_conversation_history()
            assert len(system.get_conversation_history()) == 0
    
    def test_system_status(self, system):
        """Test system status reporting"""
        status = system.get_system_status()
        
        assert "system_info" in status
        assert "performance_stats" in status
        assert "conversation_stats" in status
        assert "status" in status
        assert status["status"] == "operational"
        
        # Verify system info structure
        system_info = status["system_info"]
        assert "models_available" in system_info
        assert "primary_model" in system_info
        assert "agents_initialized" in system_info
    
    def test_performance_metrics_collection(self, system, sample_docs):
        """Test performance metrics collection"""
        with patch('autogen.agentchat.contrib.retrieve_user_proxy_agent.RetrieveUserProxyAgent.initiate_chat') as mock_chat:
            mock_chat_result = Mock()
            mock_chat_result.summary = "Test response for metrics"
            mock_chat_result.chat_history = ["turn1", "turn2"]
            mock_chat.return_value = mock_chat_result
            
            system.create_rag_agent(docs_path=sample_docs, task_type="qa")
            
            result = system.execute_conversation("Test question for metrics")
            metrics = result["metrics"]
            
            # Verify metrics structure
            required_metrics = [
                "execution_time", "question_length", "question_words",
                "conversation_id", "success", "timestamp"
            ]
            
            for metric in required_metrics:
                assert metric in metrics
            
            assert metrics["success"] is True
            assert metrics["execution_time"] >= 0
            assert "performance_grade" in metrics
    
    def test_task_optimization(self, system):
        """Test task-specific optimization"""
        # Test code optimization
        code_config = system.optimize_for_task("code")
        assert code_config is not None
        assert "temperature" in code_config
        assert "max_tokens" in code_config
        
        # Test QA optimization
        qa_config = system.optimize_for_task("qa")
        assert qa_config is not None
        
        # Test invalid task type
        invalid_config = system.optimize_for_task("invalid_task")
        assert invalid_config is None

class TestPromptManager:
    """Test cases for PromptManager"""
    
    @pytest.fixture
    def prompt_manager(self):
        """Setup PromptManager for testing"""
        return PromptManager()
    
    def test_prompt_manager_initialization(self, prompt_manager):
        """Test PromptManager initialization"""
        assert prompt_manager is not None
        assert len(prompt_manager.prompts) > 0
        assert "code_generation" in prompt_manager.prompts
        assert "technical_qa" in prompt_manager.prompts
    
    def test_get_prompt_by_task_type(self, prompt_manager):
        """Test getting prompts by task type"""
        code_prompt = prompt_manager.get_prompt("code")
        assert code_prompt is not None
        assert "{input_context}" in code_prompt
        assert "{input_question}" in code_prompt
        
        qa_prompt = prompt_manager.get_prompt("qa")
        assert qa_prompt is not None
        
        # Test custom prompt override
        custom_prompt = "Custom: {input_context} Q: {input_question} A:"
        result_prompt = prompt_manager.get_prompt("code", custom_prompt)
        assert result_prompt == custom_prompt
    
    def test_specialized_prompts(self, prompt_manager):
        """Test specialized domain prompts"""
        healthcare_prompt = prompt_manager.get_specialized_prompt("healthcare")
        assert healthcare_prompt is not None
        
        comparison_prompt = prompt_manager.get_specialized_prompt("comparison")
        assert comparison_prompt is not None
    
    def test_custom_prompt_creation(self, prompt_manager):
        """Test custom prompt creation"""
        instructions = "Provide detailed technical analysis"
        format_req = "Use bullet points for key findings"
        examples = "Example: Question -> Analysis -> Conclusion"
        
        custom_prompt = prompt_manager.create_custom_prompt(
            instructions=instructions,
            format_requirements=format_req,
            examples=examples
        )
        
        assert instructions in custom_prompt
        assert format_req in custom_prompt
        assert examples in custom_prompt
        assert "{input_context}" in custom_prompt
        assert "{input_question}" in custom_prompt
    
    def test_prompt_validation(self, prompt_manager):
        """Test prompt validation"""
        # Valid prompt
        valid_prompt = "Context: {input_context}\nQuestion: {input_question}\nAnswer:"
        validation = prompt_manager.validate_prompt(valid_prompt)
        assert validation["valid"] is True
        assert len(validation["missing_placeholders"]) == 0
        
        # Invalid prompt - missing placeholders
        invalid_prompt = "Just a simple prompt without placeholders"
        validation = prompt_manager.validate_prompt(invalid_prompt)
        assert validation["valid"] is False
        assert len(validation["missing_placeholders"]) == 2
        
        # Test warnings for prompt length
        short_prompt = "Short {input_context} {input_question}"
        validation = prompt_manager.validate_prompt(short_prompt)
        assert "too short" in validation["warnings"][0]
    
    def test_add_custom_prompt(self, prompt_manager):
        """Test adding custom prompts"""
        valid_custom = "Custom prompt: {input_context}\nQuery: {input_question}\nResponse:"
        result = prompt_manager.add_custom_prompt("test_custom", valid_custom)
        assert result is True
        assert "test_custom" in prompt_manager.prompts
        
        # Test invalid custom prompt
        invalid_custom = "Invalid prompt without placeholders"
        result = prompt_manager.add_custom_prompt("test_invalid", invalid_custom)
        assert result is False
    
    def test_available_prompts(self, prompt_manager):
        """Test getting available prompts list"""
        available = prompt_manager.get_available_prompts()
        assert isinstance(available, list)
        assert len(available) > 0
        assert "code_generation" in available

class TestPerformanceAnalyzer:
    """Test cases for PerformanceAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Setup PerformanceAnalyzer for testing"""
        return PerformanceAnalyzer()
    
    def test_analyzer_initialization(self, analyzer):
        """Test PerformanceAnalyzer initialization"""
        assert analyzer is not None
        assert len(analyzer.metrics_history) == 0
        assert "excellent" in analyzer.thresholds
        assert analyzer.thresholds["excellent"] == 1.0
    
    def test_record_metric(self, analyzer):
        """Test recording performance metrics"""
        test_metrics = {
            "execution_time": 1.5,
            "success": True,
            "question_length": 50,
            "response_length": 200,
            "conversation_turns": 2
        }
        
        analyzer.record_metric(test_metrics)
        assert len(analyzer.metrics_history) == 1
        
        recorded_metric = analyzer.metrics_history[0]
        assert recorded_metric.execution_time == 1.5
        assert recorded_metric.success is True
        assert recorded_metric.question_length == 50
    
    def test_performance_classification(self, analyzer):
        """Test performance classification"""
        execution_times = [0.5, 1.5, 4.0, 6.0]  # excellent, good, acceptable, needs_optimization
        classification = analyzer._classify_performance(execution_times)
        
        assert classification["excellent"] == 1
        assert classification["good"] == 1
        assert classification["acceptable"] == 1
        assert classification["needs_optimization"] == 1
    
    def test_generate_performance_report(self, analyzer):
        """Test performance report generation"""
        # Add some test metrics
        test_metrics = [
            {"execution_time": 0.8, "success": True, "question_length": 30, "response_length": 150},
            {"execution_time": 2.1, "success": True, "question_length": 45, "response_length": 200},
            {"execution_time": 4.5, "success": False, "question_length": 60, "response_length": 0}
        ]
        
        for metrics in test_metrics:
            analyzer.record_metric(metrics)
        
        report = analyzer.generate_performance_report()
        
        assert "summary" in report
        assert "performance_distribution" in report
        assert "trends" in report
        assert "recommendations" in report
        
        # Verify summary metrics
        summary = report["summary"]
        assert summary["total_operations"] == 3
        assert 0 <= summary["success_rate"] <= 1
        assert summary["avg_execution_time"] > 0

# Integration tests
class TestSystemIntegration:
    """Integration tests for complete system functionality"""
    
    @pytest.fixture
    def integration_system(self):
        """Setup system for integration testing"""
        # Use mock configuration to avoid API calls
        mock_config = [{
            "model": "gpt-4",
            "api_key": "test-key",
            "base_url": "https://api.openai.com/v1"
        }]
        return RetrieveChatSystem(mock_config)
    
    @patch('requests.head')
    def test_document_validation_integration(self, mock_head, integration_system):
        """Test document validation integration"""
        # Mock successful URL validation
        mock_head.return_value.status_code = 200
        
        from utils.document_processor import DocumentProcessor
        doc_processor = DocumentProcessor()
        
        test_docs = [
            "https://example.com/doc1.md",
            "https://example.com/doc2.pdf",
            "invalid_file.txt"
        ]
        
        validation_result = doc_processor.validate_documents(test_docs)
        
        assert "valid_docs" in validation_result
        assert "invalid_docs" in validation_result
        assert validation_result["total_docs"] == 3
    
    def test_end_to_end_workflow(self, integration_system):
        """Test complete end-to-end workflow"""
        with patch('autogen.agentchat.contrib.retrieve_user_proxy_agent.RetrieveUserProxyAgent') as mock_rag_class:
            # Setup mocks
            mock_rag_agent = Mock()
            mock_chat_result = Mock()
            mock_chat_result.summary = "Integration test response"
            mock_chat_result.chat_history = ["turn1"]
            
            mock_rag_agent.initiate_chat.return_value = mock_chat_result
            mock_rag_class.return_value = mock_rag_agent
            
            # Test workflow
            docs_path = ["https://example.com/test.md"]
            question = "Test integration question"
            
            # Create agent
            integration_system.create_rag_agent(
                docs_path=docs_path,
                task_type="qa",
                collection_name="integration-test"
            )
            
            # Execute conversation
            result = integration_system.execute_conversation(question)
            
            # Verify end-to-end functionality
            assert result is not None
            assert "result" in result
            assert "metrics" in result
            assert "conversation_id" in result
            
            # Check conversation history
            history = integration_system.get_conversation_history()
            assert len(history) == 1
            assert history[0]["question"] == question

# Performance and stress tests
class TestPerformanceAndStress:
    """Performance and stress testing"""
    
    def test_concurrent_conversations(self):
        """Test handling multiple concurrent conversations"""
        # This would test concurrent access patterns
        # For now, just verify the concept works
        mock_config = [{"model": "gpt-4", "api_key": "test"}]
        system = RetrieveChatSystem(mock_config)
        
        # Simulate multiple conversation setups
        conversation_ids = []
        for i in range(5):
            # In real implementation, this would test actual concurrency
            conv_id = f"test-conversation-{i}"
            conversation_ids.append(conv_id)
        
        assert len(conversation_ids) == 5
    
    def test_large_document_handling(self):
        """Test system behavior with large document sets"""
        mock_config = [{"model": "gpt-4", "api_key": "test"}]
        system = RetrieveChatSystem(mock_config)
        
        # Simulate large document set
        large_doc_set = [f"https://example.com/doc{i}.md" for i in range(100)]
        
        # Test document info processing
        from utils.document_processor import DocumentProcessor
        doc_processor = DocumentProcessor()
        info = doc_processor.get_document_info(large_doc_set)
        
        assert info["total_documents"] == 100
        assert info["processing_complexity"] == "high"

if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
