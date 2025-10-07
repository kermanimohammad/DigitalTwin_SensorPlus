#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for online system with built-in simulator
"""

import requests
import time
import json
from datetime import datetime

def test_online_system():
    """Test online system functionality"""
    print("=" * 60)
    print("Testing Online System with Built-in Simulator")
    print("=" * 60)
    
    # Test 1: Check online dashboard API
    print("\n1. Testing Online Dashboard API...")
    try:
        response = requests.get("http://localhost:5000/api/data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Online Dashboard API is responding")
            print(f"   Success: {data.get('success', False)}")
            print(f"   Devices: {len(data.get('devices', {}))}")
            print(f"   Device Count: {data.get('device_count', 0)}")
            print(f"   Message Count: {data.get('message_count', 0)}")
            print(f"   Uptime: {data.get('uptime', 0)} seconds")
            
            # Show some device data
            devices = data.get('devices', {})
            if devices:
                print("\n   Recent device data:")
                for device_id, device_data in list(devices.items())[:5]:
                    print(f"     {device_id}: {device_data.get('value', 'N/A')} {device_data.get('unit', '')}")
            else:
                print("   ⚠️  No device data found")
        else:
            print(f"❌ Online Dashboard API error: {response.status_code}")
    except Exception as e:
        print(f"❌ Online Dashboard API error: {e}")
    
    # Test 2: Test simulator toggle
    print("\n2. Testing Simulator Toggle...")
    try:
        # Stop simulator
        response = requests.post("http://localhost:5000/api/toggle-simulator", 
                               json={"running": False}, timeout=5)
        if response.status_code == 200:
            print("✅ Simulator stopped successfully")
        else:
            print(f"❌ Error stopping simulator: {response.status_code}")
        
        time.sleep(2)
        
        # Start simulator
        response = requests.post("http://localhost:5000/api/toggle-simulator", 
                               json={"running": True}, timeout=5)
        if response.status_code == 200:
            print("✅ Simulator started successfully")
        else:
            print(f"❌ Error starting simulator: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Simulator toggle error: {e}")
    
    # Test 3: Monitor data changes over time
    print("\n3. Monitoring data changes (15 seconds)...")
    initial_data = None
    try:
        response = requests.get("http://localhost:5000/api/data", timeout=5)
        if response.status_code == 200:
            initial_data = response.json()
            initial_count = initial_data.get('message_count', 0)
            initial_devices = initial_data.get('device_count', 0)
            print(f"   Initial: {initial_devices} devices, {initial_count} messages")
            
            print("   Waiting for new data...")
            time.sleep(15)
            
            response = requests.get("http://localhost:5000/api/data", timeout=5)
            if response.status_code == 200:
                final_data = response.json()
                final_count = final_data.get('message_count', 0)
                final_devices = final_data.get('device_count', 0)
                print(f"   Final: {final_devices} devices, {final_count} messages")
                
                if final_count > initial_count:
                    print(f"✅ New data received! (+{final_count - initial_count} messages)")
                else:
                    print("⚠️  No new data received in 15 seconds")
                
                if final_devices > 0:
                    print(f"✅ Devices detected: {final_devices}")
                else:
                    print("⚠️  No devices detected")
            else:
                print("❌ Error getting final data")
        else:
            print("❌ Error getting initial data")
    except Exception as e:
        print(f"❌ Monitoring error: {e}")
    
    # Test 4: Check different sensor types
    print("\n4. Checking sensor types...")
    try:
        response = requests.get("http://localhost:5000/api/data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            devices = data.get('devices', {})
            
            sensor_types = {}
            for device_id, device_data in devices.items():
                kind = device_data.get('kind', 'unknown')
                sensor_types[kind] = sensor_types.get(kind, 0) + 1
            
            if sensor_types:
                print("   Sensor types detected:")
                for kind, count in sensor_types.items():
                    print(f"     {kind}: {count} devices")
            else:
                print("   ⚠️  No sensor types detected")
        else:
            print("❌ Error getting sensor data")
    except Exception as e:
        print(f"❌ Sensor type check error: {e}")
    
    print("\n" + "=" * 60)
    print("Online system test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_online_system()
