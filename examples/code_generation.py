
"""
Code generation example with AutoGen RetrieveChat
Author: Jay Guwalani
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from retrievechat.core import RetrieveChatSystem
from config.config import Config

def run_code_generation_example():
    """Run code generation example"""
    
    # Initialize system
    config = Config()
    system = RetrieveChatSystem(config.llm_config)
    
    # Create RAG agent for code generation
    docs_path = [
        "https://raw.githubusercontent.com/microsoft/FLAML/main/website/docs/Examples/Integrate%20-%20Spark.md"
    ]
    
    system.create_rag_agent(
        docs_path=docs_path,
        task_type="code",
        collection_name="code-gen-demo"
    )
    
    # Code generation requests
    code_requests = [
        "Generate Python code for FLAML classification with Spark parallel training and 30-second time budget",
        "Create a complete FLAML regression example with error handling and logging",
        "Show how to use FLAML's hyperparameter optimization with custom metrics"
    ]
    
    for i, request in enumerate(code_requests, 1):
        print(f"\nCode Request {i}: {request}")
        print("=" * 80)
        
        result = system.execute_conversation(request, search_string="spark")
        print(f"Generation time: {result['metrics']['execution_time']:.2f}s")
        print("Generated Code:")
        print(result['result'].summary)

if __name__ == "__main__":
    run_code_generation_example()
