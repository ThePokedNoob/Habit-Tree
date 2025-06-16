class GardenModel:
    def __init__(self, db):
        self.db = db
    
    def get_garden_data(self):
        """Retrieve current garden status"""
        return self.db.execute('''
            SELECT Level, Experience, Experience_Required, Water, Daily_Water_Earned
            FROM Garden 
            LIMIT 1
        ''').fetchone()
    
    def update_experience(self, level, experience, experience_required):
        """Update garden experience and level"""
        with self.db:
            self.db.execute('''
                UPDATE Garden 
                SET Level = ?, Experience = ?, Experience_Required = ?
            ''', (level, experience, experience_required))
    
    def update_water(self, water_amount):
        """Update garden water reserves"""
        with self.db:
            self.db.execute('''
                UPDATE Garden 
                SET Water = Water + ?
            ''', (water_amount,))
    
    def add_daily_water_earned(self, water_amount):
        """Add to daily water earned counter"""
        with self.db:
            self.db.execute('''
                UPDATE Garden 
                SET Daily_Water_Earned = Daily_Water_Earned + ?
            ''', (water_amount,))
    
    def reset_daily_water_earned(self):
        """Reset daily water earned counter"""
        with self.db:
            self.db.execute('UPDATE Garden SET Daily_Water_Earned = 0')