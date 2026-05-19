import sys
sys.path.append('.')

import pytest
from application import app
from models.user import get_db

@pytest.fixture(autouse=True)
def setup_and_teardown():
    conn = get_db()
    conn.execute('DELETE FROM users')
    conn.commit()
    conn.close()
    yield
    conn = get_db()
    conn.execute('DELETE FROM users')
    conn.commit()
    conn.close()


def test_get_user():
    client = app.test_client()
    username = "bob"
    password = "pass"
    resp = client.post('/users', json={"username": username, "password": password}, headers={"X-API-Key": "api-key-123"})
    assert resp.status_code == 201

    # Récupération de la liste avec authentification
    resp = client.get('/users', headers={"X-API-Key": "api-key-123"})
    assert resp.status_code == 200
    users = resp.get_json()
    assert any(u['username'] == username for u in users)
    resp = client.get('/users', follow_redirects=True, headers={"X-API-Key": "api-key-123"})
    assert resp.status_code == 200
    users = resp.get_json()
    assert any(u['username'] == 'bob' for u in users)


def test_update_user():
    client = app.test_client()
    username = "carol"
    password = "old"
    client.post('/users', json={"username": username, "password": password}, headers={"X-API-Key": "api-key-123"})
    users = client.get('/users', headers={"X-API-Key": "api-key-123"}).get_json()
    user_id = [u['id'] for u in users if u['username'] == username][0]
    resp = client.put(f'/users/{user_id}', json={"username": username, "password": "newpass"}, headers={"X-API-Key": "api-key-123"})
    assert resp.status_code == 200
    assert b'Utilisateur modifi' in resp.data


def test_delete_user():
    client = app.test_client()
    username = "dave"
    password = "pass"
    client.post('/users', json={"username": username, "password": password}, headers={"X-API-Key": "api-key-123"})
    users = client.get('/users', headers={"X-API-Key": "api-key-123"}).get_json()
    user_id = [u['id'] for u in users if u['username'] == username][0]
    resp = client.delete(f'/users/{user_id}', headers={"X-API-Key": "api-key-123"})
    assert resp.status_code == 200
    assert b'Utilisateur supprim' in resp.data
