from config import REQUIRED_EXPERIENCE_INCREASE_PER_LEVEL_PERCENTAGE

class GardenService:
    def __init__(self, garden_model):
        self.garden_model = garden_model
    
    def add_experience(self, amount):
        """Add experience to garden and handle level-ups"""
        garden = self.garden_model.get_garden_data()
        new_exp = garden['Experience'] + amount
        level = garden['Level']
        exp_required = garden['Experience_Required']
        
        while new_exp >= exp_required:
            new_exp -= exp_required
            level += 1
            exp_required += round(exp_required / 100 * REQUIRED_EXPERIENCE_INCREASE_PER_LEVEL_PERCENTAGE, -1)
        
        self.garden_model.update_experience(level, new_exp, exp_required)