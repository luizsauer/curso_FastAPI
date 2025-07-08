# src\fast_zero\app.py
from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, Token, UserList, UserPublic, UserSchema
from fast_zero.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World'}


# * criar um usuario
# * com validação de username e email únicos
@app.post('/users', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(
    user: UserSchema,
    session: Session = Depends(get_session),
    # current_user=Depends(get_current_user),
):
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
@app.get('/users', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    limit: int = 10,  # limite de usuarios por pagina
    skip: int = 0,  # começar a partir do offset
    session: Session = Depends(get_session),
):
    user = session.scalars(select(User).offset(skip).limit(limit)).all()
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='No users found.')
    return {'users': user}


# * retornar um usuario pelo id
@app.get('/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def read_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f'User with ID {user_id} not found.'
        )

    return db_user


# * atualizar um usuario
@app.put('/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
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
@app.delete('/users/{user_id}', status_code=HTTPStatus.OK)
def delete_user(
    user_id: int, session: Session = Depends(get_session), current_user=Depends(get_current_user)
):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f'User with ID {user_id} not found.'
        )

    session.delete(db_user)
    session.commit()

    return {'message': 'User deleted successfully'}


# * autenticar um usuario
# * retornar um token JWT
@app.post('/token', response_model=Token, status_code=HTTPStatus.OK)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)
):
    user = session.scalar(select(User).where(User.username == form_data.username))
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Incorrect username or password.'
        )

    access_token = create_access_token(data={'sub': user.username})
    if not access_token:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='Could not create access token.'
        )

    return {'access_token': access_token, 'token_type': 'bearer'}
