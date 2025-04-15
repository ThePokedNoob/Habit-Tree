"""
Habit Tree Application using Flask and SQLite

This application helps users manage habits and grow virtual trees based on their progress.
Includes garden leveling system and daily habit tracking.
"""

from flask import Flask, jsonify, render_template, g, redirect, request, url_for
import sqlite3
import datetime

# --------------------------
# Configuration Constants
# --------------------------

DATABASE = "habit_tree_save_file.db"
TREE_REQUIREMENTS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]     # Level requirements for each tree slot
REQUIRED_WATER_INCREASE_PER_STAGE_PERCENTAGE = 50       # The increase of the required water to the next stage as a percentage of the current required water
REQUIRED_EXPERIENCE_INCREASE_PER_LEVEL_PERCENTAGE = 50  # The increase of the required experience to the next level as a percentage of the current required experience

app = Flask(__name__)

# --------------------------
# Database Helper Functions
# --------------------------

def get_db():
    """Get or create SQLite database connection using Flask's g object"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # Return rows as dictionaries
    return g.db

def close_db(e=None):
    """Close database connection if it exists"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database tables and default garden values"""
    db = get_db()
    
    # Table creation SQL commands
    tables = {
        'Trees': '''
            CREATE TABLE IF NOT EXISTS Trees (
                Name TEXT,
                Creation_Date TEXT,
                Stage INTEGER,
                Water INTEGER,
                Water_Required INTEGER
            )
        ''',
        'Garden': '''
            CREATE TABLE IF NOT EXISTS Garden (
                Creation_Date TEXT,
                Level INTEGER,
                Experience INTEGER,
                Experience_Required INTEGER,
                Water INTEGER
            )
        ''',
        'Habits': '''
            CREATE TABLE IF NOT EXISTS Habits (
                Name TEXT PRIMARY KEY,
                Creation_Date TEXT,
                Priority INTEGER,
                Days_Of_The_Week TEXT,
                Completed BOOLEAN
            )
        '''
    }

    # Create tables
    with db:
        cursor = db.cursor()
        for table, schema in tables.items():
            cursor.execute(schema)
        
        # Initialize garden with default values if empty
        if not cursor.execute("SELECT 1 FROM Garden LIMIT 1").fetchone():
            cursor.execute('''
                INSERT INTO Garden (Creation_Date, Level, Experience, Experience_Required, Water)
                VALUES (?, 1, 0, 100, 0)
            ''', (datetime.date.today().isoformat(),))

# --------------------------
# Data Access Layer
# --------------------------

def get_garden_data(db):
    """Retrieve current garden status"""
    return db.execute('''
        SELECT Level, Experience, Experience_Required, Water 
        FROM Garden 
        LIMIT 1
    ''').fetchone()

def get_trees_data(db):
    """Retrieve first 10 trees ordered by creation date"""
    return db.execute('''
        SELECT rowid, *, Creation_Date 
        FROM Trees 
        ORDER BY Creation_Date 
        LIMIT 10
    ''').fetchall()

def get_habits_data(db):
    """Retrieve all habits"""
    return db.execute('''
        SELECT Name, Creation_Date, Priority, Days_Of_The_Week, Completed 
        FROM Habits
    ''').fetchall()

# --------------------------
# Business Logic
# --------------------------

def process_trees(trees_data, garden_level):
    """Process raw tree data into frontend-friendly format"""
    trees = []
    for i in range(10):
        required_level = TREE_REQUIREMENTS[i]
        unlocked = garden_level >= required_level
        planted = i < len(trees_data)
        
        tree = {
            "unlocked": unlocked,
            "planted": planted,
            "required_level": required_level
        }
        
        if unlocked and planted:
            tree.update({
                "name": trees_data[i]['Name'],
                "stage": trees_data[i]['Stage'],
                "water": trees_data[i]['Water'],
                "water_required": trees_data[i]['Water_Required']
            })
        
        trees.append(tree)
    return trees

def process_habits(habits_data):
    """Separate habits into active (today) and scheduled (other days)"""
    current_day = datetime.datetime.now().strftime("%A")
    active, scheduled = [], []
    
    for habit in habits_data:
        days = [d.strip() for d in habit['Days_Of_The_Week'].split(',')]
        habit_dict = {
            "name": habit['Name'],
            "creation_date": habit['Creation_Date'],
            "priority": habit['Priority'],
            "days": habit['Days_Of_The_Week'],
            "completed": bool(habit['Completed'])
        }
        
        if current_day in days:
            active.append(habit_dict)
        else:
            scheduled.append(habit_dict)
    
    return active, scheduled

