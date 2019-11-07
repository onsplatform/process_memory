from pymongo import MongoClient
from flask import current_app, g


def init_app(app):
    app.teardown_appcontext(close_db_connection)
    with app.app_context():
        get_database_name()


def open_db_connection():
    """ 
    Connect to database. First create the URI and then connect to it.
    Production params should come from a config file. Default values are provided for dev.
    """
    uri = f"mongodb://{current_app.config['USER']}:{current_app.config['SECRET']}@{current_app.config['HOST']}" \
          f":{current_app.config['PORT']}/{current_app.config['OPTIONS']}"

    if 'db' not in g:
        g.db = MongoClient(uri)
    return g.db


def get_database_name():
    db = open_db_connection()
    return db[current_app.config['DATABASE_NAME']]


def close_db_connection(e=None):
    db = g.pop('db', e)

    if db is not None:
        db.close()
