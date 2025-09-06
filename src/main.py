# src/main.py
"""
AutoGen RetrieveChat System - Main Application
Author: Jay Guwalani
"""

import logging
import os
from typing import Dict, List, Any
import time

from retrievechat.core import RetrieveChatSystem
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Main application entry point"""
    
    logger.info("Starting AutoGen RetrieveChat System")
    
    try:
        # Initialize configuration
        config = Config()
        
        # Initialize RetrieveChat system
        system = RetrieveChatSystem(config.llm_config)
        
        # Example usage
        demo_code_generation(system)
        demo_question_answering(system)
        
        logger.info("Application completed successfully")
        
    except Exception as e:
        logger.error(f"Application failed: {e}")
        raise

def demo_code_generation(system: RetrieveChatSystem):
    """Demonstrate code generation capabilities"""
    
    docs_path = [
        "https://raw.githubusercontent.com/microsoft/FLAML/main/website/docs/Examples/Integrate%20-%20Spark.md"
    ]
    
    rag_agent = system.create_rag_agent(
        docs_path=docs_path,
        task_type="code",
        collection_name="flaml-demo"
    )
    
    question = "Generate Python code for FLAML classification with Spark parallel training"
    
    result = system.execute_conversation(question)
    logger.info(f"Code generation completed in {result['metrics']['execution_time']:.2f}s")

def demo_question_answering(system: RetrieveChatSystem):
    """Demonstrate Q&A capabilities"""
    
    docs_path = [
        "https://raw.githubusercontent.com/microsoft/FLAML/main/website/docs/Research.md"
    ]
    
    rag_agent = system.create_rag_agent(
        docs_path=docs_path,
        task_type="qa",
        collection_name="research-qa"
    )
    
    question = "Who are the authors of FLAML?"
    
    result = system.execute_conversation(question)
    logger.info(f"Q&A completed in {result['metrics']['execution_time']:.2f}s")

if __name__ == "__main__":
    main()
