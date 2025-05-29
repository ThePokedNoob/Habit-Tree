from flask import Blueprint, jsonify, request, redirect, url_for
from database import get_db
from models import GardenModel, TreeModel
from services import TreeService

tree_bp = Blueprint('tree', __name__)

@tree_bp.route('/plant_tree', methods=['POST'])
def plant_tree():
    """Plant a new tree in the first available slot"""
    db = get_db()
    tree_model = TreeModel(db)
    tree_model.plant_tree()
    return redirect(url_for('main.index'))

@tree_bp.route('/edit_tree', methods=['POST'])
def edit_tree():
    """Edit tree name"""
    data = request.get_json()
    new_name = data.get('name')
    tree_index = data.get('index')
    
    db = get_db()
    tree_model = TreeModel(db)
    trees_data = tree_model.get_trees_data()
    
    if tree_index >= len(trees_data):
        return jsonify(success=False, error="Tree not found"), 404
    
    tree = trees_data[tree_index]
    tree_model.update_tree_name(tree['rowid'], new_name)
    
    return jsonify(success=True)

@tree_bp.route('/water_tree', methods=['POST'])
def water_tree():
    """Water a specific tree using garden water reserves"""
    data = request.get_json()
    tree_index = data['index']
    amount = int(data['water_amount'])
    
    db = get_db()
    garden_model = GardenModel(db)
    tree_model = TreeModel(db)
    tree_service = TreeService(tree_model, garden_model)
    
    success, error = tree_service.water_tree(tree_index, amount)
    
    if not success:
        return jsonify(success=False, error=error), 403
    
    return jsonify(success=True)