from flask import Blueprint, render_template
from database import get_db
from models import GardenModel, TreeModel, HabitModel, WeatherModel
from services import GardenService, TreeService, HabitService, TimeService
from config import (
    MOISTURE_VERY_DRY_THRESHOLD, MOISTURE_DRY_THRESHOLD, 
    MOISTURE_NEUTRAL_THRESHOLD, MOISTURE_HEALTHY_THRESHOLD,
    MOISTURE_VERY_DRY_LABEL, MOISTURE_DRY_LABEL,
    MOISTURE_NEUTRAL_LABEL, MOISTURE_HEALTHY_LABEL, MOISTURE_TOO_MOIST_LABEL
)
import datetime

main_bp = Blueprint('main', __name__)

def state_to_text(state):
    """Convert numeric state (0–100) into weather description."""
    s = float(state)
    if 0 <= s <= 20:
        return "Sunny"
    elif 21 <= s <= 40:
        return "Partly Cloudy"
    elif 41 <= s <= 60:
        return "Cloudy"
    elif 61 <= s <= 80:
        return "Rainy"
    elif 81 <= s <= 100:
        return "Thunderstorm"
    else:
        return "Unknown"

def calculate_time_until_day_ends(weather_model):
    """Calculate time remaining until day ends"""
    last_run_text = weather_model.get_meta('global_last_run')
    if not last_run_text:
        return "Unknown"
    
    try:
        last_run = datetime.datetime.fromisoformat(last_run_text)
        next_day = last_run + datetime.timedelta(days=1)
        now = datetime.datetime.utcnow()
        
        if now >= next_day:
            return "Day ended"
        
        time_left = next_day - now
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60
        
        return f"{hours}h {minutes}m"
    except:
        return "Unknown"

@main_bp.route('/')
def index():
    """Main dashboard showing garden status, trees, and habits"""
    db = get_db()
    
    # Initialize models
    garden_model = GardenModel(db)
    tree_model = TreeModel(db)
    habit_model = HabitModel(db)
    weather_model = WeatherModel(db)
    
    # Initialize services
    garden_service = GardenService(garden_model)
    tree_service = TreeService(tree_model, garden_model)
    habit_service = HabitService(habit_model, garden_service)
    time_service = TimeService()
    
    # Check time and trigger global daily updates
    time_service.trigger_daily_updates()
    
    # Get processed data
    garden_data = garden_model.get_garden_data()
    active_habits, scheduled_habits = habit_service.process_habits()
    trees = tree_service.process_trees(garden_data['Level'])
    weather = weather_model.get_all_weather()
    time_until_day_ends = calculate_time_until_day_ends(weather_model)
    
    # Moisture configuration for template
    moisture_config = {
        'very_dry_threshold': MOISTURE_VERY_DRY_THRESHOLD,
        'dry_threshold': MOISTURE_DRY_THRESHOLD,
        'neutral_threshold': MOISTURE_NEUTRAL_THRESHOLD,
        'healthy_threshold': MOISTURE_HEALTHY_THRESHOLD,
        'very_dry_label': MOISTURE_VERY_DRY_LABEL,
        'dry_label': MOISTURE_DRY_LABEL,
        'neutral_label': MOISTURE_NEUTRAL_LABEL,
        'healthy_label': MOISTURE_HEALTHY_LABEL,
        'too_moist_label': MOISTURE_TOO_MOIST_LABEL
    }
    
    return render_template("index.html",
        trees=trees,
        active_habits=active_habits,
        scheduled_habits=scheduled_habits,
        garden=garden_data,
        weather=weather,
        time_until_day_ends=time_until_day_ends,
        state_to_text=state_to_text,
        moisture_config=moisture_config
    )