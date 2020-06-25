from flask import current_app, g
from mongoengine import *

ROOT_PATH = None

def create_indexes(platform_memory):
    platform_memory['entities'].create_index([("header.instanceId", 1)])
    platform_memory['event'].create_index([("header.instanceId", 1)])
    platform_memory['fork'].create_index([("header.instanceId", 1)])
    platform_memory['instance_filter'].create_index([("header.instanceId", 1)])
    platform_memory['maps'].create_index([("header.instanceId", 1)])


def init_app(app):
    app.teardown_appcontext(close_db_connection)
    global ROOT_PATH
    ROOT_PATH = app.root_path
    with app.app_context():
        db = get_database()
        create_indexes(db)


def get_database():
    """
    Get the current configured database. All configurations are on __init__.py: Check HOST and DATABASE_NAME.
    :return: MongoClient connected to the configured host and database.
    """
    db = open_db_connection()
    return db[current_app.config['DATABASE_NAME']]


def open_db_connection():
    """
    Connect to database. First create the URI and then connect to it.
    Production params should come from a config file. Default values are provided for dev.
    uri = f"mongodb://{current_app.config['HOST']}:{current_app.config['PORT']}"
    """
    # import pdb; pdb.set_trace()
    if 'db' not in g:
        if current_app.config['HOST'] != 'mongo':
            uri = f'mongodb://' \
                  f'{current_app.config["USER"]}:{current_app.config["SECRET"]}' \
                  f'@{current_app.config["HOST"]}:{current_app.config["PORT"]}' \
                  f'/?ssl=true' \
                  f'&ssl_ca_certs={ROOT_PATH}/certs/rds-combined-ca-bundle.pem' \
                  f'&replicaSet={current_app.config["REPLICASET"]}' \
                  f'&readPreference=secondaryPreferred'
            g.db = connect(current_app.config['DATABASE_NAME'], host=uri)
        else:
            g.db = connect(db=current_app.config['DATABASE_NAME'], host=current_app.config['HOST'], alias='default')

        """        
        g.db = connect(
            host=current_app.config['HOST'],
            db=current_app.config['DATABASE_NAME'],
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
