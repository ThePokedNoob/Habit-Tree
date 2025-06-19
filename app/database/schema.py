import datetime
from database.connection import get_db

def init_db():
    """Initialize database tables and default garden values"""
    db = get_db()
    
    tables = {
        'Trees': '''
            CREATE TABLE IF NOT EXISTS Trees (
                Name TEXT NOT NULL CHECK (Name != ''),
                Creation_Date TEXT NOT NULL,
                Stage INTEGER NOT NULL DEFAULT 1 CHECK (Stage >= 1),
                Water INTEGER NOT NULL DEFAULT 0 CHECK (Water >= 0),
                Water_Required INTEGER NOT NULL DEFAULT 50 CHECK (Water_Required > 0),
                Last_Watered TEXT NOT NULL,
                Moisture INTEGER NOT NULL CHECK (Moisture >= 0 AND Moisture <= 100)
            )
        ''',
        'Garden': '''
            CREATE TABLE IF NOT EXISTS Garden (
                Creation_Date TEXT NOT NULL,
                Level INTEGER NOT NULL DEFAULT 1 CHECK (Level >= 1),
                Experience INTEGER NOT NULL DEFAULT 0 CHECK (Experience >= 0),
                Experience_Required INTEGER NOT NULL DEFAULT 100 CHECK (Experience_Required > 0),
                Water INTEGER NOT NULL DEFAULT 0 CHECK (Water >= 0),
                Daily_Water_Earned INTEGER NOT NULL DEFAULT 0 CHECK (Daily_Water_Earned >= 0)
            )
        ''',
        'Habits': '''
            CREATE TABLE IF NOT EXISTS Habits (
                Name TEXT PRIMARY KEY,
                Creation_Date TEXT NOT NULL,
                Priority INTEGER NOT NULL CHECK (Priority >= 0 AND Priority <= 5),
                Days_Of_The_Week TEXT NOT NULL CHECK (Days_Of_The_Week != ''),
                Completed BOOLEAN NOT NULL DEFAULT 0
            )
        ''',
        'Weather': '''
            CREATE TABLE IF NOT EXISTS Weather (
                Id INTEGER PRIMARY KEY,
                Temperature INTEGER NOT NULL CHECK (Temperature >= -5 AND Temperature <= 35),
                Humidity INTEGER NOT NULL CHECK (Humidity >= 0 AND Humidity <= 100),
                State INTEGER NOT NULL CHECK (State >= 0 AND State <= 100)
            )
        ''',
        'Meta': '''
            CREATE TABLE IF NOT EXISTS Meta (
                key TEXT PRIMARY KEY NOT NULL CHECK (key != ''),
                value TEXT NOT NULL CHECK (value != '')
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
                INSERT INTO Garden (Creation_Date, Level, Experience, Experience_Required, Water, Daily_Water_Earned)
                VALUES (?, 1, 0, 100, 0, 0)
            ''', (datetime.date.today().isoformat(),))
            
        # Initialize weather with default values if empty
        if not cursor.execute("SELECT 1 FROM Weather LIMIT 1").fetchone():
            from models import WeatherModel
            from services import WeatherService
            
            weather_model = WeatherModel(db)
            weather_service = WeatherService(weather_model)
            weather_service.simulate_weather(n_days=4)