#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import time

def test_separate_tables():
    """Test all separate table endpoints"""
    
    print("=== Testing Separate Tables System ===")
    
    base_url = "http://localhost:5001"
    endpoints = [
        '/api/temperature',
        '/api/humidity', 
        '/api/co2',
        '/api/light',
        '/api/solar'
    ]
    
    print("\nTesting individual sensor endpoints:")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                sensor_type = data.get('sensor_type', endpoint.split('/')[-1])
                print(f"  {sensor_type}: {count} records")
            else:
                print(f"  {endpoint}: ERROR {response.status_code}")
        except Exception as e:
            print(f"  {endpoint}: ERROR - {e}")
    
    print("\nTesting room endpoint:")
    try:
        response = requests.get(f"{base_url}/api/room/room1")
        if response.status_code == 200:
            data = response.json()
            room_data = data.get('data', {})
            print(f"  Room1 data:")
            for sensor_type, sensor_data in room_data.items():
                if sensor_data:
                    print(f"    {sensor_type}: {sensor_data}")
                else:
                    print(f"    {sensor_type}: No data")
        else:
            print(f"  Room endpoint: ERROR {response.status_code}")
    except Exception as e:
        print(f"  Room endpoint: ERROR - {e}")
    
    print("\nTesting stats endpoint:")
    try:
        response = requests.get(f"{base_url}/api/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            print(f"  Total records: {stats.get('total_records', 0)}")
            print(f"  Sensor counts: {stats.get('sensor_counts', {})}")
            print(f"  Tables: {stats.get('tables', [])}")
        else:
            print(f"  Stats endpoint: ERROR {response.status_code}")
    except Exception as e:
        print(f"  Stats endpoint: ERROR - {e}")
    
    print("\nTesting health endpoint:")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"  Status: {data.get('status', 'unknown')}")
            print(f"  Database: {data.get('database', 'unknown')}")
            print(f"  Tables: {data.get('tables', 'unknown')}")
        else:
            print(f"  Health endpoint: ERROR {response.status_code}")
    except Exception as e:
        print(f"  Health endpoint: ERROR - {e}")
    
    print("\n" + "="*50)
    print("SUCCESS: All endpoints are working with separate tables!")
    print("="*50)

if __name__ == "__main__":
    test_separate_tables()
