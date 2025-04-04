from flask import Flask, render_template, g
import sqlite3

DATABASE = "habit_tree_save_file.db"

app = Flask(__name__)

# Configuration: tree requirements for each of 10 tree slots.
# For example, the first slot requires level 1, the second level 2, and so on.
TREE_REQUIREMENTS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tree (
            Name TEXT,
            Creation_Date TEXT,
            Stage INTEGER,
            Water INTEGER,
            Water_Required INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Farm (
            Creation_Date TEXT,
            Level INTEGER,
            Experience INTEGER,
            Experience_Required INTEGER
        )   
    ''')

    # Initialize the Tree table if empty
    cursor.execute("SELECT COUNT(*) FROM Tree")
    tree_count = cursor.fetchone()[0]
    if tree_count == 0:
        cursor.execute('''
            INSERT INTO Tree (Name, Creation_Date, Stage, Water, Water_Required)
            VALUES (?, ?, ?, ?, ?)
        ''', ('My Tree', '2025-04-04', 1, 0, 50))

    # Initialize the Farm table if empty
    cursor.execute("SELECT COUNT(*) FROM Farm")
    farm_count = cursor.fetchone()[0]
    if farm_count == 0:
        cursor.execute('''
            INSERT INTO Farm (Creation_Date, Level, Experience, Experience_Required)
            VALUES (?, ?, ?, ?)
        ''', ('2025-04-04', 1, 0, 100))

    db.commit()

@app.route("/")
def index():
    db = get_db()
    cursor = db.cursor()

    # Fetch first 10 trees from the database
    cursor.execute("SELECT * FROM Tree LIMIT 10")
    trees_data = cursor.fetchall()

    # Retrieve the current farm level (assume one farm record)
    cursor.execute("SELECT Level FROM Farm LIMIT 1")
    farm_row = cursor.fetchone()
    farm_level = farm_row[0] if farm_row else 1

    trees = []
    for i in range(10):
        required_level = TREE_REQUIREMENTS[i]
        # Check if the player has reached the required level for this tree slot
        if farm_level >= required_level:
            # If a tree already exists in this slot, display its data
            if i < len(trees_data):
                tree_row = trees_data[i]
                trees.append({
                    "unlocked": True,
                    "planted": True,
                    "name": tree_row[0],
                    "stage": tree_row[2],
                    "water": tree_row[3],
                    "water_required": tree_row[4],
                    "required_level": required_level
                })
            else:
                # Slot is unlocked but no tree planted yet
                trees.append({
                    "unlocked": True,
                    "planted": False,
                    "required_level": required_level
                })
        else:
            # Tree slot is locked because the required farm level has not been reached
            trees.append({
                "unlocked": False,
                "planted": False,
                "required_level": required_level
            })

    return render_template("index.html", trees=trees, farm_level=farm_level)

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
