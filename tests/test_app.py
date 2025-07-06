# tests\test_app.py
from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app

client = TestClient(app)


def test_root_deve_retornar_200_e_ola_mundo():
    # Arrange (Organizar)
    client = TestClient(app)
    # Act (Ação)
    response = client.get('/')
    # Assert (Afirmar)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World'}
