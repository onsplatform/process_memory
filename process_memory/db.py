import pymongo
from flask import current_app, g
from flask.cli import with_appcontext
import click

def get_db():    
    uri = f"mongodb+srv://{current_app.config['USER']}:{current_app.config['SECRET_KEY']}@{current_app.config['DATABASE']}"
    if 'db' not in g:
        g.db = pymongo.MongoClient(uri) 
    return g.db

def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db_collection()    

def init_db_collection():
    db = get_db()
    return db[current_app.config['COLLECTION']]

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()