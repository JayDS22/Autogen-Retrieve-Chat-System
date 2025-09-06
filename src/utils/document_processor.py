"""
Document processing utilities for AutoGen RetrieveChat system
Author: Jay Guwalani
"""

import logging
import hashlib
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
import mimetypes
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document processing and validation for the RAG system"""
    
    def __init__(self):
        self.supported_formats = [
            'txt', 'json', 'csv', 'tsv', 'md', 'html', 'htm', 
            'rtf', 'rst', 'jsonl', 'log', 'xml', 'yaml', 'yml', 'pdf'
        ]
        self.processed_docs = {}
        logger.info("DocumentProcessor initialized")
    
    def validate_documents(self, docs_path: List[str]) -> Dict[str, Any]:
        """Validate document paths and accessibility"""
        
        validation_result = {
            "valid_docs": [],
            "invalid_docs": [],
            "warnings": [],
            "total_docs": len(docs_path)
        }
        
        for doc_path in docs_path:
            try:
                if self._is_url(doc_path):
                    if self._validate_url(doc_path):
                        validation_result["valid_docs"].append(doc_path)
                    else:
                        validation_result["invalid_docs"].append({
                            "path": doc_path,
                            "error": "URL not accessible"
                        })
                else:
                    if self._validate_file_path(doc_path):
                        validation_result["valid_docs"].append(doc_path)
                    else:
                        validation_result["invalid_docs"].append({
                            "path": doc_path,
                            "error": "File not found or unsupported format"
                        })
                        
            except Exception as e:
                validation_result["invalid_docs"].append({
                    "path": doc_path,
                    "error": str(e)
                })
        
        # Add warnings for common issues
        if len(validation_result["valid_docs"]) == 0:
            validation_result["warnings"].append("No valid documents found")
        elif len(validation_result["valid_docs"]) > 50:
            validation_result["warnings"].append("Large number of documents may impact performance")
        
        logger.info(f"Document validation: {len(validation_result['valid_docs'])}/{len(docs_path)} valid")
        return validation_result
    
    def _is_url(self, path: str) -> bool:
        """Check if path is a URL"""
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL accessibility"""
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
    
    def _validate_file_path(self, file_path: str) -> bool:
        """Validate local file path and format"""
        try:
            path = Path(file_path)
            if not path.exists():
                return False
            
            # Check file extension
            extension = path.suffix.lower().lstrip('.')
            return extension in self.supported_formats
            
        except:
            return False
    
    def get_document_info(self, docs_path: List[str]) -> Dict[str, Any]:
        """Get detailed information about documents"""
        
        info = {
            "total_documents": len(docs_path),
            "document_types": {},
            "estimated_size": 0,
            "processing_complexity": "low"
        }
        
        for doc_path in docs_path:
            try:
                if self._is_url(doc_path):
                    doc_type = "url"
                    info["document_types"][doc_type] = info["document_types"].get(doc_type, 0) + 1
                else:
                    path = Path(doc_path)
                    extension = path.suffix.lower().lstrip('.')
                    info["document_types"][extension] = info["document_types"].get(extension, 0) + 1
                    
                    if path.exists():
                        info["estimated_size"] += path.stat().st_size
                        
            except Exception as e:
                logger.warning(f"Error getting info for {doc_path}: {e}")
        
        # Determine processing complexity
        if info["total_documents"] > 20:
            info["processing_complexity"] = "high"
        elif info["total_documents"] > 5:
            info["processing_complexity"] = "medium"
            
        return info
    
    def create_document_hash(self, docs_path: List[str]) -> str:
        """Create a unique hash for a set of documents"""
        content = str(sorted(docs_path))
        return hashlib.md5(content.encode()).hexdigest()[:16]
