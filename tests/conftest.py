# tests\conftest.py
import factory
import factory.fuzzy
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import Todo, TodoState, User, table_registry
from fast_zero.security import get_password_hash


# Fabrica de de usuários para testes
class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')  # Unique username for each user
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.LazyAttribute(lambda _: get_password_hash('password123'))


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('sentence')
    state = factory.fuzzy.FuzzyChoice(TodoState)  # Randomly choose a state from TodoState enum
    user_id = factory.LazyAttribute(lambda _: UserFactory().id)  # Reference to the user ID


# Arrange (Organizar)
@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()  # Clear overrides after the test


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:latest', driver='psycopg') as postgres:
        # Create a new SQLAlchemy engine using the database URL from the settings
        _engine = create_engine(postgres.get_connection_url(), echo=True)
        with _engine.begin():
            yield _engine


@pytest.fixture
def session(engine):
    # * Create an in-memory SQLite database for testing
    # engine = create_engine(
    #     'sqlite:///:memory:',
    #     # Allow multiple threads to use the same connection
    #     connect_args={'check_same_thread': False},
    #     poolclass=StaticPool,
    #     echo=True,
    # )
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
    test_user = UserFactory(
        password=pwd,
    )

    session.add(test_user)
    session.commit()
    session.refresh(test_user)  # Refresh to get the updated user with ID

    test_user.clean_password = plain_password  # monkey patching para evitar hash de senha em testes
    return test_user


@pytest.fixture
def other_user(session):
    test_user = UserFactory()

    session.add(test_user)
    session.commit()
    session.refresh(test_user)

    return test_user


@pytest.fixture
def limpar_banco(session):
    table_registry.metadata.drop_all(bind=session.get_bind())
    table_registry.metadata.create_all(bind=session.get_bind())


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.username,
            'password': user.clean_password,  # Use the clean password from the fixture
        },
    )
    token = response.json()['access_token']
    return token
