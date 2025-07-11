# tests\test_users.py
from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_criar_usuario_deve_retornar_201(client):
    # Act (Ação)
    response = client.post(
        '/users',
        json={
            'username': 'teste',
            'email': 'teste@teste.com',
            'password': '123456',
        },
    )
    # Assert (Afirmar) # voltou o status code correto?
    assert response.status_code == HTTPStatus.CREATED
    # validar UserPublic # voltou o usuario correto?
    assert response.json() == {
        'id': 1,
        'username': 'teste',
        'email': 'teste@teste.com',
    }


def test_listar_usuarios_deve_retornar_200(client, user):
    response = client.get('/users')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        ]
    }


def test_read_users_with_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    # Act (Ação)
    response = client.get('/users')
    # Assert (Afirmar)
    assert response.status_code == HTTPStatus.OK
    # validar UserList # voltou a lista de usuários correta?
    assert response.json() == {'users': [user_schema]}


def test_listar_usuarios_com_banco_vazio_deve_retornar_404(client, limpar_banco):
    response = client.get('/users')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Not Found.'}


def test_atualizar_usuario_deve_retornar_200(client, user, token):
    # Act (Ação)
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'teste_atualizado',
            'email': 'teste_atualizado@teste.com',
            'password': '123456',
            'id': user.id,  # Incluindo o ID do usuário para atualização
        },
    )
    # Assert (Afirmar)
    assert response.status_code == HTTPStatus.OK
    # validar UserPublic # voltou o usuario correto?
    assert response.json() == {
        'id': user.id,
        'username': 'teste_atualizado',
        'email': 'teste_atualizado@teste.com',
    }


def test_atualizar_usuario_inexistente_deve_retornar_403(client, other_user, token):
    # Act (Ação)
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'usuario_inexistente',
            'email': 'usuario_inexistente@teste.com',
            'password': '123456',
        },
    )
    # Assert (Afirmar)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'You do not have permission to update this user.'}


def test_put_usuario_com_id_zero_deve_retornar_403(client, token):
    response = client.put(
        '/users/0',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'teste', 'email': 'teste@teste.com', 'password': '123456'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_deletar_usuario_deve_retornar_200_com_mensagem(client, user, token):
    # Act (Ação)
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    # Assert (Afirmar)
    # Verificar se o usuário foi realmente deletado
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully'}


def test_deletar_usuario_inexistente_deve_retornar_403(client, other_user, token):
    # O token é de um usuário diferente do other_user
    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'You do not have permission to delete this user.'}


# def test_deletar_usuario_inexistente_deve_retornar_404(client, other_user, token):
#     # Act (Ação)
#     response = client.delete(
#         f'/users/{other_user.id}',
#         headers={'Authorization': f'Bearer {token}'},
#     )
#     # Assert (Afirmar)
#     assert response.status_code == HTTPStatus.FORBIDDEN
#     assert response.json() == {'detail': f'User with ID {other_user.id} not found.'}


def test_delete_usuario_com_id_zero_deve_retornar_404(client, token):
    response = client.delete(
        '/users/0',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_obter_usuario_existente_deve_retornar_200(client, user):
    # Act
    response = client.get(f'/users/{user.id}')

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }


def test_obter_usuario_inexistente_deve_retornar_404(client, token):
    # Act
    response = client.get(
        '/users/999',
        headers={'Authorization': f'Bearer {token}'},
    )

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User with ID 999 not found.'}


def test_deletar_usuario_com_banco_vazio_deve_retornar_404(client, limpar_banco, token):
    response = client.delete(
        '/users/999',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code in {HTTPStatus.FORBIDDEN, HTTPStatus.UNAUTHORIZED}
    assert response.json() == {'detail': 'User with ID 999 not found.'}


def test_get_usuario_com_banco_vazio_deve_retornar_404(client, limpar_banco):
    response = client.get('/users/1')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_criar_usuario_com_username_duplicado_deve_retornar_400(client, user):
    response = client.post(
        '/users',
        json={
            'username': user.username,
            'email': 'novoemail@teste.com',
            'password': 'novasenha',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists.'}


def test_criar_usuario_com_email_duplicado_deve_retornar_400(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'novousername',
            'email': user.email,
            'password': 'novasenha',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already exists.'}
