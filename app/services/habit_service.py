import datetime
from models.tree import TreeModel

class HabitService:
    def __init__(self, habit_model, garden_service):
        self.habit_model = habit_model
        self.garden_service = garden_service
    
    def process_habits(self):
        """Separate habits into active (today) and scheduled (other days)"""
        habits_data = self.habit_model.get_habits_data()
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
    
    def calculate_water_reward(self, habit_priority):
        """Calculate water reward based on priority and tree count"""
        from config import WATER_PER_TREE, PRIORITY_WEIGHTS
        
        # Get total trees to determine water pool
        tree_count = len(TreeModel.get_all_trees())
        if tree_count == 0:
            return 0
            
        total_water_pool = tree_count * WATER_PER_TREE
        
        # Get all incomplete habits to calculate weight distribution
        incomplete_habits = self.get_incomplete_habits()
        if not incomplete_habits:
            return total_water_pool  # If only one habit, give full amount
            
        # Calculate total weight of all incomplete habits
        total_weight = sum(PRIORITY_WEIGHTS.get(habit['priority'], 1.0) 
                          for habit in incomplete_habits)
        
        # Calculate this habit's share
        habit_weight = PRIORITY_WEIGHTS.get(habit_priority, 1.0)
        water_reward = int((habit_weight / total_weight) * total_water_pool)
        
        return water_reward
    
    def complete_habit(self, habit_name):
        """Mark a habit as completed and reward resources"""
        if not self.habit_model.complete_habit(habit_name):
            return False, "Habit not found"
        
        # Award resources
        from models import GardenModel
        from database import get_db
        garden_model = GardenModel(get_db())
        garden_model.update_water(100000)
        self.garden_service.add_experience(200)
        
        return True, None