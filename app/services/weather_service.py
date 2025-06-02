import datetime
import random
from config import *

def clamp(value, min_val, max_val):
    """Clamp a value to the provided bounds."""
    return max(min_val, min(max_val, value))

class WeatherService:
    def __init__(self, weather_model):
        self.weather_model = weather_model
    
    def simulate_weather(self, n_days=4):
        """Run a rolling window of at most n_days in the Weather table."""
        # Count existing rows
        count = self.weather_model.get_weather_count()
        
        # Seed defaults if empty
        if count == 0:
            self.weather_model.insert_weather(DEFAULT_TEMP, DEFAULT_HUM, DEFAULT_STATE)
            count = 1
        
        # Rotate out oldest to keep at most n_days-1 existing
        if count >= n_days:
            to_delete = count - (n_days - 1)
            for _ in range(to_delete):
                self.weather_model.delete_oldest_weather()
            count = self.weather_model.get_weather_count()
        
        # Append new days until we have n_days
        while count < n_days:
            temp_prev, hum_prev, state_prev = self.weather_model.get_last_weather()
            
            # Temperature
            temp_delta = random.uniform(*TEMP_DELTA_RANGE)
            temp_curr = clamp(
                temp_prev + temp_delta + DRIFT_TEMP * (DEFAULT_TEMP - temp_prev),
                MIN_TEMP, MAX_TEMP
            )
            
            # Humidity
            hum_delta = random.uniform(*HUM_DELTA_RANGE)
            hum_curr = clamp(
                hum_prev + hum_delta - HUMIDITY_TEMP_INFLUENCE * (temp_curr - temp_prev) + DRIFT_HUM * (DEFAULT_HUM - hum_prev),
                MIN_HUM, MAX_HUM
            )
            
            # State
            state_delta = random.uniform(*STATE_DELTA_RANGE)
            state_curr = clamp(
                state_prev + state_delta + STATE_HUM_INFLUENCE * (hum_curr - hum_prev) + STATE_TEMP_INFLUENCE * (temp_curr - temp_prev) + DRIFT_STATE * (DEFAULT_STATE - state_prev),
                MIN_STATE, MAX_STATE
            )
            
            self.weather_model.insert_weather(temp_curr, hum_curr, state_curr)
            count += 1