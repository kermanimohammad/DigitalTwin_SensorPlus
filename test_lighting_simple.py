#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test for enhanced lighting scenarios
"""

import sys
import os
from datetime import datetime, timedelta

# Add current path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mqtt_simulator_enhanced import LightingController, RoomType, Season

def test_basic_lighting():
    """Test basic lighting functionality"""
    
    print("=" * 60)
    print("Testing Enhanced Lighting Scenarios")
    print("=" * 60)
    
    controller = LightingController()
    
    # Test different times of day
    test_times = [
        datetime.now().replace(hour=6, minute=0, second=0),   # Morning
        datetime.now().replace(hour=12, minute=0, second=0),  # Noon
        datetime.now().replace(hour=18, minute=0, second=0),  # Evening
        datetime.now().replace(hour=22, minute=0, second=0),  # Night
    ]
    
    room_types = [
        (RoomType.BEDROOM, "Bedroom"),
        (RoomType.LIVING_ROOM, "Living Room"),
        (RoomType.KITCHEN, "Kitchen"),
        (RoomType.OFFICE, "Office"),
        (RoomType.BATHROOM, "Bathroom")
    ]
    
    print(f"Current Season: {controller.get_current_season()}")
    print(f"Current Date: {datetime.now().strftime('%Y-%m-%d %A')}")
    print(f"Weekend: {'Yes' if controller.is_weekend(datetime.now()) else 'No'}")
    print(f"Holiday: {'Yes' if controller.is_holiday(datetime.now()) else 'No'}")
    print()
    
    for test_time in test_times:
        print(f"Time: {test_time.strftime('%H:%M')}")
        print("-" * 40)
        
        for room_type, room_name in room_types:
            light_on, occupancy = controller.should_light_be_on(
                room_type, test_time, "test_room", 0.0
            )
            status = "ON" if light_on else "OFF"
            print(f"  {room_name:12} | {status:3} | Occupancy: {occupancy:.2f}")
        
        print()

def test_seasonal_effects():
    """Test seasonal lighting variations"""
    
    print("=" * 60)
    print("Testing Seasonal Variations")
    print("=" * 60)
    
    controller = LightingController()
    
    seasons = [
        (Season.SPRING, "Spring"),
        (Season.SUMMER, "Summer"),
        (Season.AUTUMN, "Autumn"),
        (Season.WINTER, "Winter")
    ]
    
    test_time = datetime.now().replace(hour=18, minute=0, second=0)  # Evening
    
    for season, season_name in seasons:
        print(f"Season: {season_name}")
        print("-" * 30)
        
        # Temporarily change season for testing
        original_season = controller.get_current_season()
        controller._current_season = season
        
        for room_type, room_name in [
            (RoomType.BEDROOM, "Bedroom"),
            (RoomType.LIVING_ROOM, "Living Room"),
            (RoomType.KITCHEN, "Kitchen")
        ]:
            light_on, occupancy = controller.should_light_be_on(
                room_type, test_time, "test_room", 0.0
            )
            status = "ON" if light_on else "OFF"
            print(f"  {room_name:12} | {status}")
        
        print()

def test_room_patterns():
    """Test room-specific lighting patterns"""
    
    print("=" * 60)
    print("Testing Room-Specific Patterns")
    print("=" * 60)
    
    controller = LightingController()
    
    # Test different hours
    hours_to_test = [6, 8, 12, 18, 22]
    
    for hour in hours_to_test:
        test_time = datetime.now().replace(hour=hour, minute=0, second=0)
        print(f"Hour {hour:02d}:00")
        print("-" * 30)
        
        for room_type, room_name in [
            (RoomType.BEDROOM, "Bedroom"),
            (RoomType.KITCHEN, "Kitchen"),
            (RoomType.OFFICE, "Office"),
            (RoomType.BATHROOM, "Bathroom"),
            (RoomType.LIVING_ROOM, "Living Room")
        ]:
            # Test multiple times to see pattern
            light_results = []
            for i in range(5):
                light_on, occupancy = controller.should_light_be_on(
                    room_type, test_time, f"room{i}", 0.0
                )
                light_results.append(light_on)
            
            light_probability = sum(light_results) / len(light_results)
            status = "ON" if light_probability > 0.5 else "OFF"
            
            print(f"  {room_name:12} | {status:3} | Probability: {light_probability:.2f}")
        
        print()

if __name__ == "__main__":
    print("Starting Enhanced Lighting Test")
    print()
    
    try:
        test_basic_lighting()
        test_seasonal_effects()
        test_room_patterns()
        
        print("=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error in test execution: {e}")
        import traceback
        traceback.print_exc()
