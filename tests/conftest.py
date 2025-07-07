# tests\conftest.py
import pytest
from fastapi.testclient import TestClient

from fast_zero.app import app


# Arrange (Organizar)
@pytest.fixture
def client():
    return TestClient(app)
