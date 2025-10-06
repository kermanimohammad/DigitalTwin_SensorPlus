#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import signal
import time
import paho.mqtt.client as mqtt
from database_separate_tables import separate_db_manager

class MQTTSubscriberSeparateTables:
    def __init__(self, broker, port, topics, qos=0):
        self.broker = broker
        self.port = port
        self.topics = topics if isinstance(topics, list) else [topics]
        self.qos = qos
        self.client = mqtt.Client()
        self.running = True
        
        # Setup MQTT callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker"""
        if rc == 0:
            print(f"[MQTT] Connected to {self.broker}:{self.port}")
            # Subscribe to all topics
            for topic in self.topics:
                client.subscribe(topic, qos=self.qos)
                print(f"[MQTT] Subscribed to topic: {topic}")
        else:
            print(f"[MQTT] Connection failed with code {rc}")
    
    def on_message(self, client, userdata, msg):
        """Callback for when a message is received"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            print(f"[MQTT] Received: {topic}")
            print(f"[MQTT] Payload: {payload}")
            
            # Parse JSON payload
            data = json.loads(payload)
            
            # Add topic information to the data
            data['topic'] = topic
            
            # Save to appropriate separate table
            success = separate_db_manager.save_sensor_data(data)
            if success:
                print(f"[MQTT] Data saved successfully for device: {data.get('deviceId', 'unknown')}")
            else:
                print(f"[MQTT] Failed to save data for device: {data.get('deviceId', 'unknown')}")
                
        except json.JSONDecodeError as e:
            print(f"[MQTT] Error parsing JSON: {e}")
            print(f"[MQTT] Raw payload: {msg.payload}")
        except Exception as e:
            print(f"[MQTT] Error processing message: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects"""
        if rc != 0:
            print(f"[MQTT] Unexpected disconnection (rc={rc})")
        else:
            print("[MQTT] Disconnected gracefully")
    
    def on_log(self, client, userdata, level, buf):
        """Callback for MQTT logging"""
        if level == mqtt.MQTT_LOG_ERR:
            print(f"[MQTT] Error: {buf}")
        elif level == mqtt.MQTT_LOG_WARNING:
            print(f"[MQTT] Warning: {buf}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n[MQTT] Received signal {signum}, shutting down...")
        self.running = False
        self.client.disconnect()
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            # Setup authentication if provided
            mqtt_user = os.getenv("MQTT_USER", "")
            mqtt_pass = os.getenv("MQTT_PASS", "")
            if mqtt_user and mqtt_pass:
                self.client.username_pw_set(mqtt_user, mqtt_pass)
                print(f"[MQTT] Using authentication for user: {mqtt_user}")
            
            # Setup SSL for secure connections
            if self.port == 8883:
                self.client.tls_set()
                print("[MQTT] SSL/TLS enabled")
            
            # Connect to broker
            self.client.connect(self.broker, self.port, keepalive=60)
            print(f"[MQTT] Connecting to {self.broker}:{self.port}")
            
        except Exception as e:
            print(f"[MQTT] Error connecting to broker: {e}")
            raise
    
    def run(self):
        """Start the MQTT subscriber"""
        try:
            self.connect()
            self.client.loop_start()
            
            print("[MQTT] Subscriber started with separate tables, waiting for messages...")
            print("[MQTT] Press Ctrl+C to stop")
            
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n[MQTT] Keyboard interrupt received")
        except Exception as e:
            print(f"[MQTT] Error in main loop: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("[MQTT] Cleaning up...")
        self.client.loop_stop()
        self.client.disconnect()
        print("[MQTT] Cleanup completed")

def main():
    """Main function"""
    # Get configuration from environment variables
    broker = os.getenv("BROKER", "test.mosquitto.org")
    port = int(os.getenv("PORT", "1883"))
    topics = os.getenv("TOPICS", "building/demo/#").split(",")
    qos = int(os.getenv("QOS", "0"))
    
    print("=== MQTT Database Subscriber with Separate Tables ===")
    print(f"Broker: {broker}:{port}")
    print(f"Topics: {topics}")
    print(f"QoS: {qos}")
    print("=" * 60)
    
    # Test database connection first
    if not separate_db_manager.test_connection():
        print("Database connection failed, exiting...")
        return
    
    # Create and run subscriber
    subscriber = MQTTSubscriberSeparateTables(broker, port, topics, qos)
    subscriber.run()

if __name__ == "__main__":
    main()
