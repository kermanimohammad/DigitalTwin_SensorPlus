#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for updated separate sensor tables functionality
"""

import sys
import os
from datetime import datetime
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager

def test_updated_models():
    """Test the updated separate tables functionality"""
    print("=" * 60)
    print("Testing Updated Separate Sensor Tables")
    print("=" * 60)
    
    # Test database connection
    print("\n1. Testing database connection...")
    if not db_manager.test_connection():
        print("❌ Database connection failed!")
        return False
    print("✅ Database connection successful!")
    
    # Test saving data to different tables
    print("\n2. Testing data saving to separate tables...")
    
    test_data = [
        {
            'deviceId': 'temp-test-2',
            'kind': 'temperature',
            'value': 26.5,
            'unit': '°C',
            'roomId': 'test-room',
            'ts': int(datetime.now().timestamp() * 1000)
        },
        {
            'deviceId': 'hum-test-2',
            'kind': 'humidity',
            'value': 65.2,
            'unit': '%',
            'roomId': 'test-room',
            'ts': int(datetime.now().timestamp() * 1000)
        },
        {
            'deviceId': 'co2-test-2',
            'kind': 'co2',
            'value': 480,
            'unit': 'ppm',
            'roomId': 'test-room',
            'ts': int(datetime.now().timestamp() * 1000)
        },
        {
            'deviceId': 'light-test-2',
            'kind': 'light',
            'value': 900,
            'unit': 'lux',
            'on': True,
            'powerW': 15.5,
            'roomId': 'test-room',
            'ts': int(datetime.now().timestamp() * 1000)
        },
        {
            'deviceId': 'solar-test-2',
            'kind': 'solar',
            'value': 130.5,
            'unit': 'W',
            'powerW': 130.5,
            'voltage': 24.5,
            'current': 5.33,
            'on': True,
            'ts': int(datetime.now().timestamp() * 1000)
        }
    ]
    
    for data in test_data:
        success = db_manager.save_sensor_data(data)
        if success:
            print(f"   ✅ Saved {data['kind']} data for {data['deviceId']}")
        else:
            print(f"   ❌ Failed to save {data['kind']} data for {data['deviceId']}")
    
    # Test table statistics
    print("\n3. Getting table statistics...")
    stats = db_manager.get_table_statistics()
    for table_name, stat in stats.items():
        if 'error' in stat:
            print(f"   {table_name}: ❌ {stat['error']}")
        else:
            print(f"   {table_name}: {stat['count']} records")
    
    print("\n" + "=" * 60)
    print("✅ Updated models test completed!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_updated_models()
