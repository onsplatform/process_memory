from process_memory.db import get_database


def test_db(app):
    """
    Test database connection
    """
    with app.app_context():
        database = get_database()
        assert database is not None
