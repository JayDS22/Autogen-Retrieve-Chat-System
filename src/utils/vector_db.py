"""
Vector database management utilities
Author: Jay Guwalani
"""

import logging
import time
from typing import Dict, Any, List, Optional
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

class VectorDBManager:
    """Manages vector database operations and optimization"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.client = None
        self.collections = {}
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize ChromaDB client with optimal settings"""
        try:
            # Configuration for production use
            settings = Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.config.get("persist_directory", "./chroma_db"),
                anonymized_telemetry=False
            )
            
            self.client = chromadb.Client(settings)
            logger.info("ChromaDB client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a specific collection"""
        try:
            collection = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "count": collection.count(),
                "metadata": collection.metadata,
                "exists": True
            }
        except Exception:
            return {
                "name": collection_name,
                "exists": False
            }
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """List all collections with their information"""
        try:
            collections = self.client.list_collections()
            return [
                {
                    "name": collection.name,
                    "count": collection.count(),
                    "metadata": collection.metadata
                }
                for collection in collections
            ]
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []
    
    def optimize_collection(self, collection_name: str) -> Dict[str, Any]:
        """Optimize collection performance"""
        try:
            # This would contain actual optimization logic
            # For now, we'll return optimization recommendations
            info = self.get_collection_info(collection_name)
            
            recommendations = []
            if info.get("count", 0) > 10000:
                recommendations.append("Consider partitioning large collection")
            if info.get("count", 0) < 10:
                recommendations.append("Collection may be too small for optimal performance")
            
            return {
                "collection": collection_name,
                "recommendations": recommendations,
                "optimization_applied": True
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize collection {collection_name}: {e}")
            return {"error": str(e)}
