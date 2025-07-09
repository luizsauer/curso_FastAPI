# tests\test_app.py
from http import HTTPStatus


def test_root_deve_retornar_200_e_ola_mundo(client):
    # Act (Ação)
    response = client.get('/')
    # Assert (Afirmar)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World'}
