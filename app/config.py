#config.py - Responsible for storing all the configurable variables, for ease of access

DATABASE = "habit_tree_save_file.db"                    # SQLite3 local database path for storing all the data
TREE_REQUIREMENTS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]     # The garden level required to unlock each tree slot
REQUIRED_WATER_INCREASE_PER_STAGE_PERCENTAGE = 50       # How much more water is needed to stage up a tree as a percentage per stage (each stage requires 50% more water than previous)
REQUIRED_EXPERIENCE_INCREASE_PER_LEVEL_PERCENTAGE = 50  # How much more experience is needed to level up the garden as a percentage per level (each level requires 50% more XP)

# Weather defaults and ranges
DEFAULT_TEMP = 25.0     # The baseline temperature that weather drifts toward (25°C)
DEFAULT_HUM = 50.0      # The baseline humidity that weather drifts toward (50%)
DEFAULT_STATE = 30.0    # The baseline weather state that drifts toward (30 = partly cloudy on 0-100 scale)

TEMP_DELTA_RANGE = (-5, 5)      # Daily temperature random change range
HUM_DELTA_RANGE = (-5.0, 5.0)   # Daily humidity bonus random change range
STATE_DELTA_RANGE = (-5.0, 5.0) # Daily weather state bomus random change range

# Weather influence weights
HUMIDITY_TEMP_INFLUENCE = 0.5   # How much temperature changes affect humidity (higher temp = lower humidity)
STATE_HUM_INFLUENCE = 0.4       # How much humidity changes affect weather state (higher humidity = more cloudy/rainy)
STATE_TEMP_INFLUENCE = 0.2      # How much temperature changes affect weather state (higher temp = less cloudy)

# Weather value bounds
MIN_TEMP, MAX_TEMP = -5.0, 35.0     # The clamped values for temperature
MIN_HUM, MAX_HUM = 0.0, 100.0       # The clamped values for humidity
MIN_STATE, MAX_STATE = 0.0, 100.0   # The clamped values for weather state

# Weather drifts
DRIFT_TEMP = 0.2    # How strongly temperature drifts back toward DEFAULT_TEMP each day
DRIFT_HUM = 0.2     # How strongly humidity drifts back toward DEFAULT_HUM each day
DRIFT_STATE = 0.2   # How strongly weather state drifts back toward DEFAULT_STATE each day

# Daily water limit settings
WATER_PER_PLANTED_TREE = 50  # Water available to earn per planted tree each day

# Tree moisture settings
DEFAULT_MOISTURE = 60           # Starting moisture level for newly planted trees
HUMIDITY_INFLUENCE = 0.3        # How much daily humidity affects tree moisture (higher humidity = higher moisture)
TEMP_INFLUENCE = 0.2            # How much daily temperature affects tree moisture (higher temp = lower moisture)
WEATHER_STATE_INFLUENCE = 0.3   # How much weather state affects tree moisture (rain = higher moisture)
MIN_MOISTURE, MAX_MOISTURE = 0, 100  # Clamped values for tree moisture

# Water efficiency settings
WATER_EFFICIENCY_REDUCTION = 0.7  # Maximum efficiency reduction for very moist trees (70% reduction)
WATER_TO_MOISTURE_RATIO = 2     # How much water equals 1 moisture point (higher = less moisture per water)
MOISTURE_BOOST_THRESHOLD = 30   # Below this level, watering provides bonus moisture
MOISTURE_BOOST_MULTIPLIER = 1.5 # Multiplier for moisture gain when tree is very dry

# Moisture display thresholds and labels
MOISTURE_VERY_DRY_THRESHOLD = 30        # Below this level shows "Very Dry" (red)
MOISTURE_DRY_THRESHOLD = 50             # Below this level shows "Dry" (yellow/warning)
MOISTURE_NEUTRAL_THRESHOLD = 70         # Below this level shows "Neutral" (secondary/gray)
MOISTURE_HEALTHY_THRESHOLD = 90         # Below this level shows "Healthy" (green)

# Moisture status labels (customizable text)
MOISTURE_VERY_DRY_LABEL = "Very Dry"
MOISTURE_DRY_LABEL = "Dry"
MOISTURE_NEUTRAL_LABEL = "Neutral"
MOISTURE_HEALTHY_LABEL = "Healthy"
MOISTURE_TOO_MOIST_LABEL = "Too moist"