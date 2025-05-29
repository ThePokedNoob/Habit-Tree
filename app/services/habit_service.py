import datetime

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