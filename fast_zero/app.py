# src\fast_zero\app.py
from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World'}


@app.post('/users', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session=Depends(get_session)):
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

    db_user = User(username=user.username, password=user.password, email=user.email)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)  # Refresh to get the updated user with ID

    return db_user


@app.get('/users', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    limit: int = 10,  # limite de usuarios por pagina
    skip: int = 0,  # começar a partir do offset
    session=Depends(get_session),
):
    user = session.scalars(select(User).offset(skip).limit(limit)).all()
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='No users found.')
    return {'users': user}


# * atualizar um usuario
@app.put('/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(user_id: int, user: UserSchema, session=Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f'User with ID {user_id} not found.'
        )

    db_user.username = user.username
    db_user.password = user.password
    db_user.email = user.email

    session.add(db_user)
    session.commit()
    session.refresh(db_user)  # Refresh to get the updated user with ID

    return db_user


# * deletar um usuario
@app.delete('/users/{user_id}', status_code=HTTPStatus.OK)
def delete_user(user_id: int, session=Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f'User with ID {user_id} not found.'
        )

    session.delete(db_user)
    session.commit()

    return {'message': 'User deleted successfully'}


# * retornar um usuario pelo id
@app.get('/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def read_user(user_id: int, session=Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f'User with ID {user_id} not found.'
        )

    return db_user
