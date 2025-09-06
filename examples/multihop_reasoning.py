
"""
Multi-hop reasoning example with custom prompts
Author: Jay Guwalani
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from retrievechat.core import RetrieveChatSystem
from config.config import Config

MULTIHOP_PROMPT = """
You are an advanced AI assistant that excels at multi-hop reasoning. When answering questions:

1. Break down complex queries into component parts
2. Identify information needed for each part
3. Synthesize information from multiple sources
4. Provide step-by-step reasoning
5. Draw logical conclusions

Format your response as:
Analysis:
- Component 1: [analysis]
- Component 2: [analysis]
- Synthesis: [combination of information]

Conclusion: [final answer with reasoning]

Context: {input_context}
Question: {input_question}
Response:
"""

def run_multihop_reasoning_example():
    """Run multi-hop reasoning example"""
    
    # Initialize system
    config = Config()
    system = RetrieveChatSystem(config.llm_config)
    
    # Create RAG agent with custom prompt
    docs_path = [
        "https://raw.githubusercontent.com/microsoft/FLAML/main/website/docs/Research.md",
        "https://raw.githubusercontent.com/microsoft/FLAML/main/website/docs/Examples/Integrate%20-%20Spark.md"
    ]
    
    system.create_rag_agent(
        docs_path=docs_path,
        task_type="qa",
        collection_name="multihop-demo",
        custom_prompt=MULTIHOP_PROMPT
    )
    
    # Complex reasoning questions
    complex_questions = [
        "How do the research contributions of FLAML's authors relate to its Spark integration capabilities?",
        "What are the computational trade-offs between FLAML's optimization techniques and traditional approaches?",
        "How does FLAML's architecture support both local and distributed computing paradigms?"
    ]
    
    for i, question in enumerate(complex_questions, 1):
        print(f"\nComplex Question {i}: {question}")
        print("=" * 100)
        
        result = system.execute_conversation(question, n_results=40)
        print(f"Reasoning time: {result['metrics']['execution_time']:.2f}s")
        print("Multi-hop Analysis:")
        print(result['result'].summary)

if __name__ == "__main__":
    run_multihop_reasoning_example()
