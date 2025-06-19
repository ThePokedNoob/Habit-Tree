import random
from config import *

class WeatherModel:
    def __init__(self, db):
        self.db = db
    
    def get_all_weather(self):
        """Return all weather rows ordered oldest→newest"""
        return self.db.execute('''
            SELECT Temperature, Humidity, State
            FROM Weather
            ORDER BY ROWID ASC
        ''').fetchall()
    
    def get_weather_count(self):
        """Return number of rows in Weather."""
        cur = self.db.execute('SELECT COUNT(*) FROM Weather')
        return cur.fetchone()[0]
    
    def get_last_weather(self):
        """Return the last (most recent) weather row."""
        return self.db.execute('''
            SELECT Temperature, Humidity, State 
            FROM Weather
            ORDER BY ROWID DESC
            LIMIT 1
        ''').fetchone()
    
    def insert_weather(self, temp, hum, state):
        """Insert new weather data"""
        self.db.execute('''
            INSERT OR REPLACE INTO Weather (Temperature, Humidity, State)
            VALUES (?, ?, ?)
        ''', (int(temp), int(hum), int(state)))
        self.db.commit()
    
    def delete_oldest_weather(self):
        """Delete the oldest weather record"""
        self.db.execute('''
            DELETE FROM Weather
            WHERE ROWID = (
                SELECT ROWID FROM Weather
                ORDER BY ROWID ASC LIMIT 1
            )
        ''')
        self.db.commit()
    
    def get_meta(self, key):
        """Get metadata value"""
        cur = self.db.execute('SELECT value FROM Meta WHERE key = ?', (key,))
        row = cur.fetchone()
        return row[0] if row else None
    
    def set_meta(self, key, value):
        """Set metadata value"""
        self.db.execute('''
            INSERT INTO Meta(key, value)
            VALUES(?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        ''', (key, value))
        self.db.commit()