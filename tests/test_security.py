# tests\test_security.py
from http import HTTPStatus

from jwt import decode

from fast_zero.security import ALGORITHM, SECRET_KEY, create_access_token


def test_jwt_token_creation():
    # Arrange
    data = {'sub': 'test_user'}

    # Act
    token = create_access_token(data)

    result = decode(token, SECRET_KEY, algorithms=[ALGORITHM])

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


def test_get_token(client, user):
    # Act
    response = client.post(
        '/token',
        data={
            'username': user.username,
            'password': user.clean_password,  # Use the clean password from the fixture
        },
    )
    token_data = response.json()

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert token_data['token_type'] == 'bearer'
    assert 'access_token' in token_data
    assert isinstance(token_data['access_token'], str)


def test_get_token_with_invalid_credentials(client):
    # Act
    response = client.post(
        '/token',
        data={
            'username': 'invalid_user',
            'password': 'invalid_password',
        },
    )
    # Assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password.'}
