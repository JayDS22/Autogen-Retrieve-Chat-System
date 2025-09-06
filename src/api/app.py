"""
Flask API for RetrieveChat system
"""

from flask import Flask, request, jsonify
import logging
from retrievechat.core import RetrieveChatSystem
from config.config import Config

app = Flask(__name__)
config = Config()
system = RetrieveChatSystem(config.llm_config)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "retrievechat"})

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint"""
    try:
        data = request.json
        question = data.get('question')
        docs_path = data.get('docs_path', [])
        task_type = data.get('task_type', 'qa')
        
        if not question or not docs_path:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Create RAG agent
        system.create_rag_agent(
            docs_path=docs_path,
            task_type=task_type
        )
        
        # Execute conversation
        result = system.execute_conversation(question)
        
        return jsonify({
            "answer": str(result['result'].summary),
            "metrics": result['metrics']
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=config.app_config['debug'])
