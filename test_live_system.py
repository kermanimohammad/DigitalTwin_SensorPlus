#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Live Sensor System
Tests both the real-time dashboard and live API
"""

import requests
import time
import json
from datetime import datetime

def test_live_api():
    """Test the live sensor API endpoints"""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Live Sensor API...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/live/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Check: PASSED")
            print(f"   MQTT Status: {data['health']['mqtt_status']}")
            print(f"   Connected Devices: {data['health']['connected_devices']}")
        else:
            print("❌ Health Check: FAILED")
    except Exception as e:
        print(f"❌ Health Check: ERROR - {e}")
    
    # Test stats endpoint
    try:
        response = requests.get(f"{base_url}/api/live/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Stats Endpoint: PASSED")
            print(f"   Total Devices: {data['stats']['total_devices']}")
            print(f"   Active Devices: {data['stats']['active_devices']}")
            print(f"   Sensor Types: {data['stats']['sensor_type_counts']}")
        else:
            print("❌ Stats Endpoint: FAILED")
    except Exception as e:
        print(f"❌ Stats Endpoint: ERROR - {e}")
    
    # Test devices endpoint
    try:
        response = requests.get(f"{base_url}/api/live/devices", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Devices Endpoint: PASSED")
            print(f"   Device Count: {data['count']}")
            if data['devices']:
                for device_id in list(data['devices'].keys())[:3]:  # Show first 3 devices
                    device = data['devices'][device_id]
                    latest = device['latest_data']
                    print(f"   - {device_id}: {latest.get('kind')} = {latest.get('value')} {latest.get('unit', '')}")
        else:
            print("❌ Devices Endpoint: FAILED")
    except Exception as e:
        print(f"❌ Devices Endpoint: ERROR - {e}")

def test_dashboard():
    """Test the real-time dashboard"""
    dashboard_url = "http://localhost:5000"
    
    print("\n🌐 Testing Live Dashboard...")
    print("=" * 50)
    
    try:
        response = requests.get(dashboard_url, timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard: ACCESSIBLE")
            print(f"   URL: {dashboard_url}")
            print("   WebSocket: ws://localhost:5000/socket.io/")
        else:
            print("❌ Dashboard: NOT ACCESSIBLE")
    except Exception as e:
        print(f"❌ Dashboard: ERROR - {e}")

def test_mqtt_connection():
    """Test MQTT connection"""
    print("\n📡 Testing MQTT Connection...")
    print("=" * 50)
    
    try:
        import paho.mqtt.client as mqtt
        import time
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("✅ MQTT Broker: CONNECTED")
                client.disconnect()
            else:
                print(f"❌ MQTT Broker: CONNECTION FAILED (rc={rc})")
        
        def on_disconnect(client, userdata, rc):
            print("   MQTT connection test completed")
        
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        
        client.connect("localhost", 1883, 60)
        client.loop_start()
        time.sleep(2)
        client.loop_stop()
        
    except Exception as e:
        print(f"❌ MQTT Test: ERROR - {e}")

def main():
    """Run all tests"""
    print("🚀 Live Sensor System Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test MQTT connection first
    test_mqtt_connection()
    
    # Test API endpoints
    test_live_api()
    
    # Test dashboard
    test_dashboard()
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")
    print("\n📋 Next steps:")
    print("1. Start MQTT simulator: python mqtt_simulator.py")
    print("2. Open dashboard: http://localhost:5000")
    print("3. Check API docs: http://localhost:5001")
    print("4. Monitor real-time data updates")

if __name__ == "__main__":
    main()
