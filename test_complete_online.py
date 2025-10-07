#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Online System Test
Tests all components: broker, simulator, dashboard, and data flow
"""

import requests
import time
import json
from datetime import datetime

def test_complete_online_system():
    """Test the complete online system"""
    print("=" * 60)
    print("Complete Online System Test")
    print("=" * 60)
    
    # Test 1: Check if system is running
    print("\n1. Checking if system is running...")
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ System is running on port 5000")
        else:
            print(f"❌ System not responding: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to system: {e}")
        print("   Make sure to run: python deploy_online_complete.py")
        return False
    
    # Test 2: Check API endpoints
    print("\n2. Testing API endpoints...")
    endpoints = [
        ("/api/data", "Data API"),
        ("/dashboard", "Dashboard Page")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name}: OK")
            else:
                print(f"   ❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: {e}")
    
    # Test 3: Check data generation
    print("\n3. Testing data generation...")
    try:
        response = requests.get("http://localhost:5000/api/data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            devices = data.get('devices', {})
            message_count = data.get('message_count', 0)
            
            print(f"   📊 Current status:")
            print(f"      Devices: {len(devices)}")
            print(f"      Messages: {message_count}")
            print(f"      Uptime: {data.get('uptime', 0)} seconds")
            
            if len(devices) > 0:
                print("   ✅ Data generation is working")
                
                # Show sample data
                print("   📋 Sample data:")
                for i, (device_id, device_data) in enumerate(list(devices.items())[:3]):
                    print(f"      {device_id}: {device_data.get('value', 'N/A')} {device_data.get('unit', '')}")
            else:
                print("   ⚠️  No devices found - simulator might not be running")
        else:
            print(f"   ❌ Cannot get data: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Data test error: {e}")
    
    # Test 4: Test simulator control
    print("\n4. Testing simulator control...")
    try:
        # Stop simulator
        response = requests.post("http://localhost:5000/api/toggle-simulator", 
                               json={"running": False}, timeout=5)
        if response.status_code == 200:
            print("   ✅ Simulator stopped")
        else:
            print(f"   ❌ Cannot stop simulator: {response.status_code}")
        
        time.sleep(2)
        
        # Start simulator
        response = requests.post("http://localhost:5000/api/toggle-simulator", 
                               json={"running": True}, timeout=5)
        if response.status_code == 200:
            print("   ✅ Simulator started")
        else:
            print(f"   ❌ Cannot start simulator: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Simulator control error: {e}")
    
    # Test 5: Monitor data flow
    print("\n5. Monitoring data flow (10 seconds)...")
    try:
        # Get initial data
        response = requests.get("http://localhost:5000/api/data", timeout=5)
        if response.status_code == 200:
            initial_data = response.json()
            initial_messages = initial_data.get('message_count', 0)
            initial_devices = len(initial_data.get('devices', {}))
            
            print(f"   📊 Initial: {initial_devices} devices, {initial_messages} messages")
            
            # Wait and check again
            time.sleep(10)
            
            response = requests.get("http://localhost:5000/api/data", timeout=5)
            if response.status_code == 200:
                final_data = response.json()
                final_messages = final_data.get('message_count', 0)
                final_devices = len(final_data.get('devices', {}))
                
                print(f"   📊 Final: {final_devices} devices, {final_messages} messages")
                
                if final_messages > initial_messages:
                    print(f"   ✅ Data flow working! (+{final_messages - initial_messages} messages)")
                else:
                    print("   ⚠️  No new messages received")
                
                if final_devices > 0:
                    print(f"   ✅ {final_devices} devices active")
                else:
                    print("   ❌ No devices active")
            else:
                print("   ❌ Cannot get final data")
        else:
            print("   ❌ Cannot get initial data")
    except Exception as e:
        print(f"   ❌ Data flow test error: {e}")
    
    # Test 6: Check sensor types
    print("\n6. Checking sensor types...")
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
                print("   📊 Sensor types detected:")
                for kind, count in sensor_types.items():
                    print(f"      {kind}: {count} devices")
                
                expected_types = ['temperature', 'humidity', 'co2', 'light', 'solar']
                missing_types = [t for t in expected_types if t not in sensor_types]
                
                if not missing_types:
                    print("   ✅ All expected sensor types present")
                else:
                    print(f"   ⚠️  Missing sensor types: {missing_types}")
            else:
                print("   ❌ No sensor types detected")
        else:
            print("   ❌ Cannot get sensor data")
    except Exception as e:
        print(f"   ❌ Sensor type test error: {e}")
    
    print("\n" + "=" * 60)
    print("Complete online system test finished!")
    print("=" * 60)
    print("\n🌐 To view the dashboard, open:")
    print("   http://localhost:5000")
    print("   http://localhost:5000/dashboard")
    print("\n📊 Expected features:")
    print("   - Real-time sensor data updates")
    print("   - 21 devices (5 rooms × 4 sensors + 1 solar)")
    print("   - WebSocket updates every 5 seconds")
    print("   - Toggle simulator on/off")
    print("   - Live statistics")

if __name__ == "__main__":
    test_complete_online_system()
