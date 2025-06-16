DATABASE = "habit_tree_save_file.db"
TREE_REQUIREMENTS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
REQUIRED_WATER_INCREASE_PER_STAGE_PERCENTAGE = 50
REQUIRED_EXPERIENCE_INCREASE_PER_LEVEL_PERCENTAGE = 50

# Weather defaults and ranges
DEFAULT_TEMP = 25.0
DEFAULT_HUM = 50.0
DEFAULT_STATE = 30.0

TEMP_DELTA_RANGE = (-5, 5)
HUM_DELTA_RANGE = (-5.0, 5.0)
STATE_DELTA_RANGE = (-5.0, 5.0)

# Weather influence weights
HUMIDITY_TEMP_INFLUENCE = 0.5
STATE_HUM_INFLUENCE = 0.4
STATE_TEMP_INFLUENCE = 0.2

# Weather value bounds
MIN_TEMP, MAX_TEMP = -5.0, 35.0
MIN_HUM, MAX_HUM = 0.0, 100.0
MIN_STATE, MAX_STATE = 0.0, 100.0

# Weather drifts
DRIFT_TEMP = 0.2
DRIFT_HUM = 0.2
DRIFT_STATE = 0.2

# Daily water limit settings
WATER_PER_PLANTED_TREE = 50  # Base water amount per planted tree

# Tree moisture settings
DEFAULT_MOISTURE = 60
HUMIDITY_INFLUENCE = 0.3
TEMP_INFLUENCE = 0.2
WEATHER_STATE_INFLUENCE = 0.3
MIN_MOISTURE, MAX_MOISTURE = 0, 100

# Watering moisture settings
WATER_TO_MOISTURE_RATIO = 4  # Every 4 water = 1 moisture point
MOISTURE_BOOST_THRESHOLD = 35  # Below this, moisture gains are boosted
MOISTURE_BOOST_MULTIPLIER = 2.0  # Boost multiplier for low moisture