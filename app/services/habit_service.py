import datetime
from config import WATER_PER_PLANTED_TREE

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
    
    def reset_daily_habits(self):
        """Reset all habits to incomplete for the new day"""
        self.habit_model.reset_all_habits()
    
    def calculate_max_daily_water(self, garden_level, planted_tree_count):
        """Calculate maximum daily water based on trees and garden level"""
        return planted_tree_count * WATER_PER_PLANTED_TREE + garden_level
    
    def calculate_priority_weight(self, priority):
        """Convert priority (0-5) to weight (higher priority = higher weight)"""
        # Priority 0 = highest priority = weight 6
        # Priority 5 = lowest priority = weight 1
        return 6 - priority
    
    def calculate_water_reward_for_habit(self, habit_priority, garden_level, planted_tree_count):
        """Calculate water reward for a specific habit based on its priority"""
        active_habits, _ = self.process_habits()
        
        if not active_habits:
            return 0
        
        # Calculate total priority weight of all active habits
        total_weight = sum(self.calculate_priority_weight(habit['priority']) for habit in active_habits)
        
        if total_weight == 0:
            return 0
        
        # Calculate this habit's share based on priority weight
        max_daily_water = self.calculate_max_daily_water(garden_level, planted_tree_count)
        habit_weight = self.calculate_priority_weight(habit_priority)
        
        return int((habit_weight / total_weight) * max_daily_water)
    
    def get_active_habits_count(self):
        """Get count of today's active habits"""
        active_habits, _ = self.process_habits()
        return len(active_habits)
    
    def complete_habit(self, habit_name):
        """Mark a habit as completed and reward resources"""
        if not self.habit_model.complete_habit(habit_name):
            return False, "Habit not found"
        
        # Get current garden data and planted tree count
        from models import GardenModel, TreeModel
        from database import get_db
        
        db = get_db()
        garden_model = GardenModel(db)
        tree_model = TreeModel(db)
        
        garden_data = garden_model.get_garden_data()
        planted_trees = tree_model.get_trees_data()
        planted_tree_count = len(planted_trees)
        
        # Find the completed habit's priority
        active_habits, _ = self.process_habits()
        completed_habit = next((h for h in active_habits if h['name'] == habit_name), None)
        
        if not completed_habit:
            return False, "Habit not found in active habits"
        
        # Calculate water reward based on priority
        water_reward = self.calculate_water_reward_for_habit(
            completed_habit['priority'],
            garden_data['Level'], 
            planted_tree_count
        )
        
        # Check if adding this water would exceed daily limit
        max_daily_water = self.calculate_max_daily_water(garden_data['Level'], planted_tree_count)
        current_daily_earned = garden_data['Daily_Water_Earned']
        
        if current_daily_earned + water_reward > max_daily_water:
            water_reward = max_daily_water - current_daily_earned
            if water_reward <= 0:
                return False, "Daily water limit already reached"
        
        # Award resources
        garden_model.update_water(water_reward)
        garden_model.add_daily_water_earned(water_reward)
        self.garden_service.add_experience(200)
        
        return True, None