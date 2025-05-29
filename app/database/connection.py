import sqlite3
from flask import g
from config import DATABASE

def get_db():
    """Get or create SQLite database connection using Flask's g object"""
    if 'db' not in g:   
        g.db = sqlite3.connect(DATABASE, timeout=2)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection if it exists"""
    db = g.pop('db', None)
    if db is not None:
        db.close()