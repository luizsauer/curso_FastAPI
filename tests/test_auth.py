# tests\test_auth.py
from http import HTTPStatus


def test_get_token(client, user):
    # Act
    response = client.post(
        'auth/token',
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
        'auth/token',
        data={
            'username': 'invalid_user',
            'password': 'invalid_password',
        },
    )
    # Assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password.'}
