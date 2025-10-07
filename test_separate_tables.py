#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for separate sensor tables functionality
"""

import sys
import os
from datetime import datetime
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, TemperatureData, HumidityData, CO2Data, LightData, SolarData, SensorData

def test_separate_tables():
    """Test the separate tables functionality"""
    print("=" * 60)
    print("Testing Separate Sensor Tables")
    print("=" * 60)
    
    # Test database connection
    print("\n1. Testing database connection...")
    if not db_manager.test_connection():
        print("❌ Database connection failed!")
        return False
    print("✅ Database connection successful!")
    
    # Test table statistics
    print("\n2. Getting table statistics...")
    stats = db_manager.get_table_statistics()
    for table_name, stat in stats.items():
        if 'error' in stat:
            print(f"   {table_name}: ❌ {stat['error']}")
        else:
            print(f"   {table_name}: {stat['count']} records, latest: {stat['latest_timestamp']}")
    
    # Test saving data to different tables
    print("\n3. Testing data saving to separate tables...")
    
    test_data = [
        {
            'deviceId': 'temp-test-1',
            'kind': 'temperature',
            'value': 25.5,
            'unit': '°C',
            'roomId': 'test-room',
            'ts': int(datetime.now().timestamp() * 1000)
        },
        {
            'deviceId': 'hum-test-1',
            'kind': 'humidity',
            'value': 60.2,
            'unit': '%',
            'roomId': 'test-room',
            'ts': int(datetime.now().timestamp() * 1000)
        },
        {
            'deviceId': 'co2-test-1',
            'kind': 'co2',
            'value': 450,
            'unit': 'ppm',
            'roomId': 'test-room',
            'ts': int(datetime.now().timestamp() * 1000)
        },
        {
            'deviceId': 'light-test-1',
            'kind': 'light',
            'value': 800,
            'unit': 'lux',
            'roomId': 'test-room',
            'ts': int(datetime.now().timestamp() * 1000)
        },
        {
            'deviceId': 'solar-test-1',
            'kind': 'solar',
            'value': 120.5,
            'unit': 'W',
            'powerW': 120.5,
            'voltage': 24.0,
            'current': 5.02,
            'on_status': True,
            'roomId': 'test-room',
            'ts': int(datetime.now().timestamp() * 1000)
        }
    ]
    
    for data in test_data:
        success = db_manager.save_sensor_data(data)
        if success:
            print(f"   ✅ Saved {data['kind']} data for {data['deviceId']}")
        else:
            print(f"   ❌ Failed to save {data['kind']} data for {data['deviceId']}")
    
    # Test retrieving data from specific tables
    print("\n4. Testing data retrieval from specific tables...")
    
    sensor_types = ['temperature', 'humidity', 'co2', 'light', 'solar']
    for sensor_type in sensor_types:
        data = db_manager.get_recent_data(kind=sensor_type, limit=5)
        print(f"   {sensor_type}: {len(data)} recent records")
        if data:
            latest = data[0]
            print(f"      Latest: {latest.device_id} = {latest.value} {latest.unit}")
    
    # Test retrieving data from all tables
    print("\n5. Testing data retrieval from all tables...")
    all_data = db_manager.get_recent_data(limit=10)
    print(f"   Total recent records from all tables: {len(all_data)}")
    
    # Test room data retrieval
    print("\n6. Testing room data retrieval...")
    room_data = db_manager.get_room_data('test-room', limit=10)
    print(f"   Records for test-room: {len(room_data)}")
    
    # Final statistics
    print("\n7. Final table statistics...")
    final_stats = db_manager.get_table_statistics()
    for table_name, stat in final_stats.items():
        if 'error' in stat:
            print(f"   {table_name}: ❌ {stat['error']}")
        else:
            print(f"   {table_name}: {stat['count']} records")
    
    print("\n" + "=" * 60)
    print("✅ Separate tables test completed!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_separate_tables()