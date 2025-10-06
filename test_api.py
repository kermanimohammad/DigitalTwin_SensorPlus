#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import time

def test_api():
    """Test the sensor API endpoints"""
    
    base_url = "http://localhost:5000"
    
    print("=== Testing Sensor API ===")
    
    # Wait a moment for server to start
    time.sleep(2)
    
    try:
        # Test health check
        print("\n1. Testing health check...")
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("SUCCESS: Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"FAILED: Health check failed: {response.status_code}")
            return
        
        # Test main sensors endpoint
        print("\n2. Testing sensors endpoint...")
        response = requests.get(f"{base_url}/api/sensors")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Sensors endpoint working")
            print(f"   Count: {data['count']} records")
            print(f"   Sample data:")
            for record in data['data'][:3]:
                print(f"     - {record['device_id']} ({record['kind']}): {record['value']} {record['unit'] or ''}")
        else:
            print(f"FAILED: Sensors endpoint failed: {response.status_code}")
        
        # Test with limit
        print("\n3. Testing with limit...")
        response = requests.get(f"{base_url}/api/sensors?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Limit filter working: {data['count']} records")
        else:
            print(f"FAILED: Limit filter failed: {response.status_code}")
        
        # Test room filter
        print("\n4. Testing room filter...")
        response = requests.get(f"{base_url}/api/sensors?room=room1")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Room filter working: {data['count']} records for room1")
        else:
            print(f"FAILED: Room filter failed: {response.status_code}")
        
        # Test stats endpoint
        print("\n5. Testing stats endpoint...")
        response = requests.get(f"{base_url}/api/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data['stats']
            print(f"SUCCESS: Stats endpoint working")
            print(f"   Total records: {stats['total_records']}")
            print(f"   Sensor types: {list(stats['sensor_types'].keys())}")
            print(f"   Rooms: {list(stats['rooms'].keys())}")
        else:
            print(f"FAILED: Stats endpoint failed: {response.status_code}")
        
        # Test rooms endpoint
        print("\n6. Testing rooms endpoint...")
        response = requests.get(f"{base_url}/api/rooms")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Rooms endpoint working: {len(data['rooms'])} rooms")
            for room in data['rooms'][:2]:
                print(f"   - {room['room_id']}: {list(room['sensors'].keys())}")
        else:
            print(f"FAILED: Rooms endpoint failed: {response.status_code}")
        
        print("\n" + "="*50)
        print("API Testing Completed Successfully!")
        print("="*50)
        print("\nYou can now access the API in your browser:")
        print(f"  - Main page: {base_url}")
        print(f"  - Latest data: {base_url}/api/sensors")
        print(f"  - Statistics: {base_url}/api/stats")
        print(f"  - Room data: {base_url}/api/rooms")
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to API server")
        print("Make sure the server is running: python sensor_api.py")
    except Exception as e:
        print(f"ERROR: Error testing API: {e}")

if __name__ == "__main__":
    test_api()
