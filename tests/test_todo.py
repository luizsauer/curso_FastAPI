# tests\test_todo.py


from http import HTTPStatus

from fast_zero.models import TodoState
from tests.conftest import TodoFactory, UserFactory


def test_create_todo(client, token):
    response = client.post(
        '/todos/',
        json={'title': 'Test Todo', 'description': 'This is a test todo item.', 'state': 'draft'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.json() == {
        'id': 1,
        'title': 'Test Todo',
        'description': 'This is a test todo item.',
        'state': 'draft',
        'created_at': response.json()['created_at'],
        'updated_at': response.json()['updated_at'],
    }
    assert response.status_code == HTTPStatus.CREATED


def test_create_todo_unauthorized(client):
    response = client.post(
        '/todos/',
        json={'title': 'Test Todo', 'description': 'This is a test todo item.', 'state': 'draft'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_list_todos_should_return_5_todos(client, token, session, user):
    expected_todos = 5
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_pagination_should_return_2_todos(client, token, session, user):
    expected_todos = 2
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todos/?limit=2&offset=0',
        headers={'Authorization': f'Bearer {token}'},
        # params={'limit': expected_todos, 'offset': 0},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_title_should_return_5_todos(client, token, session, user):
    expected_todos = 5
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id, title='Test Todo 1'))
    session.commit()

    response = client.get(
        '/todos/?title=Test Todo 1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_description_should_return_5_todos(client, token, session, user):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(5, user_id=user.id, description='Test Description')
    )
    session.commit()

    response = client.get(
        '/todos/?descr=Test Description',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_state_should_return_5_todos(client, token, session, user):
    expected_todos = 5
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id, state=TodoState.draft))
    session.commit()

    response = client.get(
        '/todos/?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_combined_should_return_5_todos(client, token, session, user):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='Test Todo Combined',
            description='combined',
            state=TodoState.done,
        )
    )
    session.bulk_save_objects(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Other title',
            description='Other description',
            state=TodoState.todo,
        )
    )
    session.commit()

    response = client.get(
        '/todos/?title=Test Todo Combined&description=combined&state=done',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_delete_todo(client, token, session, user):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    # Verify the todo was deleted
    deleted_todo = session.get(todo.__class__, todo.id)
    assert deleted_todo is None


def test_delete_todo_not_found(client, token, session, user):
    response = client.delete(
        f'/todos/{10}',  # Assuming this ID does not exist
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Todo not found or not owned by user'}


def test_delete_todo_unauthorized(client, session):
    user = UserFactory()
    session.add(user)
    session.commit()
    session.refresh(user)

    todo = TodoFactory.build(user_id=user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)

    response = client.delete(f'/todos/{todo.id}')
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_update_todo(client, token, session, user):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)

    updated_data = {
        'title': 'Updated Todo',
        'description': 'This is an updated todo item.',
        'state': 'doing',
    }

    response = client.patch(
        f'/todos/{todo.id}',
        json=updated_data,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': todo.id,
        'title': updated_data['title'],
        'description': updated_data['description'],
        'state': updated_data['state'],
        'created_at': response.json()['created_at'],
        'updated_at': response.json()['updated_at'],
    }


def test_update_todo_not_found(client, token):
    response = client.patch(
        '/todos/9999',  # Assuming this ID does not exist
        json={
            'title': 'Updated Todo',
            'description': 'This is an updated todo item.',
            'state': 'doing',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Todo not found or not owned by user'}
