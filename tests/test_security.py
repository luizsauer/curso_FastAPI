# tests\test_security.py
from http import HTTPStatus

from jwt import decode

from fast_zero.security import Settings, create_access_token

settings = Settings()


def test_jwt_token_creation():
    # Arrange
    data = {'sub': 'test_user'}

    # Act
    token = create_access_token(data)

    result = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    # Assert
    assert result['sub'] == data['sub']
    assert 'exp' in result  # Check if expiration time is included
    assert result['exp'] > 0  # Ensure expiration time is a positive integer


def test_jwt_invalid_token(client):
    # Act
    response = client.delete(
        '/users/1',
        headers={'Authorization': 'Bearer invalid_token'},
    )
    # Assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
