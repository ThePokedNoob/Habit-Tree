import datetime
from database import get_db
from models import WeatherModel

class TimeService:
    def __init__(self):
        self.db = get_db()
        self.weather_model = WeatherModel(self.db)
    
    def check_global_time(self):
        """Check if a day has passed and return number of days elapsed"""
        last_run_text = self.weather_model.get_meta('global_last_run')
        now = datetime.datetime.utcnow()
        
        if last_run_text is None:
            self.weather_model.set_meta('global_last_run', now.isoformat())
            return 0
        
        last_run = datetime.datetime.fromisoformat(last_run_text)
        delta = now - last_run
        days_elapsed = delta.days
        
        if days_elapsed > 0:
            new_last_run = last_run + datetime.timedelta(days=days_elapsed)
            self.weather_model.set_meta('global_last_run', new_last_run.isoformat())
        
        return days_elapsed
    
    def trigger_daily_updates(self):
        """Trigger all daily update services"""
        days_elapsed = self.check_global_time()
        
        if days_elapsed > 0:
            # Import services here to avoid circular imports
            from services import WeatherService, HabitService, TreeService
            from models import WeatherModel, HabitModel, GardenModel, TreeModel
            from services import GardenService
            
            # Initialize models and services
            weather_model = WeatherModel(self.db)
            habit_model = HabitModel(self.db)
            garden_model = GardenModel(self.db)
            tree_model = TreeModel(self.db)
            
            weather_service = WeatherService(weather_model)
            garden_service = GardenService(garden_model)
            habit_service = HabitService(habit_model, garden_service)
            tree_service = TreeService(tree_model, garden_model)
            
            # Run daily updates for each elapsed day
            for _ in range(days_elapsed):
                self._run_daily_cycle(weather_service, habit_service, tree_service, garden_model)
        
        return days_elapsed
    
    def _run_daily_cycle(self, weather_service, habit_service, tree_service, garden_model):
        """Run a single day's worth of updates"""
        # Update weather first
        weather_service.simulate_weather()
        
        # Get current weather for tree updates
        current_weather = self.weather_model.get_last_weather()
        
        # Update trees with new weather
        tree_service.daily_tree_update(current_weather)
        
        # Reset habits for new day
        habit_service.reset_daily_habits()
        
        # Reset daily water earned counter
        garden_model.reset_daily_water_earned()