# fast_zero\routers\users.py
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import UserList, UserPublic, UserSchema
from fast_zero.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(
    prefix='/users',
    tags=['users'],
    responses={404: {'description': 'Not found'}},
)
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


# * criar um usuario
# * com validação de username e email únicos
@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: T_Session):
    db_user = session.scalar(
        select(User).where((User.username == user.username) | (User.email == user.email))
    )
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already exists.',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exists.',
            )

    db_user = User(
        username=user.username, password=get_password_hash(user.password), email=user.email
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)  # Refresh to get the updated user with ID

    return db_user


# * retornar uma lista de usuarios
# * com paginação
@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    session: T_Session,
    limit: int = 10,  # limite de usuarios por pagina
    skip: int = 0,  # começar a partir do offset
):
    user = session.scalars(select(User).offset(skip).limit(limit)).all()
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Not Found.')
    return {'users': user}


# * retornar um usuario pelo id
@router.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def read_user(user_id: int, session: T_Session):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f'User with ID {user_id} not found.'
        )

    return db_user


# * atualizar um usuario
@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    # * Verifica se o usuário é o mesmo que está tentando atualizar
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to update this user.',
        )

    current_user.username = user.username
    current_user.password = get_password_hash(user.password)
    current_user.email = user.email

    session.commit()
    session.refresh(current_user)  # Refresh to get the updated user with ID

    return current_user


# * deletar um usuario
@router.delete('/{user_id}', status_code=HTTPStatus.OK)
def delete_user(user_id: int, session: T_Session, current_user: T_CurrentUser):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail=f'User with ID {user_id} not found.'
        )

    session.delete(db_user)
    session.commit()

    return {'message': 'User deleted successfully'}
