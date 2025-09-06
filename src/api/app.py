"""
Flask API for AutoGen RetrieveChat system
Author: Jay Guwalani
"""

import logging
import sys
import os
from typing import Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import time

from config.config import Config
from retrievechat.core import RetrieveChatSystem
from utils.logger import setup_logger
from utils.performance import PerformanceAnalyzer

# Initialize logging
logger = setup_logger(__name__)

def create_app(config_override: Dict = None) -> Flask:
    """Application factory pattern"""
    
    app = Flask(__name__)
    
    # Load configuration
    config = Config()
    if config_override:
        config.app_config.update(config_override)
    
    # Configure Flask
    app.config.update({
        'SECRET_KEY': config.app_config['secret_key'],
        'DEBUG': config.app_config['debug'],
        'CORS_ORIGINS': config.app_config['cors_origins']
    })
    
    # Enable CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Initialize system components
    retrievechat_system = RetrieveChatSystem(config.llm_config)
    performance_analyzer = PerformanceAnalyzer()
    
    # Request timing middleware
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        return response
    
    # Error handlers
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        logger.error(f"HTTP Error {e.code}: {e.description}")
        return jsonify({
            "error": e.description,
            "code": e.code
        }), e.code
    
    @app.errorhandler(Exception)
    def handle_general_exception(e):
        logger.error(f"Unhandled exception: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e) if app.config['DEBUG'] else "An error occurred"
        }), 500
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        try:
            status = retrievechat_system.get_system_status()
            return jsonify({
                "status": "healthy",
                "service": "autogen-retrievechat",
                "version": "1.0.0",
                "timestamp": time.time(),
                "system_status": status
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                "status": "unhealthy",
                "error": str(e)
            }), 503
    
    # Main chat endpoint
    @app.route('/chat', methods=['POST'])
    def chat():
        """Main chat endpoint for conversations"""
        try:
            # Validate request
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json"}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "Empty request body"}), 400
            
            # Extract parameters
            question = data.get('question')
            docs_path = data.get('docs_path', [])
            task_type = data.get('task_type', 'qa')
            search_string = data.get('search_string')
            n_results = data.get('n_results', 20)
            custom_prompt = data.get('custom_prompt')
            
            # Validate required fields
            if not question:
                return jsonify({"error": "Question is required"}), 400
            
            if not docs_path:
                return jsonify({"error": "Documents path is required"}), 400
            
            # Create RAG agent
            try:
                retrievechat_system.create_rag_agent(
                    docs_path=docs_path,
                    task_type=task_type,
                    custom_prompt=custom_prompt
                )
            except Exception as e:
                logger.error(f"Failed to create RAG agent: {e}")
                return jsonify({
                    "error": "Failed to initialize document processing",
                    "details": str(e)
                }), 500
            
            # Execute conversation
            result = retrievechat_system.execute_conversation(
                question=question,
                search_string=search_string,
                n_results=n_results
            )
            
            # Handle errors in conversation
            if "error" in result:
                return jsonify({
                    "error": "Conversation failed",
                    "details": result["error"],
                    "conversation_id": result.get("conversation_id")
                }), 500
            
            # Record performance metrics
            performance_analyzer.record_metric(result["metrics"])
            
            # Return successful response
            return jsonify({
                "answer": str(result['result'].summary) if result['result'].summary else "No response generated",
                "conversation_id": result["conversation_id"],
                "metrics": result["metrics"],
                "success": True
            })
            
        except Exception as e:
            logger.error(f"Chat endpoint error: {e}")
            return jsonify({
                "error": "Internal server error",
                "message": str(e) if app.config['DEBUG'] else "An error occurred processing your request"
            }), 500
    
    # Code generation endpoint
    @app.route('/generate-code', methods=['POST'])
    def generate_code():
        """Specialized endpoint for code generation"""
        try:
            data = request.get_json()
            
            code_request = data.get('request')
            docs_path = data.get('docs_path', [])
            language = data.get('language', 'python')
            requirements = data.get('requirements', [])
            
            if not code_request or not docs_path:
                return jsonify({"error": "Code request and docs_path are required"}), 400
            
            # Enhanced prompt for code generation
            enhanced_request = f"""
            Generate {language} code for: {code_request}
            
            Requirements:
            {chr(10).join(f"- {req}" for req in requirements)}
            
            Please include:
            - Proper error handling
            - Meaningful comments
            - Best practices for {language}
            - Production-ready code structure
            """
            
            # Create RAG agent for code generation
            retrievechat_system.create_rag_agent(
                docs_path=docs_path,
                task_type="code",
                collection_name=f"code-gen-{int(time.time())}"
            )
            
            # Execute code generation
            result = retrievechat_system.execute_conversation(
                question=enhanced_request,
                search_string=f"{language} code"
            )
            
            return jsonify({
                "generated_code": str(result['result'].summary),
                "language": language,
                "conversation_id": result["conversation_id"],
                "metrics": result["metrics"]
            })
            
        except Exception as e:
            logger.error(f"Code generation error: {e}")
            return jsonify({"error": str(e)}), 500
    
    # Performance analytics endpoint
    @app.route('/analytics', methods=['GET'])
    def analytics():
        """Get performance analytics"""
        try:
            report = performance_analyzer.generate_performance_report()
            system_status = retrievechat_system.get_system_status()
            
            return jsonify({
                "performance_report": report,
                "system_status": system_status,
                "timestamp": time.time()
            })
            
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return jsonify({"error": str(e)}), 500
    
    # Configuration endpoint
    @app.route('/config', methods=['GET'])
    def get_config():
        """Get system configuration (sanitized)"""
        try:
            sanitized_config = {
                "models_available": config.get_model_names(),
                "supported_formats": [
                    'txt', 'json', 'csv', 'tsv', 'md', 'html', 'htm',
                    'rtf', 'rst', 'jsonl', 'log', 'xml', 'yaml', 'yml', 'pdf'
                ],
                "task_types": ["code", "qa", "analysis", "multihop"],
                "environment": config.app_config["environment"],
                "version": "1.0.0"
            }
            
            return jsonify(sanitized_config)
            
        except Exception as e:
            logger.error(f"Config endpoint error: {e}")
            return jsonify({"error": str(e)}), 500
    
    logger.info("Flask application created successfully")
    return app

# Create application instance
app = create_app()

def main():
    """Main entry point for running the application"""
    config = Config()
    app.run(
        host=config.app_config['api_host'],
        port=config.app_config['api_port'],
        debug=config.app_config['debug']
    )

if __name__ == '__main__':
    main()
