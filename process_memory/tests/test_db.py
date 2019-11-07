import pytest
from process_memory.db import open_db_connection


def test_db(app):
    """
    Test database connection
    """
    with app.app_context():
        database = open_db_connection()
        assert database is open_db_connection()
