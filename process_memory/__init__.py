import os
import logging
from flask import Flask
from process_memory import db
from flask.json import JSONEncoder
from datetime import date
from . import memory_queries, collection, memory_create


def create_app(test_config=None):
    """
    Application Factory. Register new modules below.
    :param test_config:
    :return:
    """

    class CustomJSONEncoder(JSONEncoder):
        def default(self, obj):
            try:
                if isinstance(obj, date):
                    return obj.isoformat()
                iterable = iter(obj)
            except TypeError:
                pass
            else:
                return list(iterable)
            return JSONEncoder.default(self, obj)

    app = Flask(__name__, instance_relative_config=True)
    app.config["JSON_SORT_KEYS"] = False
    app.config.from_mapping(
        USER=os.getenv('DOCDB_USER', ''),
        SECRET=os.getenv('DOCDB_SECRET', ''),
        HOST=os.getenv('HOST', 'localhost'),
        DATABASE_NAME=os.getenv('DATABASE_NAME', 'platform_memory'),
        PORT=os.getenv('DOCDB_PORT', '27017'),
        REPLICASET=os.getenv('DOCDB_REPLICASET', 'rs0'),
        MAX_DOC_SIZE=os.getenv('DOCUMENT_SIZE', 15000000)
    )
    app.json_encoder = CustomJSONEncoder
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    if not test_config:
        # Load the instance config, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Connects to database
    db.init_app(app)

    @app.route('/')
    def hello():
        return 'Hello, World! The application is running.'

    @app.route('/hello')
    def test_db():
        current_db = db.open_db_connection()
        return str(f"Hello! This is the current configured database: {current_db.test}")

    app.register_blueprint(memory_create.bp)
    app.register_blueprint(memory_queries.bp)
    app.register_blueprint(collection.bp)

    return app
