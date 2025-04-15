from flask import Flask, jsonify, render_template, g, redirect, request, url_for
import datetime
import sqlite3
import datetime

# --------------------------
# Configuration Constants
# --------------------------
DATABASE = "habit_tree_save_file.db"
TREE_REQUIREMENTS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
WATER_REQUIRED_INCREASE_PER_STAGE_PERCENTAGE = 50
EXPERIENCE_REQUIRED_INCREASE_PER_LEVEL_PERCENTAGE = 50

app = Flask(__name__)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Trees (
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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Habits (
            Name TEXT PRIMARY KEY,
            Creation_Date TEXT,
            Priority INTEGER,
            Days_Of_The_Week TEXT,
            Completed BOOLEAN
        );
    ''')

    # Initialize the Garden table if empty
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

    cursor.execute("SELECT * FROM Trees ORDER BY Creation_Date LIMIT 10")
    trees_data = cursor.fetchall()

    cursor.execute("SELECT * FROM Habits")
    habits_data = cursor.fetchall()

    # Retrieve the current garden values as before...
    cursor.execute("SELECT Level FROM Garden LIMIT 1")
    garden_row = cursor.fetchone()
    garden_level = garden_row[0] if garden_row else 1

    cursor.execute("SELECT Water FROM Garden LIMIT 1")
    garden_row = cursor.fetchone()
    garden_water = garden_row[0] if garden_row else 1

    cursor.execute("SELECT Experience FROM Garden LIMIT 1")
    garden_row = cursor.fetchone()
    garden_experience = garden_row[0] if garden_row else 1

    cursor.execute("SELECT Experience_Required FROM Garden LIMIT 1")
    garden_row = cursor.fetchone()
    garden_experience_required = garden_row[0] if garden_row else 1

    trees = []
    for i in range(10):
        required_level = TREE_REQUIREMENTS[i]
        if garden_level >= required_level:
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
                trees.append({
                    "unlocked": True,
                    "planted": False,
                    "required_level": required_level
                })
        else:
            trees.append({
                "unlocked": False,
                "planted": False,
                "required_level": required_level
            })

    # Determine the current day, e.g., "Monday"
    current_day = datetime.datetime.now().strftime("%A")
    active_habits = []
    scheduled_habits = []

    # Process habits_data assuming each row is (Name, Creation_Date, Priority, Days_Of_The_Week, Completed)
    for habit in habits_data:
        # Split the comma-separated days and strip any extra whitespace
        days_list = [day.strip() for day in habit[3].split(',')]
        habit_dict = {
            "name": habit[0],
            "creation_date": habit[1],
            "priority": habit[2],
            "days": habit[3],
            "completed": habit[4]
        }
        if current_day in days_list:
            active_habits.append(habit_dict)
        else:
            scheduled_habits.append(habit_dict)

    return render_template("index.html",
                           trees=trees,
                           active_habits=active_habits,
                           scheduled_habits=scheduled_habits,
                           garden_level=garden_level,
                           garden_water=garden_water,
                           garden_experience=garden_experience,
                           garden_experience_required=garden_experience_required)

@app.route('/plant_tree', methods=['POST'])
def plant_tree():
    # Add your tree planting logic here
    create_tree()
    return redirect(url_for('index'))

def create_tree():
    db = get_db()
    cursor = db.cursor()

    current_date = datetime.date.today().isoformat()  # Get current date as string
    cursor.execute('''
        INSERT INTO Trees (Name, Creation_Date, Stage, Water, Water_Required)
        VALUES (?, ?, ?, ?, ?)
    ''', ('My Tree', current_date, 1, 0, 50))  # Use current date

    db.commit()

@app.route('/edit_tree', methods=['POST'])
def edit_tree():
    data = request.get_json()
    new_name = data.get('name')
    index = data.get('index')

    db = get_db()
    cursor = db.cursor()

    # Get the rowid of the tree at the given index ordered by creation date
    cursor.execute("SELECT rowid FROM Trees ORDER BY Creation_Date LIMIT 1 OFFSET ?", (index,))
    tree = cursor.fetchone()
    if not tree:
        return jsonify(success=False, error="Tree not found"), 404

    rowid = tree[0]
    cursor.execute("UPDATE Trees SET Name = ? WHERE rowid = ?", (new_name, rowid))
    db.commit()

    return jsonify(success=True)

@app.route('/add_habit', methods=['POST'])
def add_habit():
    data = request.get_json()
    habit_name = data.get('habit_name')
    habit_priority = data.get('habit_priority')
    habit_days_of_the_week = data.get('days_of_the_week')
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO Habits (Name, Creation_Date, Priority, Days_Of_The_Week, Completed) VALUES (?, datetime('now'), ?, ?, false)",
            (habit_name, habit_priority, habit_days_of_the_week)
        )
        db.commit()
    except sqlite3.IntegrityError:
        # This error will be raised if the habit_name already exists.
        return jsonify(success=False, error="A habit with that name already exists."), 400

    return jsonify(success=True)

@app.route('/edit_habit', methods=['POST'])
def edit_habit():
    data = request.get_json()
    # Extract values from the JSON body
    existing_habit_name = data.get('existing_habit_name')
    new_habit_name = data.get('new_habit_name')
    habit_priority = data.get('habit_priority')
    habit_days_of_the_week = data.get('days_of_the_week')
    
    db = get_db()
    cursor = db.cursor()
    try:
        # Execute update statement
        cursor.execute('''
            UPDATE Habits 
            SET Name = ?, Priority = ?, Days_Of_The_Week = ?
            WHERE Name = ?
        ''', (new_habit_name, habit_priority, habit_days_of_the_week, existing_habit_name))
        db.commit()
        
        # Check if any row was actually updated.
        if cursor.rowcount == 0:
            return jsonify(success=False, error="No habit found with that name."), 404
            
    except sqlite3.IntegrityError:
        # This error is raised if the new habit name already exists in the database.
        return jsonify(success=False, error="The new habit name already exists."), 400

    return jsonify(success=True)


@app.route('/complete_habit', methods=['POST'])
def complete_habit():
    data = request.get_json()
    habit_name = data.get('habit_name')
    
    if not habit_name:
        return jsonify(success=False, error="Not tree name passed!"), 403

    db = get_db()
    cursor = db.cursor()
    
    # Update the habit in the database
    cursor.execute("UPDATE Habits SET Completed = 1 WHERE Name = ?", (habit_name,))
    
    # Add water to garden
    cursor.execute("UPDATE Garden SET Water = Water + ? WHERE rowid = ?", (100000, 1))
    
    # Add experience to garden
    add_garden_experience(db, 200)
    
    db.commit()

    return jsonify(success=True)


@app.route('/water_tree', methods=['POST'])
def water_tree():
    data = request.get_json()

    # Extract and convert parameters
    tree_index = data.get('index')
    water_amount = int(data.get('water_amount', 0))

    db = get_db()
    cursor = db.cursor()

    # Get the rowid of the tree at the given index (ordered by creation date)
    cursor.execute("SELECT rowid FROM Trees ORDER BY Creation_Date LIMIT 1 OFFSET ?", (tree_index,))
    tree = cursor.fetchone()
    if not tree:
        return jsonify(success=False, error="Tree not found"), 404
    tree_rowid = tree[0]

    # Get the current water in the garden
    cursor.execute("SELECT Water FROM Garden LIMIT 1")
    garden = cursor.fetchone()
    if not garden:
        return jsonify(success=False, error="Garden not found"), 404
    garden_water = int(garden[0])
    if water_amount > garden_water:
        return jsonify(success=False, error="Not enough water!"), 403

    # Update the tree's water level
    cursor.execute("UPDATE Trees SET Water = Water + ? WHERE rowid = ?", (water_amount, tree_rowid))
    
    # Check and update the tree's growth if its water exceeds the required threshold
    check_and_update_tree_growth(db, tree_rowid)

    # Remove the used water from the garden
    cursor.execute("UPDATE Garden SET Water = Water - ? WHERE rowid = ?", (water_amount, 1))
    
    db.commit()
    return jsonify(success=True)

def add_garden_experience(db, amount):
    cursor = db.cursor()
    # Retrieve the current garden record. Adjust your query if you have multiple rows.
    cursor.execute("SELECT Level, Experience, Experience_Required FROM Garden LIMIT 1")
    row = cursor.fetchone()

    if row is None:
        raise ValueError("No garden record found in the database.")

    level, current_exp, exp_required = row
    new_exp_total = current_exp + amount

    # Loop to handle possible multiple level-ups.
    while new_exp_total >= exp_required:
        new_exp_total -= exp_required
        level += 1
        # Increase the required experience for the next level by the config variable.
        exp_required += exp_required / 100 * EXPERIENCE_REQUIRED_INCREASE_PER_LEVEL_PERCENTAGE
        exp_required = round(exp_required, -1)  # rounds to one decimal place (nearest tenth)

    # Update the Garden record with the new level, remaining experience, and updated requirement.
    cursor.execute("""
        UPDATE Garden
        SET Level = ?, Experience = ?, Experience_Required = ?
        WHERE rowid = (SELECT rowid FROM Garden LIMIT 1)
    """, (level, new_exp_total, exp_required))
    db.commit()


def check_and_update_tree_growth(db, tree_rowid):
    """
    Checks if the tree's water level has met or exceeded its required water for growth.
    If so, increases the tree's Stage by 1, adds 50 to Water_Required, resets the tree's water 
    to the leftover amount, and repeats if multiple stages are achieved.
    """
    cursor = db.cursor()
    cursor.execute("SELECT Water, Water_Required, Stage FROM Trees WHERE rowid = ?", (tree_rowid,))
    result = cursor.fetchone()
    if not result:
        return

    water, water_required, stage = map(int, result)
    updated = False

    # While the current water level is enough to grow the tree...
    while water >= water_required:
        # Use up the required water and carry over any extra
        water -= water_required 
        
        # Increase stage
        stage += 1
        
        # Increase water needed for the next stage
        water_required += water_required / 100 * WATER_REQUIRED_INCREASE_PER_STAGE_PERCENTAGE
        water_required = round(water_required, -1)  # rounds to one decimal place (nearest tenth)
        updated = True

    if updated:
        cursor.execute(
            "UPDATE Trees SET Water = ?, Water_Required = ?, Stage = ? WHERE rowid = ?",
            (water, water_required, stage, tree_rowid)
        )

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
                  # Increase the tree's stage