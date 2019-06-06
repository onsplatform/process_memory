import os
from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        USER = 'dbadmin',
        SECRET_KEY='T4FbKpQoURhrilE7',        
        DATABASE = 'docdb-jmi5t.mongodb.net/test?retryWrites=true',
        COLLECTION = 'process_memory'
    )

    if test_config is None:
        # Load the instance config, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    from process_memory import db
    db.init_app(app)

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/')
    def testdb():
        mydb = db.get_db()
        return str(mydb.test)

    from . import history
    app.register_blueprint(history.bp)
    app.add_url_rule('/', endpoint='index')

    return app