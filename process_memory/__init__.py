import os
from flask import Flask
from process_memory import db
from . import instances, collection, history, memory


def create_app(test_config=None):
    """
    Application Factory. Register new modules below.
    :param test_config:
    :return:
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        USER=os.getenv('DOCDB_USER', 'docdbadmin'),
        SECRET=os.getenv('DOCDB_SECRET', 'docdbadmin'),
        HOST=os.getenv('DOCDB_HOST', 'plataforma-docdb.cluster-czqebrnlxa8n.us-east-1.docdb.amazonaws.com'),
        DATABASE_NAME=os.getenv('DOCDB_DATABASE_NAME', 'platform_memory'),
        PORT=os.getenv('DOCDB_PORT', '27017'),
        OPTIONS=os.getenv('DOCDB_OPTIONS', f"?replicaSet=rs0"),
        MAX_DOC_SIZE=os.getenv('DOCUMENT_SIZE', 15000000)
    )

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

    app.register_blueprint(memory.bp)
    app.register_blueprint(instances.bp)
    app.register_blueprint(collection.bp)
    app.register_blueprint(history.bp)

    return app
