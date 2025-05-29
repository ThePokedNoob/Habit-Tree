import sqlite3

class HabitModel:
    def __init__(self, db):
        self.db = db
    
    def get_habits_data(self):
        """Retrieve all habits"""
        return self.db.execute('''
            SELECT Name, Creation_Date, Priority, Days_Of_The_Week, Completed 
            FROM Habits
        ''').fetchall()
    
    def add_habit(self, name, priority, days_of_week):
        """Add a new habit"""
        try:
            with self.db:
                self.db.execute(
                    "INSERT INTO Habits (Name, Creation_Date, Priority, Days_Of_The_Week, Completed) VALUES (?, datetime('now'), ?, ?, false)",
                    (name, priority, days_of_week)
                )
            return True, None
        except sqlite3.IntegrityError:
            return False, "A habit with that name already exists."
    
    def update_habit(self, existing_name, new_name, priority, days_of_week):
        """Update an existing habit"""
        try:
            with self.db:
                cursor = self.db.execute('''
                    UPDATE Habits 
                    SET Name = ?, Priority = ?, Days_Of_The_Week = ?
                    WHERE Name = ?
                ''', (new_name, priority, days_of_week, existing_name))
                
                if cursor.rowcount == 0:
                    return False, "No habit found with that name."
            return True, None
        except sqlite3.IntegrityError:
            return False, "The new habit name already exists."
    
    def delete_habit(self, name):
        """Delete a habit"""
        with self.db:
            cursor = self.db.execute('DELETE FROM Habits WHERE Name = ?', (name,))
            return cursor.rowcount > 0
    
    def complete_habit(self, name):
        """Mark a habit as completed"""
        with self.db:
            result = self.db.execute('''
                UPDATE Habits 
                SET Completed = 1 
                WHERE Name = ?
            ''', (name,))
            return result.rowcount > 0