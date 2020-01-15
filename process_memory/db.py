from flask import current_app, g
import gridfs
from mongoengine import *

ROOT_PATH = None


def init_app(app):
    app.teardown_appcontext(close_db_connection)
    global ROOT_PATH
    ROOT_PATH = app.root_path
    with app.app_context():
        get_database()


def get_database():
    """
    Get the current configured database. All configurations are on __init__.py: Check HOST and DATABASE_NAME.
    :return: MongoClient connected to the configured host and database.
    """
    db = open_db_connection()
    return db[current_app.config['DATABASE_NAME']]


def get_grid_fs():
    db = get_database()
    return gridfs.GridFS(db)


def open_db_connection():
    """ 
    Connect to database. First create the URI and then connect to it.
    Production params should come from a config file. Default values are provided for dev.
    """
    uri = f"mongodb://{current_app.config['HOST']}:{current_app.config['PORT']}"
    if 'db' not in g:

        g.db = connect(db='platform_memory')
        """        
        g.db = connect(
            host='localhost',
            db='platform_memory',
            username=current_app.config['USER'],
            password=current_app.config['SECRET'],
            ssl=True,
            ssl_ca_certs=f'{ROOT_PATH}/certs/rds-combined-ca-bundle.pem',
            replicaSet=current_app.config['REPLICASET']
        )
        """
    return g.db


def close_db_connection(e=None):
    """
    Close the database connection.
    :param e: return value to global
    :return: none
    """
    db = g.pop('db', e)

    if db is not None:
        disconnect_all()

