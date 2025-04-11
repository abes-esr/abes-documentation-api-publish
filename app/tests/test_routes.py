import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

def test_list_manuals():
    response = client.get('/api/list')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
