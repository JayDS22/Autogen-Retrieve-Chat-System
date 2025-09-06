# docs/api_documentation.md
# AutoGen RetrieveChat API Documentation

## Overview

The AutoGen RetrieveChat system provides a RESTful API for advanced conversational AI capabilities with retrieval-augmented generation.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API uses API keys configured in environment variables. Future versions will include token-based authentication.

## Endpoints

### Health Check

**GET** `/health`

Check system health and status.

**Response:**
```json
{
  "status": "healthy",
  "service": "autogen-retrievechat", 
  "version": "1.0.0",
  "timestamp": 1640995200.0,
  "system_status": {
    "system_info": {...},
    "performance_stats": {...}
  }
}
```

### Chat

**POST** `/chat`

Execute a conversation with document-based context.

**Request Body:**
```json
{
  "question": "Your question here",
  "docs_path": ["https://example.com/doc1.md", "path/to/doc2.pdf"],
  "task_type": "qa",
  "search_string": "optional search filter",
  "n_results": 20,
  "custom_prompt": "optional custom prompt template"
}
```

**Response:**
```json
{
  "answer": "AI generated response",
  "conversation_id": "abc123",
  "metrics": {
    "execution_time": 2.5,
    "response_length": 150,
    "performance_grade": "Good"
  },
  "success": true
}
```

### Code Generation

**POST** `/generate-code`

Specialized endpoint for code generation tasks.

**Request Body:**
```json
{
  "request": "Generate Python code for data processing",
  "docs_path": ["https://example.com/api_docs.md"],
  "language": "python",
  "requirements": ["error handling", "logging", "type hints"]
}
```

**Response:**
```json
{
  "generated_code": "# Generated Python code...",
  "language": "python",
  "conversation_id": "def456",
  "metrics": {...}
}
```

### Analytics

**GET** `/analytics`

Get performance analytics and system metrics.

**Response:**
```json
{
  "performance_report": {
    "summary": {...},
    "performance_distribution": {...},
    "trends": {...},
    "recommendations": [...]
  },
  "system_status": {...},
  "timestamp": 1640995200.0
}
```

### Configuration

**GET** `/config`

Get system configuration information.

**Response:**
```json
{
  "models_available": ["gpt-4", "gpt-3.5-turbo"],
  "supported_formats": ["txt", "md", "pdf", "json", ...],
  "task_types": ["code", "qa", "analysis", "multihop"],
  "environment": "production",
  "version": "1.0.0"
}
```

## Error Responses

All endpoints return appropriate HTTP status codes and error messages:

```json
{
  "error": "Error description",
  "code": 400,
  "details": "Additional error details"
}
```

## Rate Limiting

- Default: 100 requests per hour per client
- Configurable via environment variables
- Headers include rate limit information

## Examples

### Python Client Example

```python
import requests

# Basic chat request
response = requests.post('http://localhost:8000/chat', json={
    "question": "What are the benefits of AutoML?",
    "docs_path": ["https://example.com/automl_guide.md"],
    "task_type": "qa"
})

if response.status_code == 200:
    result = response.json()
    print(f"Answer: {result['answer']}")
    print(f"Time: {result['metrics']['execution_time']}s")
```

### cURL Example

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Generate a Python data pipeline",
    "docs_path": ["https://example.com/pipeline_docs.md"],
    "task_type": "code"
  }'
```
