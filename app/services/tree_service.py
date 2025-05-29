import datetime
from config import TREE_REQUIREMENTS, REQUIRED_WATER_INCREASE_PER_STAGE_PERCENTAGE

class TreeService:
    def __init__(self, tree_model, garden_model):
        self.tree_model = tree_model
        self.garden_model = garden_model
    
    def process_trees(self, garden_level):
        """Process raw tree data into frontend-friendly format"""
        trees_data = self.tree_model.get_trees_data()
        trees = []
        
        for i in range(10):
            required_level = TREE_REQUIREMENTS[i]
            unlocked = garden_level >= required_level
            planted = i < len(trees_data)
            
            tree = {
                "unlocked": unlocked,
                "planted": planted,
                "required_level": required_level
            }
            
            if unlocked and planted:
                tree.update({
                    "name": trees_data[i]['Name'],
                    "stage": trees_data[i]['Stage'],
                    "water": trees_data[i]['Water'],
                    "water_required": trees_data[i]['Water_Required'],
                    "last_watered": trees_data[i]['Last_Watered'],
                    "moisture": trees_data[i]["Moisture"]
                })
            
            trees.append(tree)
        return trees
    
    def water_tree(self, tree_index, amount):
        """Water a specific tree using garden water reserves"""
        garden = self.garden_model.get_garden_data()
        if garden['Water'] < amount:
            return False, "Not enough water!"
        
        trees_data = self.tree_model.get_trees_data()
        if tree_index >= len(trees_data):
            return False, "Tree not found!"
        
        tree = trees_data[tree_index]
        self.tree_model.water_tree(tree['rowid'], amount)
        self.garden_model.update_water(-amount)
        self.check_tree_growth(tree['rowid'])
        
        return True, None
    
    def check_tree_growth(self, tree_id):
        """Check if tree has enough water to advance stages"""
        tree = self.tree_model.get_tree_by_id(tree_id)
        if not tree:
            return 0
        
        tree = dict(tree)  # Convert to dict for mutations
        
        while tree['Water'] >= tree['Water_Required']:
            tree['Water'] -= tree['Water_Required']
            tree['Stage'] += 1
            tree['Water_Required'] += round(tree['Water_Required'] / 100 * REQUIRED_WATER_INCREASE_PER_STAGE_PERCENTAGE, -1)
        
        self.tree_model.update_tree_growth(tree_id, tree['Water'], tree['Stage'], tree['Water_Required'])
        return tree['Stage']