# fast_zero\routers\todo.py
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import Todo, TodoState, User
from fast_zero.schemas import TodoList, TodoPublic, TodoSchema, TodoUpdate
from fast_zero.security import get_current_user

router = APIRouter(
    prefix='/todos',
    tags=['todos'],
    responses={404: {'description': 'Not found'}},
)

T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TodoPublic, status_code=HTTPStatus.CREATED)
def create_todo(todo: TodoSchema, session: T_Session, user: T_CurrentUser):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodoList)
def list_todos(  # noqa
    session: T_Session,
    user: T_CurrentUser,
    title: str | None = None,
    description: str | None = None,
    state: TodoState | None = None,
    limit: int = 10,
    offset: int = 0,
):
    query = select(Todo).where(Todo.user_id == user.id)

    if title:
        query = query.filter(Todo.title.ilike(f'%{title}%'))
    if description:
        query = query.filter(Todo.description.ilike(f'%{description}%'))
    if state:
        query = query.filter(Todo.state == state)

    todos = session.scalars(query.offset(offset).limit(limit)).all()
    return {'todos': todos}


@router.delete('/{todo_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_todo(todo_id: int, session: T_Session, user: T_CurrentUser):
    todo = session.scalar(select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id))
    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Todo not found or not owned by user',
        )

    session.delete(todo)
    session.commit()
    return {'message': 'Todo deleted successfully'}


@router.patch('/{todo_id}', response_model=TodoPublic)
def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    session: T_Session,
    user: T_CurrentUser,
):
    todo = session.scalar(select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id))
    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Todo not found or not owned by user',
        )

    for key, value in todo_update.model_dump(exclude_unset=True).items():
        setattr(todo, key, value)

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
