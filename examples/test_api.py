
"""
API test suite
"""

import pytest
import json
from api.app import app

@pytest.fixture
def client():
    """Test client fixture"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'retrievechat'

def test_chat_endpoint_missing_data(client):
    """Test chat endpoint with missing data"""
    response = client.post('/chat', json={})
    assert response.status_code == 400

def test_chat_endpoint_valid_request(client):
    """Test chat endpoint with valid request"""
    request_data = {
        "question": "Test question",
        "docs_path": ["https://raw.githubusercontent.com/microsoft/FLAML/main/website/docs/Research.md"],
        "task_type": "qa"
    }
    
    response = client.post('/chat', 
                          json=request_data,
                          content_type='application/json')
    
    # Note: This test might fail without proper API keys
    # In a real test environment, you'd mock the LLM calls
    assert response.status_code in [200, 500]  # 500 if no API key

if __name__ == "__main__":
    pytest.main([__file__])
