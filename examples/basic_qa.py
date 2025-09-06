# examples/basic_qa.py
"""
Basic Q&A example with AutoGen RetrieveChat
Author: Jay Guwalani
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from retrievechat.core import RetrieveChatSystem
from config.config import Config

def run_basic_qa_example():
    """Run basic Q&A example"""
    
    # Initialize system
    config = Config()
    system = RetrieveChatSystem(config.llm_config)
    
    # Create RAG agent with sample documentation
    docs_path = [
        "https://raw.githubusercontent.com/microsoft/FLAML/main/website/docs/Research.md"
    ]
    
    system.create_rag_agent(
        docs_path=docs_path,
        task_type="qa",
        collection_name="basic-qa-demo"
    )
    
    # Ask questions
    questions = [
        "Who are the authors of FLAML?",
        "What is the main contribution of FLAML?",
        "How does FLAML optimize hyperparameters?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\nQuestion {i}: {question}")
        print("-" * 50)
        
        result = system.execute_conversation(question)
        print(f"Response time: {result['metrics']['execution_time']:.2f}s")
        print(f"Answer: {result['result'].summary}")

if __name__ == "__main__":
    run_basic_qa_example()
