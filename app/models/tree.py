import datetime

class TreeModel:
    def __init__(self, db):
        self.db = db
    
    def get_trees_data(self):
        """Retrieve first 10 trees ordered by creation date"""
        return self.db.execute('''
            SELECT rowid, *, Creation_Date 
            FROM Trees 
            ORDER BY Creation_Date 
            LIMIT 10
        ''').fetchall()
    
    def get_tree_by_id(self, tree_id):
        """Get a specific tree by its rowid"""
        return self.db.execute('''
            SELECT rowid, * FROM Trees WHERE rowid = ?
        ''', (tree_id,)).fetchone()
    
    def plant_tree(self, name="My Tree"):
        """Plant a new tree"""
        now = datetime.datetime.now().isoformat()
        with self.db:
            self.db.execute('''
                INSERT INTO Trees (Name, Creation_Date, Stage, Water, Water_Required, Last_Watered, Moisture)
                VALUES (?, ?, 1, 0, 50, ?, 60)
            ''', (name, now, now))
    
    def update_tree_name(self, tree_id, new_name):
        """Update tree name"""
        with self.db:
            self.db.execute("UPDATE Trees SET Name = ? WHERE rowid = ?", (new_name, tree_id))
    
    def water_tree(self, tree_id, amount):
        """Add water to a tree"""
        with self.db:
            self.db.execute('''
                UPDATE Trees 
                SET Water = Water + ? 
                WHERE rowid = ?
            ''', (amount, tree_id))
    
    def update_tree_growth(self, tree_id, water, stage, water_required):
        """Update tree growth parameters"""
        with self.db:
            self.db.execute('''
                UPDATE Trees 
                SET Water = ?, Stage = ?, Water_Required = ? 
                WHERE rowid = ?
            ''', (water, stage, water_required, tree_id))