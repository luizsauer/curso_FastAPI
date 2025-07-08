# tests\conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import get_password_hash


# Arrange (Organizar)
@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()  # Clear overrides after the test


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        # Allow multiple threads to use the same connection
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
        echo=True,
    )
    # Create tables
    table_registry.metadata.create_all(engine)

    # Create a new session
    # gerenciamento de contexto para a sessão
    # o contexto é fechado automaticamente após o uso
    with Session(engine) as session:
        yield session

    # Drop tables
    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session):
    plain_password = '123456'
    pwd = get_password_hash(plain_password)
    # Create a test user
    test_user = User(username='teste', email='teste@teste.com', password=pwd)

    session.add(test_user)
    session.commit()
    session.refresh(test_user)  # Refresh to get the updated user with ID

    test_user.clean_password = plain_password  # monkey patching para evitar hash de senha em testes
    return test_user


@pytest.fixture
def limpar_banco(session):
    table_registry.metadata.drop_all(bind=session.get_bind())
    table_registry.metadata.create_all(bind=session.get_bind())


@pytest.fixture
def token(client, user):
    response = client.post(
        '/token',
        data={
            'username': user.username,
            'password': user.clean_password,  # Use the clean password from the fixture
        },
    )
    token = response.json()['access_token']
    return token
