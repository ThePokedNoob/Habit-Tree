from config import TREE_REQUIREMENTS, REQUIRED_WATER_INCREASE_PER_STAGE_PERCENTAGE
from config import DEFAULT_MOISTURE, HUMIDITY_INFLUENCE, TEMP_INFLUENCE, WEATHER_STATE_INFLUENCE
from config import MIN_MOISTURE, MAX_MOISTURE, DEFAULT_HUM, DEFAULT_TEMP, DEFAULT_STATE

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
        
        # Calculate moisture increase from watering
        moisture_increase = self._calculate_moisture_increase(tree['Moisture'], amount)
        new_moisture = min(MAX_MOISTURE, tree['Moisture'] + moisture_increase)
        
        # Update tree water, moisture, and last watered time
        self.tree_model.water_tree(tree['rowid'], amount)
        self.tree_model.update_tree_moisture(tree['rowid'], int(new_moisture))
        self.tree_model.update_last_watered(tree['rowid'])
        
        # Update garden water reserves
        self.garden_model.update_water(-amount)
        
        # Check for tree growth
        self.check_tree_growth(tree['rowid'])
        
        return True, None

    def _calculate_moisture_increase(self, current_moisture, water_amount):
        """Calculate how much moisture increases based on water amount and current moisture level"""
        from config import WATER_TO_MOISTURE_RATIO, MOISTURE_BOOST_THRESHOLD, MOISTURE_BOOST_MULTIPLIER
        
        # Base moisture increase
        base_increase = water_amount / WATER_TO_MOISTURE_RATIO
        
        # Apply boost for low moisture
        if current_moisture < MOISTURE_BOOST_THRESHOLD:
            base_increase *= MOISTURE_BOOST_MULTIPLIER
        
        return base_increase
    
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
    
    def daily_tree_update(self, current_weather):
        """Update all trees' moisture levels based on current weather"""
        trees_data = self.tree_model.get_trees_data()
        
        current_humidity = current_weather['Humidity']
        current_temp = current_weather['Temperature']
        current_state = current_weather['State']
        
        for tree in trees_data:
            previous_moisture = tree['Moisture']
            
            # Calculate new moisture using the formula
            new_moisture = (
                previous_moisture +
                HUMIDITY_INFLUENCE * (current_humidity - DEFAULT_HUM) +
                WEATHER_STATE_INFLUENCE * (current_state - DEFAULT_STATE) -
                TEMP_INFLUENCE * (current_temp - DEFAULT_TEMP)
            )
            
            # Clamp moisture to valid range
            new_moisture = max(MIN_MOISTURE, min(MAX_MOISTURE, new_moisture))
            
            # Update tree moisture in database
            self.tree_model.update_tree_moisture(tree['rowid'], int(new_moisture))