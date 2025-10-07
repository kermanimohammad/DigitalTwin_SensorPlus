#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple MQTT Subscriber for testing
"""

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
from collections import defaultdict, deque

class SimpleMQTTSubscriber:
    def __init__(self, broker="test.mosquitto.org", port=1883):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        self.running = False
        
        # Store received data
        self.received_data = defaultdict(lambda: deque(maxlen=100))
        self.latest_data = {}
        self.device_count = 0
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"✅ Connected to MQTT broker: {self.broker}:{self.port}")
            client.subscribe("building/demo/#")
            print("📡 Subscribed to: building/demo/#")
            self.running = True
        else:
            print(f"❌ Connection failed with code {rc}")
    
    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            data = json.loads(payload)
            
            device_id = data.get('deviceId', 'unknown')
            kind = data.get('kind', 'unknown')
            value = data.get('value', 'N/A')
            unit = data.get('unit', '')
            
            # Store data
            self.received_data[device_id].append(data)
            self.latest_data[device_id] = data
            
            print(f"📨 {device_id}: {kind} = {value} {unit}")
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
    
    def get_statistics(self):
        """Get statistics about received data"""
        return {
            'total_devices': len(self.latest_data),
            'total_messages': sum(len(data) for data in self.received_data.values()),
            'latest_data': dict(self.latest_data)
        }
    
    def start(self):
        """Start the subscriber"""
        try:
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            
            print("🚀 Starting MQTT Subscriber...")
            print("📡 Broker: test.mosquitto.org:1883")
            print("🔄 Listening for messages...")
            print("Press Ctrl+C to stop")
            print("=" * 50)
            
            while self.running:
                time.sleep(1)
                
                # Print statistics every 10 seconds
                if int(time.time()) % 10 == 0:
                    stats = self.get_statistics()
                    print(f"📊 Stats: {stats['total_devices']} devices, {stats['total_messages']} messages")
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping subscriber...")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.client.loop_stop()
            self.client.disconnect()
            print("✅ Subscriber stopped")

if __name__ == "__main__":
    subscriber = SimpleMQTTSubscriber()
    subscriber.start()
