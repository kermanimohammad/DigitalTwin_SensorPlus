#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete system test
"""

import requests
import time
import json
import paho.mqtt.client as mqtt
from datetime import datetime

def test_dashboard_api():
    """Test dashboard API"""
    print("🧪 Testing Dashboard API...")
    try:
        response = requests.get("http://localhost:5000/api/data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard API: OK - {data['count']} devices")
            return True
        else:
            print(f"❌ Dashboard API: Failed - {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard API: Error - {e}")
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
                {"id": "light-1", "kind": "light", "value": 500.0, "unit": "lux", "room": "room2"}
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
            
            time.sleep(2)
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

def test_dashboard_after_data():
    """Test dashboard after sending data"""
    print("🔄 Testing dashboard after sending data...")
    time.sleep(3)  # Wait for data to be processed
    
    try:
        response = requests.get("http://localhost:5000/api/data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard after data: {data['count']} devices")
            
            if data['count'] > 0:
                print("📊 Device data:")
                for device_id, device_data in data['devices'].items():
                    print(f"   - {device_id}: {device_data['value']} {device_data['unit']}")
                return True
            else:
                print("⚠️ No devices found - data might not be reaching dashboard")
                return False
        else:
            print(f"❌ Dashboard test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard test error: {e}")
        return False

def main():
    """Run complete system test"""
    print("🚀 Complete System Test")
    print("=" * 50)
    
    # Test 1: Dashboard API
    dashboard_ok = test_dashboard_api()
    
    # Test 2: Send MQTT data
    mqtt_ok = send_test_data()
    
    # Test 3: Check dashboard after data
    data_ok = test_dashboard_after_data()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"Dashboard API: {'✅' if dashboard_ok else '❌'}")
    print(f"MQTT Data: {'✅' if mqtt_ok else '❌'}")
    print(f"Data Flow: {'✅' if data_ok else '❌'}")
    
    if dashboard_ok and mqtt_ok and data_ok:
        print("\n🎉 All tests passed! System is working correctly.")
        print("🌐 Open http://localhost:5000 to see the dashboard")
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")
        
        if not dashboard_ok:
            print("💡 Make sure the dashboard is running: python simple_dashboard.py")
        if not mqtt_ok:
            print("💡 Check MQTT broker connection")
        if not data_ok:
            print("💡 Check if MQTT subscriber is receiving data")

if __name__ == "__main__":
    main()
