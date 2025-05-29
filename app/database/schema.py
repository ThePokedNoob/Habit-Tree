import datetime
from database.connection import get_db

def init_db():
    """Initialize database tables and default garden values"""
    db = get_db()
    
    tables = {
        'Trees': '''
            CREATE TABLE IF NOT EXISTS Trees (
                Name TEXT,
                Creation_Date TEXT,
                Stage INTEGER,
                Water INTEGER,
                Water_Required INTEGER,
                Last_Watered TEXT,
                Moisture INTEGER
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
        ''',
        'Weather': '''
            CREATE TABLE IF NOT EXISTS Weather (
                Id INTEGER PRIMARY KEY,
                Temperature INTEGER NOT NULL,
                Humidity INTEGER NOT NULL,
                State INTEGER NOT NULL
            )
        ''',
        'Meta': '''
            CREATE TABLE IF NOT EXISTS Meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        '''
    }

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