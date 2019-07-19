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
        USER='dbadmin',
        SECRET_KEY='T4FbKpQoURhrilE7',        
        DATABASE='docdb-jmi5t.mongodb.net/test?retryWrites=true',
        COLLECTION='process_memory'
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
        mydb = db.get_db()
        return str(f"Database TEST: {mydb.test}")

    app.register_blueprint(instances.bp)
    app.register_blueprint(collection.bp)
    app.register_blueprint(history.bp)

    return app
