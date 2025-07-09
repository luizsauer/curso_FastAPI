# tests\test_auth.py
from http import HTTPStatus

from freezegun import freeze_time


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


def test_get_token_with_expired_password(client, user):
    # Arrange
    with freeze_time('2023-01-01 00:00:00'):
        # Act
        response = client.post(
            'auth/token',
            data={
                'username': user.username,
                'password': user.clean_password,
            },
        )

        # Assert
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-01-01 00:31:00'):
        # Act
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrong_username',
                'email': 'wrong_email',
                'new_password': 'wrong_password',
            },
        )

        # Assert
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_wrong_password(client, user):
    # Act
    response = client.post(
        'auth/token',
        data={
            'username': user.username,
            'password': 'wrong_password',
        },
    )
    # Assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password.'}


def test_token_wrong_email(client, user):
    # Act
    response = client.post(
        'auth/token',
        data={
            'username': 'wrong_email',
            'password': user.clean_password,
        },
    )
    # Assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password.'}


def test_token_wrong_username(client, user):
    # Act
    response = client.post(
        'auth/token',
        data={
            'username': 'wrong_username',
            'password': user.clean_password,
        },
    )
    # Assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password.'}


def test_refresh_token(client, user, token):
    # Act
    response = client.post(
        'auth/refresh_token',
        data={
            'username': user.username,
            'password': user.clean_password,
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    token_data = response.json()

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert token_data['token_type'] == 'bearer'
    assert 'access_token' in token_data
    assert isinstance(token_data['access_token'], str)


def test_token_expired_dont_refresh(client, user):
    # Arrange
    with freeze_time('2023-01-01 00:00:00'):
        # Act
        response = client.post(
            'auth/token',
            data={
                'username': user.username,
                'password': user.clean_password,
            },
        )

        # Assert
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-01-01 00:31:00'):
        # Act
        response = client.post(
            'auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        # Assert
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
