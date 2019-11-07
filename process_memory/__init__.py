import os
from flask import Flask
from process_memory import db
from . import instances, collection, history


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
        DATABASE_NAME=os.getenv('DOCDB_DATABASE_NAME', 'memory'),
        PORT=os.getenv('DOCDB_PORT', '27017'),
        OPTIONS=os.getenv('DOCDB_OPTIONS', '?ssl=true&ssl_ca_certs=rds-combined-ca-bundle.pem&replicaSet=rs0')
    )

    if not test_config:
        # Load the instance config, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    db.init_app(app)

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/')
    def testdb():
        mydb = db.open_db_connection()
        return str(f"Database TEST: {mydb.test}")

    app.register_blueprint(instances.bp)
    app.register_blueprint(collection.bp)
    app.register_blueprint(history.bp)

    return app
