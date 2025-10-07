#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple MQTT Simulator for testing
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

class SimpleMQTTSimulator:
    def __init__(self, broker="test.mosquitto.org", port=1883):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        self.running = False
        
        # Test devices
        self.devices = [
            {"id": "temp-1", "kind": "temperature", "room": "room1", "unit": "°C"},
            {"id": "hum-1", "kind": "humidity", "room": "room1", "unit": "%"},
            {"id": "temp-2", "kind": "temperature", "room": "room2", "unit": "°C"},
            {"id": "light-1", "kind": "light", "room": "room1", "unit": "lux"},
            {"id": "co2-1", "kind": "co2", "room": "room2", "unit": "ppm"}
        ]
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"✅ Connected to MQTT broker: {self.broker}:{self.port}")
            self.running = True
        else:
            print(f"❌ Connection failed with code {rc}")
    
    def generate_sensor_data(self, device):
        """Generate realistic sensor data"""
        data = {
            "deviceId": device["id"],
            "kind": device["kind"],
            "roomId": device["room"],
            "unit": device["unit"],
            "ts": int(time.time() * 1000)
        }
        
        # Generate realistic values based on sensor type
        if device["kind"] == "temperature":
            data["value"] = round(random.uniform(18.0, 28.0), 1)
        elif device["kind"] == "humidity":
            data["value"] = round(random.uniform(30.0, 70.0), 1)
        elif device["kind"] == "light":
            data["value"] = round(random.uniform(100.0, 1000.0), 1)
            data["powerW"] = round(random.uniform(5.0, 15.0), 1)
        elif device["kind"] == "co2":
            data["value"] = round(random.uniform(400.0, 800.0), 1)
        
        return data
    
    def publish_data(self):
        """Publish sensor data"""
        for device in self.devices:
            data = self.generate_sensor_data(device)
            topic = f"building/demo/{device['kind']}/{device['id']}"
            
            self.client.publish(topic, json.dumps(data))
            print(f"📤 {device['id']}: {data['value']} {device['unit']}")
    
    def start(self):
        """Start the simulator"""
        try:
            self.client.on_connect = self.on_connect
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            
            print("🚀 Starting MQTT Simulator...")
            print("📡 Broker: test.mosquitto.org:1883")
            print("📊 Devices:", len(self.devices))
            print("🔄 Publishing every 5 seconds...")
            print("Press Ctrl+C to stop")
            print("=" * 50)
            
            while self.running:
                self.publish_data()
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping simulator...")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.client.loop_stop()
            self.client.disconnect()
            print("✅ Simulator stopped")

if __name__ == "__main__":
    simulator = SimpleMQTTSimulator()
    simulator.start()
