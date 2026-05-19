import sys
sys.path.append('.')

from application import app

def test_hello_world():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode() == 'Hello, World!'

def test_hello_world_2():
    client = app.test_client()
    response = client.post('/')
    assert response.status_code == 405

def test_blog_articles():
    client = app.test_client()
    response = client.post('/blogs',
        json={
            "title": "Test Article",
            "content": "This is a test."
        },
        headers={"X-API-Key": "api-key-123"}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == "Test Article"
