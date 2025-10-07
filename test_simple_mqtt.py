#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple MQTT test with public broker
"""

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")
        client.subscribe("test/sensors/#")
    else:
        print(f"❌ Connection failed with code {rc}")

def on_message(client, userdata, msg):
    print(f"📨 Received: {msg.topic}")
    print(f"📄 Payload: {msg.payload.decode()}")

def test_mqtt_connection():
    """Test MQTT connection with public broker"""
    print("🧪 Testing MQTT connection...")
    
    # Use public MQTT broker
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # Connect to public broker
        client.connect("test.mosquitto.org", 1883, 60)
        client.loop_start()
        
        # Wait for connection
        time.sleep(2)
        
        # Publish test message
        test_data = {
            "deviceId": "test-device-1",
            "kind": "temperature",
            "value": 25.5,
            "unit": "°C",
            "roomId": "test-room",
            "ts": int(time.time() * 1000)
        }
        
        client.publish("test/sensors/temperature", json.dumps(test_data))
        print("📤 Published test message")
        
        # Wait for messages
        time.sleep(5)
        
        client.loop_stop()
        client.disconnect()
        print("✅ MQTT test completed")
        
    except Exception as e:
        print(f"❌ MQTT test failed: {e}")

if __name__ == "__main__":
    test_mqtt_connection()
