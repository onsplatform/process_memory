import pytest
from process_memory.db import get_db


def test_db(app):
    """
    Test database connection
    """
    with app.app_context():
        database = get_db()
        assert database is get_db()
