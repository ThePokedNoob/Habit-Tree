from flask import Blueprint, jsonify, request
from database import get_db
from models import GardenModel, HabitModel
from services import GardenService, HabitService

habit_bp = Blueprint('habit', __name__)

@habit_bp.route('/add_habit', methods=['POST'])
def add_habit():
    """Add a new habit"""
    data = request.get_json()
    habit_name = data.get('habit_name')
    habit_priority = data.get('habit_priority')
    habit_days_of_the_week = data.get('days_of_the_week')
    
    db = get_db()
    habit_model = HabitModel(db)
    success, error = habit_model.add_habit(habit_name, habit_priority, habit_days_of_the_week)
    
    if not success:
        return jsonify(success=False, error=error), 400
    
    return jsonify(success=True)

@habit_bp.route('/edit_habit', methods=['PUT'])
def edit_habit():
    """Edit an existing habit"""
    data = request.get_json()
    existing_habit_name = data.get('existing_habit_name')
    new_habit_name = data.get('new_habit_name')
    habit_priority = data.get('habit_priority')
    habit_days_of_the_week = data.get('days_of_the_week')
    
    db = get_db()
    habit_model = HabitModel(db)
    success, error = habit_model.update_habit(existing_habit_name, new_habit_name, habit_priority, habit_days_of_the_week)
    
    if not success:
        status_code = 404 if "not found" in error.lower() else 400
        return jsonify(success=False, error=error), status_code
    
    return jsonify(success=True)

@habit_bp.route('/delete_habit', methods=['DELETE'])
def delete_habit():
    """Delete a habit"""
    data = request.get_json()
    habit_name = data.get('habit_name')
    
    db = get_db()
    habit_model = HabitModel(db)
    success = habit_model.delete_habit(habit_name)
    
    if not success:
        return jsonify(success=False, error="No habit found with that name."), 404
    
    return jsonify(success=True)

@habit_bp.route('/complete_habit', methods=['POST'])
def complete_habit():
    """Mark a habit as completed and reward resources"""
    habit_name = request.json.get('habit_name')
    
    db = get_db()
    garden_model = GardenModel(db)
    habit_model = HabitModel(db)
    garden_service = GardenService(garden_model)
    habit_service = HabitService(habit_model, garden_service)
    
    success, error = habit_service.complete_habit(habit_name)
    
    if not success:
        return jsonify(success=False, error=error), 404
    
    return jsonify(success=True)