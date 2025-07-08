# tests\test_db.py
from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    # Arrange (Preparar)
    new_user = User(
        username='test_user',
        email='test_user@test_user.com',
        password='123456',
    )
    session.add(new_user)
    session.commit()
    result = session.scalar(select(User).where(User.username == 'test_user'))

    # Assert (Afirmar)
    assert result.username == 'test_user'
    assert result.email == 'test_user@test_user.com'
    assert result.password == '123456'
