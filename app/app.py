from flask import Flask, jsonify, render_template, g, redirect, request, url_for
import datetime
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
        CREATE TABLE IF NOT EXISTS Garden (
            Creation_Date TEXT,
            Level INTEGER,
            Experience INTEGER,
            Experience_Required INTEGER,
            Water INTEGER
        )   
    ''')

    # Initialize the Gaeden table if empty
    cursor.execute("SELECT COUNT(*) FROM Garden")
    garden_count = cursor.fetchone()[0]
    if garden_count == 0:
        cursor.execute('''
            INSERT INTO Garden (Creation_Date, Level, Experience, Experience_Required, Water)
            VALUES (?, ?, ?, ?, ?)
        ''', ('2025-04-04', 1, 0, 100, 0))

    db.commit()

@app.route("/")
def index():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Tree ORDER BY Creation_Date LIMIT 10")  # Ensure ORDER BY for index purposes
    trees_data = cursor.fetchall()

    # Retrieve the current garden level (assume one garden record)
    cursor.execute("SELECT Level FROM Garden LIMIT 1")
    garden_row = cursor.fetchone()
    garden_level = garden_row[0] if garden_row else 1

    # Retrieve the current water (assume one garden record)
    cursor.execute("SELECT Water FROM Garden LIMIT 1")
    garden_row = cursor.fetchone()
    garden_water = garden_row[0] if garden_row else 1

    trees = []
    for i in range(10):
        required_level = TREE_REQUIREMENTS[i]
        # Check if the player has reached the required level for this tree slot
        if garden_level >= required_level:
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
            # Tree slot is locked because the required garden level has not been reached
            trees.append({
                "unlocked": False,
                "planted": False,
                "required_level": required_level
            })

    return render_template("index.html", trees=trees, garden_level=garden_level, garden_water=garden_water)

@app.route('/plant', methods=['POST'])
def plant_tree():
    # Add your tree planting logic here
    create_tree()
    return redirect(url_for('index'))

def create_tree():
    db = get_db()
    cursor = db.cursor()

    current_date = datetime.date.today().isoformat()  # Get current date as string
    cursor.execute('''
        INSERT INTO Tree (Name, Creation_Date, Stage, Water, Water_Required)
        VALUES (?, ?, ?, ?, ?)
    ''', ('My Tree', current_date, 1, 0, 50))  # Use current date

    db.commit()

@app.route('/edit', methods=['POST'])
def edit_tree():
    data = request.get_json()
    new_name = data.get('name')
    index = data.get('index')

    db = get_db()
    cursor = db.cursor()

    # Get the rowid of the tree at the given index ordered by creation date
    cursor.execute("SELECT rowid FROM Tree ORDER BY Creation_Date LIMIT 1 OFFSET ?", (index,))
    tree = cursor.fetchone()
    if not tree:
        return jsonify(success=False, error="Tree not found"), 404

    rowid = tree[0]
    cursor.execute("UPDATE Tree SET Name = ? WHERE rowid = ?", (new_name, rowid))
    db.commit()

    return jsonify(success=True)

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
