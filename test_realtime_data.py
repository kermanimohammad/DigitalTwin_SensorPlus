#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify real-time data flow
"""

import requests
import time
import json
from datetime import datetime

def test_realtime_data():
    """Test real-time data flow"""
    print("=" * 60)
    print("Testing Real-time Data Flow")
    print("=" * 60)
    
    # Test 1: Check dashboard API
    print("\n1. Testing Dashboard API...")
    try:
        response = requests.get("http://localhost:5000/api/data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard API is responding")
            print(f"   Success: {data.get('success', False)}")
            print(f"   Devices: {len(data.get('devices', {}))}")
            print(f"   DB Saves: {data.get('db_saves', 0)}")
            print(f"   DB Fails: {data.get('db_fails', 0)}")
            
            # Show some device data
            devices = data.get('devices', {})
            if devices:
                print("\n   Recent device data:")
                for device_id, device_data in list(devices.items())[:3]:
                    print(f"     {device_id}: {device_data.get('value', 'N/A')} {device_data.get('unit', '')}")
            else:
                print("   ⚠️  No device data found")
        else:
            print(f"❌ Dashboard API error: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard API error: {e}")
    
    # Test 2: Check database test endpoint
    print("\n2. Testing Database Connection...")
    try:
        response = requests.get("http://localhost:5000/api/test-db", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Database is working")
                print(f"   Records: {data.get('record_count', 0)}")
                print(f"   Latest: {data.get('latest_record', 'N/A')}")
            else:
                print(f"❌ Database error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Database test error: {response.status_code}")
    except Exception as e:
        print(f"❌ Database test error: {e}")
    
    # Test 3: Monitor data changes over time
    print("\n3. Monitoring data changes (10 seconds)...")
    initial_data = None
    try:
        response = requests.get("http://localhost:5000/api/data", timeout=5)
        if response.status_code == 200:
            initial_data = response.json()
            initial_count = initial_data.get('db_saves', 0)
            print(f"   Initial DB saves: {initial_count}")
            
            print("   Waiting for new data...")
            time.sleep(10)
            
            response = requests.get("http://localhost:5000/api/data", timeout=5)
            if response.status_code == 200:
                final_data = response.json()
                final_count = final_data.get('db_saves', 0)
                print(f"   Final DB saves: {final_count}")
                
                if final_count > initial_count:
                    print(f"✅ New data received! (+{final_count - initial_count} saves)")
                else:
                    print("⚠️  No new data received in 10 seconds")
            else:
                print("❌ Error getting final data")
        else:
            print("❌ Error getting initial data")
    except Exception as e:
        print(f"❌ Monitoring error: {e}")
    
    print("\n" + "=" * 60)
    print("Real-time data test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_realtime_data()
