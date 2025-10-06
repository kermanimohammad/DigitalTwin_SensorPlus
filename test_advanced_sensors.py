#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Advanced Sensor Simulations
Tests realistic sensor patterns with weather, seasonal, and occupancy effects
"""

import sys
import os
from datetime import datetime, timedelta
import time

# Add current path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mqtt_simulator_advanced import AdvancedSensorController, RoomType, Season, WeatherCondition

def test_solar_simulation():
    """Test solar panel simulation with different conditions"""
    
    print("=" * 80)
    print("Testing Solar Panel Simulation")
    print("=" * 80)
    
    controller = AdvancedSensorController()
    
    # Test different times of day
    test_times = [
        datetime.now().replace(hour=5, minute=0, second=0),   # Before sunrise
        datetime.now().replace(hour=7, minute=0, second=0),   # Early morning
        datetime.now().replace(hour=12, minute=0, second=0),  # Noon (peak)
        datetime.now().replace(hour=15, minute=0, second=0),  # Afternoon
        datetime.now().replace(hour=18, minute=0, second=0),  # Evening
        datetime.now().replace(hour=20, minute=0, second=0),  # After sunset
    ]
    
    seasons = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]
    weather_conditions = [WeatherCondition.SUNNY, WeatherCondition.CLOUDY, 
                         WeatherCondition.RAINY, WeatherCondition.STORMY]
    
    print(f"Current Season: {controller.get_current_season()}")
    print()
    
    for season in seasons:
        print(f"Season: {season.upper()}")
        print("-" * 50)
        
        # Temporarily set season for testing
        controller._current_season = season
        
        for weather in weather_conditions:
            controller.current_weather = weather
            print(f"  Weather: {weather.upper()}")
            
            for test_time in test_times:
                solar_power = controller.calculate_solar_power(test_time)
                print(f"    {test_time.strftime('%H:%M')}: {solar_power:6.1f}W")
            
            print()
        print()

def test_temperature_simulation():
    """Test temperature simulation with different factors"""
    
    print("=" * 80)
    print("Testing Temperature Simulation")
    print("=" * 80)
    
    controller = AdvancedSensorController()
    
    room_types = [
        (RoomType.BEDROOM, "Bedroom"),
        (RoomType.LIVING_ROOM, "Living Room"),
        (RoomType.KITCHEN, "Kitchen"),
        (RoomType.OFFICE, "Office"),
        (RoomType.BATHROOM, "Bathroom")
    ]
    
    seasons = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]
    
    print("Temperature patterns by room type and season:")
    print()
    
    for season in seasons:
        print(f"Season: {season.upper()}")
        print("-" * 40)
        
        controller._current_season = season
        
        for room_type, room_name in room_types:
            # Test with different occupancy levels
            base_temp = 22.0
            dt = 1.0  # 1 second
            
            # Test with no occupancy
            temp_no_occ = controller.calculate_temperature(
                room_type, datetime.now(), 0.0, base_temp, dt
            )
            
            # Test with high occupancy
            temp_high_occ = controller.calculate_temperature(
                room_type, datetime.now(), 1.0, base_temp, dt
            )
            
            print(f"  {room_name:12} | Base: {base_temp:4.1f}°C | No Occ: {temp_no_occ:4.1f}°C | High Occ: {temp_high_occ:4.1f}°C")
        
        print()

def test_humidity_simulation():
    """Test humidity simulation with weather effects"""
    
    print("=" * 80)
    print("Testing Humidity Simulation")
    print("=" * 80)
    
    controller = AdvancedSensorController()
    
    weather_conditions = [WeatherCondition.SUNNY, WeatherCondition.CLOUDY, 
                         WeatherCondition.RAINY, WeatherCondition.STORMY]
    
    room_types = [
        (RoomType.BEDROOM, "Bedroom"),
        (RoomType.KITCHEN, "Kitchen"),
        (RoomType.BATHROOM, "Bathroom")
    ]
    
    print("Humidity patterns by weather condition:")
    print()
    
    for weather in weather_conditions:
        print(f"Weather: {weather.upper()}")
        print("-" * 40)
        
        controller.current_weather = weather
        
        for room_type, room_name in room_types:
            base_humidity = 50.0
            dt = 1.0
            
            # Test with different occupancy levels
            hum_no_occ = controller.calculate_humidity(
                room_type, datetime.now(), 0.0, base_humidity, dt
            )
            
            hum_high_occ = controller.calculate_humidity(
                room_type, datetime.now(), 1.0, base_humidity, dt
            )
            
            print(f"  {room_name:12} | Base: {base_humidity:4.1f}% | No Occ: {hum_no_occ:4.1f}% | High Occ: {hum_high_occ:4.1f}%")
        
        print()

def test_co2_simulation():
    """Test CO2 simulation with ventilation effects"""
    
    print("=" * 80)
    print("Testing CO2 Simulation")
    print("=" * 80)
    
    controller = AdvancedSensorController()
    
    room_types = [
        (RoomType.BEDROOM, "Bedroom"),
        (RoomType.LIVING_ROOM, "Living Room"),
        (RoomType.KITCHEN, "Kitchen"),
        (RoomType.OFFICE, "Office"),
        (RoomType.BATHROOM, "Bathroom")
    ]
    
    # Test different times of day
    test_times = [
        datetime.now().replace(hour=8, minute=0, second=0),   # Morning (good ventilation)
        datetime.now().replace(hour=12, minute=0, second=0),  # Noon (work hours)
        datetime.now().replace(hour=18, minute=0, second=0),  # Evening (family time)
        datetime.now().replace(hour=23, minute=0, second=0),  # Night (poor ventilation)
    ]
    
    print("CO2 patterns by room type and time:")
    print()
    
    for test_time in test_times:
        print(f"Time: {test_time.strftime('%H:%M')}")
        print("-" * 40)
        
        for room_type, room_name in room_types:
            base_co2 = 450.0
            dt = 1.0
            
            # Test with different occupancy levels
            co2_no_occ = controller.calculate_co2(
                room_type, test_time, 0.0, base_co2, dt
            )
            
            co2_high_occ = controller.calculate_co2(
                room_type, test_time, 1.0, base_co2, dt
            )
            
            print(f"  {room_name:12} | Base: {base_co2:4.0f}ppm | No Occ: {co2_no_occ:4.0f}ppm | High Occ: {co2_high_occ:4.0f}ppm")
        
        print()

def test_weather_changes():
    """Test weather change simulation"""
    
    print("=" * 80)
    print("Testing Weather Change Simulation")
    print("=" * 80)
    
    controller = AdvancedSensorController()
    
    print("Simulating weather changes over time:")
    print("(Each step represents 1 hour)")
    print()
    
    # Simulate 24 hours
    for hour in range(24):
        test_time = datetime.now().replace(hour=hour, minute=0, second=0)
        
        # Update weather (simulate 1 hour = 3600 seconds)
        controller.update_weather(3600.0)
        
        # Calculate solar power
        solar_power = controller.calculate_solar_power(test_time)
        
        if hour % 4 == 0:  # Show every 4 hours
            print(f"Hour {hour:2d}:00 | Weather: {controller.current_weather.upper():8} | Solar: {solar_power:6.1f}W")
    
    print()

def test_seasonal_variations():
    """Test seasonal variations across all sensors"""
    
    print("=" * 80)
    print("Testing Seasonal Variations")
    print("=" * 80)
    
    controller = AdvancedSensorController()
    
    seasons = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]
    test_time = datetime.now().replace(hour=12, minute=0, second=0)  # Noon
    
    print("Sensor values at noon (12:00) across seasons:")
    print()
    
    for season in seasons:
        print(f"Season: {season.upper()}")
        print("-" * 40)
        
        controller._current_season = season
        
        # Solar power
        solar_power = controller.calculate_solar_power(test_time)
        print(f"  Solar Power: {solar_power:6.1f}W")
        
        # Room temperatures
        for room_type, room_name in [
            (RoomType.BEDROOM, "Bedroom"),
            (RoomType.LIVING_ROOM, "Living Room"),
            (RoomType.KITCHEN, "Kitchen")
        ]:
            temp = controller.calculate_temperature(room_type, test_time, 0.5, 22.0, 1.0)
            print(f"  {room_name:12} Temperature: {temp:4.1f}°C")
        
        print()

def run_comprehensive_test():
    """Run all tests in sequence"""
    
    print("Starting Comprehensive Advanced Sensor Tests")
    print("=" * 80)
    print()
    
    try:
        test_solar_simulation()
        test_temperature_simulation()
        test_humidity_simulation()
        test_co2_simulation()
        test_weather_changes()
        test_seasonal_variations()
        
        print("=" * 80)
        print("All advanced sensor tests completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error in test execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_comprehensive_test()
