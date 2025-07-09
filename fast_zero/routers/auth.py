# fast_zero\routers\auth.py
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Token
from fast_zero.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
    responses={404: {'description': 'Not found'}},
)
T_Session = Annotated[Session, Depends(get_session)]
T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


# * autenticar um usuario
# * retornar um token JWT
@router.post('/token', response_model=Token, status_code=HTTPStatus.OK)
def login_for_access_token(session: T_Session, form_data: T_OAuth2Form):
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


@router.post('/refresh_token', response_model=Token, status_code=HTTPStatus.OK)
def refresh_token(
    user: User = Depends(get_current_user),
):
    access_token = create_access_token(data={'sub': user.username})
    if not access_token:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='Could not create access token.'
        )

    return {'access_token': access_token, 'token_type': 'bearer'}
