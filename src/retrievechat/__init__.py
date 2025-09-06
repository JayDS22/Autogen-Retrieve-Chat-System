"""
AutoGen RetrieveChat package for advanced RAG capabilities
Author: Jay Guwalani
"""

__version__ = "1.0.0"
__author__ = "Jay Guwalani"
__email__ = "jguwalan@umd.edu"

from .core import RetrieveChatSystem
from .prompts import PromptManager
from .utils import DocumentProcessor, VectorDBManager

__all__ = [
    "RetrieveChatSystem",
    "PromptManager", 
    "DocumentProcessor",
    "VectorDBManager"
]
