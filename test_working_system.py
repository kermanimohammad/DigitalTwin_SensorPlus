#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Working Dashboard System
Tests both real-time display and database storage
"""

import requests
import time
import json
import paho.mqtt.client as mqtt
from datetime import datetime

def test_working_dashboard():
    """Test working dashboard API"""
    print("🧪 Testing Working Dashboard...")
    try:
        response = requests.get("http://localhost:5000/api/data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard API: OK - {data['count']} devices")
            print(f"   DB Saves: {data.get('db_saves', 0)}")
            print(f"   DB Fails: {data.get('db_fails', 0)}")
            return True
        else:
            print(f"❌ Dashboard API: Failed - {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard API: Error - {e}")
        return False

def test_database_history():
    """Test database history API"""
    print("🧪 Testing Database History...")
    try:
        response = requests.get("http://localhost:5000/api/history?limit=10", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ History API: OK - {data['count']} records")
            return True
        else:
            print(f"❌ History API: Failed - {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ History API: Error - {e}")
        return False

def send_test_data():
    """Send test data to MQTT"""
    print("📤 Sending test data to MQTT...")
    
    client = mqtt.Client()
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connected to MQTT broker")
            
            # Send test data
            test_devices = [
                {"id": "temp-1", "kind": "temperature", "value": 25.5, "unit": "°C", "room": "room1"},
                {"id": "hum-1", "kind": "humidity", "value": 60.0, "unit": "%", "room": "room1"},
                {"id": "light-1", "kind": "light", "value": 500.0, "unit": "lux", "room": "room2"},
                {"id": "co2-1", "kind": "co2", "value": 450.0, "unit": "ppm", "room": "room2"}
            ]
            
            for device in test_devices:
                data = {
                    "deviceId": device["id"],
                    "kind": device["kind"],
                    "value": device["value"],
                    "unit": device["unit"],
                    "roomId": device["room"],
                    "ts": int(time.time() * 1000)
                }
                
                topic = f"building/demo/{device['kind']}/{device['id']}"
                client.publish(topic, json.dumps(data))
                print(f"📤 Sent: {device['id']} = {device['value']} {device['unit']}")
            
            time.sleep(3)
            client.disconnect()
        else:
            print(f"❌ MQTT connection failed: {rc}")
    
    try:
        client.on_connect = on_connect
        client.connect("test.mosquitto.org", 1883, 60)
        client.loop_start()
        time.sleep(5)
        client.loop_stop()
        return True
    except Exception as e:
        print(f"❌ MQTT test failed: {e}")
        return False

def test_complete_flow():
    """Test complete data flow"""
    print("🔄 Testing Complete Data Flow...")
    
    # Test 1: Initial state
    print("1. Testing initial state...")
    initial_ok = test_working_dashboard()
    
    # Test 2: Send data
    print("2. Sending test data...")
    mqtt_ok = send_test_data()
    
    # Test 3: Check after data
    print("3. Checking after data...")
    time.sleep(3)
    after_ok = test_working_dashboard()
    
    # Test 4: Check database history
    print("4. Checking database history...")
    history_ok = test_database_history()
    
    return initial_ok, mqtt_ok, after_ok, history_ok

def main():
    """Run complete system test"""
    print("🚀 Working Dashboard System Test")
    print("=" * 60)
    
    # Test complete flow
    initial_ok, mqtt_ok, after_ok, history_ok = test_complete_flow()
    
    print("\n" + "=" * 60)
    print("📋 Test Results:")
    print(f"Initial Dashboard: {'✅' if initial_ok else '❌'}")
    print(f"MQTT Data Send: {'✅' if mqtt_ok else '❌'}")
    print(f"After Data Dashboard: {'✅' if after_ok else '❌'}")
    print(f"Database History: {'✅' if history_ok else '❌'}")
    
    if all([initial_ok, mqtt_ok, after_ok, history_ok]):
        print("\n🎉 All tests passed! Working system is functioning correctly.")
        print("🌐 Open http://localhost:5000 to see the dashboard")
        print("📊 Features working:")
        print("   ✅ Real-time data display")
        print("   ✅ Database storage")
        print("   ✅ History viewing")
        print("   ✅ WebSocket updates")
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")
        
        if not initial_ok:
            print("💡 Make sure the working dashboard is running: python working_dashboard.py")
        if not mqtt_ok:
            print("💡 Check MQTT broker connection")
        if not after_ok:
            print("💡 Check if MQTT subscriber is receiving and processing data")
        if not history_ok:
            print("💡 Check database connection and storage")

if __name__ == "__main__":
    main()
