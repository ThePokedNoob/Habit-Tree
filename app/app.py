from flask import Flask, render_template, g
import sqlite3

# Name of the SQLite database file.
DATABASE = "habit_tree_save_file.db"

app = Flask(__name__)

def get_db():
    # Opens a new database connection if one doesn't exist for the current application context.
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

def init_db():
    # Initializes the database by creating the 'Tree' table if it doesn't already exist.
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tree (
            Name TEXT,
            Creation_Date TEXT,
            Stage TEXT,
            Water INTEGER,
            Water_Required INTEGER
        )
    ''')
    db.commit()


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    with app.app_context():
        init_db()
        app.run(debug=True)
