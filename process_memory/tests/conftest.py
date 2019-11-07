import pytest
from process_memory import create_app
from process_memory.db import init_app


@pytest.fixture
def app():
    app = create_app({"TESTING": True})

    with app.app_context():
        init_app(app)

    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
