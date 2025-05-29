from flask import Blueprint, render_template
from database import get_db
from models import GardenModel, TreeModel, HabitModel, WeatherModel
from services import GardenService, TreeService, HabitService, WeatherService

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
    weather_service = WeatherService(weather_model)
    
    # Check time and update weather
    weather_service.check_time()
    
    # Get processed data
    garden_data = garden_model.get_garden_data()
    active_habits, scheduled_habits = habit_service.process_habits()
    trees = tree_service.process_trees(garden_data['Level'])
    weather = weather_model.get_all_weather()
    
    return render_template("index.html",
        trees=trees,
        active_habits=active_habits,
        scheduled_habits=scheduled_habits,
        garden=garden_data,
        weather=weather,
        state_to_text=state_to_text
    )