def add_experience(db, amount):
    """Add experience to garden and handle level-ups"""
    garden = get_garden_data(db)
    new_exp = garden['Experience'] + amount
    level = garden['Level']
    exp_required = garden['Experience_Required']
    
    while new_exp >= exp_required:
        new_exp -= exp_required
        level += 1
        exp_required += round(exp_required / 100 * REQUIRED_EXPERIENCE_INCREASE_PER_LEVEL_PERCENTAGE, -1)
    
    with db:
        db.execute('''
            UPDATE Garden 
            SET Level = ?, Experience = ?, Experience_Required = ?
        ''', (level, new_exp, exp_required))

# --------------------------
# Application Routes
# --------------------------

@app.route('/')
def index():
    """Main dashboard showing garden status, trees, and habits"""
    db = get_db()
    active, scheduled = process_habits(get_habits_data(db))
    
    return render_template("index.html",
        trees=process_trees(get_trees_data(db), get_garden_data(db)['Level']),
        active_habits=active,
        scheduled_habits=scheduled,
        garden=get_garden_data(db)
)

@app.route('/plant_tree', methods=['POST'])
def plant_tree():
    """Plant a new tree in the first available slot"""
    db = get_db()
    with db:
        db.execute('''
            INSERT INTO Trees (Name, Creation_Date, Stage, Water, Water_Required)
            VALUES (?, ?, 1, 0, 50)
        ''', ('My Tree', datetime.date.today().isoformat()))
    return redirect(url_for('index'))

@app.route('/edit_tree', methods=['POST'])
def edit_tree():
    data = request.get_json()
    new_name = data.get('name')
    tree_index = data.get('index')

    db = get_db()
    cursor = db.cursor()
    
    # Get target tree
    tree = get_trees_data(db)[tree_index]
    if not tree:
        return jsonify(success=False, error="Tree not found"), 404

    # Update tree name
    rowid = tree[0]
    cursor.execute("UPDATE Trees SET Name = ? WHERE rowid = ?", (new_name, rowid))
    
    db.commit()

    return jsonify(success=True)


@app.route('/water_tree', methods=['POST'])
def water_tree():
    """Water a specific tree using garden water reserves"""
    data = request.get_json()
    tree_index = data['index']
    amount = int(data['water_amount'])
    
    db = get_db()
    with db:
        # Verify water availability
        garden = get_garden_data(db)
        if garden['Water'] < amount:
            return jsonify(success=False, error="Not enough water!"), 403
        
        # Get target tree
        tree = get_trees_data(db)[tree_index]
        if not tree:
            return jsonify(success=False, error="Tree not found"), 404
        
        # Update water values
        db.execute('''
            UPDATE Trees 
            SET Water = Water + ? 
            WHERE rowid = ?
        ''', (amount, tree['rowid']))
        
        db.execute('''
            UPDATE Garden 
            SET Water = Water - ?
        ''', (amount,))
        
        # Check for growth
        check_tree_growth(db, tree['rowid'])
    
    return jsonify(success=True)




# --------------------------
# Tree Growth System
# --------------------------

def check_tree_growth(db, tree_id):
    """Check if tree has enough water to advance stages"""
    tree = db.execute('''
        SELECT Water, Water_Required, Stage 
        FROM Trees 
        WHERE rowid = ?
    ''', (tree_id,)).fetchone()
    
    while tree['Water'] >= tree['Water_Required']:
        tree = dict(tree)  # Convert row to dict for mutation
        tree['Water'] -= tree['Water_Required']
        tree['Stage'] += 1
        tree['Water_Required'] += round(tree['Water_Required'] / 100 * REQUIRED_WATER_INCREASE_PER_STAGE_PERCENTAGE, -1)
        
        db.execute('''
            UPDATE Trees 
            SET Water = ?, Stage = ?, Water_Required = ? 
            WHERE rowid = ?
        ''', (tree['Water'], tree['Stage'], tree['Water_Required'], tree_id))
    
    return tree['Stage']




# --------------------------
# Habit Management
# --------------------------

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

@app.route('/delete_habit', methods=['POST'])
def delete_habit():
    data = request.get_json()
    # Extract values from the JSON body
    habit_name = data.get('habit_name')
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        DELETE FROM Habits 
        WHERE Name = ?
    ''', (habit_name,))
    db.commit()
    
    # Check if any row was actually deleted.
    if cursor.rowcount == 0:
        return jsonify(success=False, error="No habit found with that name."), 404

    return jsonify(success=True)

@app.route('/complete_habit', methods=['POST'])
def complete_habit():
    """Mark a habit as completed and reward resources"""
    habit_name = request.json.get('habit_name')
    
    db = get_db()
    with db:
        # Update habit status
        result = db.execute('''
            UPDATE Habits 
            SET Completed = 1 
            WHERE Name = ?
        ''', (habit_name,))
        
        if result.rowcount == 0:
            return jsonify(success=False, error="Habit not found"), 404
        
        # Award resources
        db.execute('UPDATE Garden SET Water = Water + 100000')
        add_experience(db, 200)
    
    return jsonify(success=True)

# --------------------------
# Application Setup
# --------------------------

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)