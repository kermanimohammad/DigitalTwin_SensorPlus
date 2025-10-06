#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time
import json

def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Connected with result code {rc}")
    if rc == 0:
        print("[MQTT] Connection successful!")
        # Subscribe to test topic
        client.subscribe("building/demo/#")
        print("[MQTT] Subscribed to building/demo/#")
    else:
        print(f"[MQTT] Connection failed with code {rc}")

def on_message(client, userdata, msg):
    print(f"[MQTT] Received: {msg.topic} -> {msg.payload.decode()}")

def on_disconnect(client, userdata, rc):
    print(f"[MQTT] Disconnected with result code {rc}")

def test_mqtt_connection():
    print("Testing MQTT connection...")
    
    # Test different brokers
    brokers = [
        ("broker.hivemq.com", 1883),
        ("mqtt.eclipseprojects.io", 1883),
        ("test.mosquitto.org", 1883)
    ]
    
    for broker, port in brokers:
        print(f"\n--- Testing {broker}:{port} ---")
        
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        
        try:
            print(f"Connecting to {broker}:{port}...")
            client.connect(broker, port, 60)
            client.loop_start()
            
            # Wait for connection
            time.sleep(3)
            
            # Publish a test message
            test_msg = {
                "deviceId": "test-device",
                "kind": "test",
                "roomId": "test-room",
                "ts": int(time.time() * 1000),
                "value": 42.5,
                "unit": "test"
            }
            
            topic = "building/demo/test"
            client.publish(topic, json.dumps(test_msg))
            print(f"Published test message to {topic}")
            
            # Wait a bit more
            time.sleep(2)
            
            client.loop_stop()
            client.disconnect()
            
        except Exception as e:
            print(f"Error connecting to {broker}:{port} - {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    test_mqtt_connection()
