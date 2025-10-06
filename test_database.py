#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import time
from database import db_manager

def test_database_connection():
    """Test database connection"""
    print("=== Testing Database Connection ===")
    if db_manager.test_connection():
        print("Database connection successful!")
        return True
    else:
        print("Database connection failed!")
        return False

def test_save_sample_data():
    """Test saving sample sensor data"""
    print("\n=== Testing Data Storage ===")
    
    # Sample temperature data
    temp_data = {
        "deviceId": "temp-1",
        "kind": "temperature",
        "roomId": "room1",
        "ts": int(time.time() * 1000),
        "value": 23.5,
        "unit": "C"
    }
    
    # Sample humidity data
    hum_data = {
        "deviceId": "hum-1",
        "kind": "humidity",
        "roomId": "room1",
        "ts": int(time.time() * 1000),
        "value": 45.2,
        "unit": "%"
    }
    
    # Sample CO2 data
    co2_data = {
        "deviceId": "co2-1",
        "kind": "co2",
        "roomId": "room1",
        "ts": int(time.time() * 1000),
        "value": 520,
        "unit": "ppm"
    }
    
    # Sample solar data
    solar_data = {
        "deviceId": "solar-plant",
        "kind": "solar",
        "ts": int(time.time() * 1000),
        "powerW": 850.5,
        "voltage": 48.2,
        "current": 17.6
    }
    
    # Test saving each type of data
    test_data = [temp_data, hum_data, co2_data, solar_data]
    
    for data in test_data:
        print(f"Testing {data['kind']} data...")
        success = db_manager.save_sensor_data(data)
        if success:
            print(f"SUCCESS: {data['kind']} data saved successfully")
        else:
            print(f"FAILED: Failed to save {data['kind']} data")
    
    return True

def test_retrieve_data():
    """Test retrieving data from database"""
    print("\n=== Testing Data Retrieval ===")
    
    # Get recent data
    recent_data = db_manager.get_recent_data(limit=10)
    print(f"Retrieved {len(recent_data)} recent records")
    
    for record in recent_data[:5]:  # Show first 5 records
        print(f"  - {record.device_id} ({record.kind}): {record.value} {record.unit or ''} at {record.timestamp}")
    
    # Get room data
    room_data = db_manager.get_room_data("room1", limit=5)
    print(f"\nRetrieved {len(room_data)} records for room1")
    
    for record in room_data:
        print(f"  - {record.device_id} ({record.kind}): {record.value} {record.unit or ''} at {record.timestamp}")
    
    return True

def main():
    """Main test function"""
    print("=== Database Test Suite ===")
    
    # Test 1: Database connection
    if not test_database_connection():
        print("Cannot proceed with tests due to connection failure")
        return
    
    # Test 2: Save sample data
    test_save_sample_data()
    
    # Test 3: Retrieve data
    test_retrieve_data()
    
    print("\n=== Test Suite Completed ===")

if __name__ == "__main__":
    main()
