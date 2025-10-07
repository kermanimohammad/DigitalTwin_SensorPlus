#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid MQTT Subscriber
- Saves data to database (for history)
- Provides real-time data access (for live display)
- Combines both database storage and live streaming
"""

import paho.mqtt.client as mqtt
import json
import signal
import sys
import time
from datetime import datetime
from collections import defaultdict, deque
import threading

# Import database manager
from database import db_manager

class HybridMQTTSubscriber:
    def __init__(self, broker="localhost", port=1883, topics=["building/demo/#"], qos=0):
        self.broker = broker
        self.port = port
        self.topics = topics
        self.qos = qos
        
        # MQTT client setup
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        
        # Real-time data storage (in memory)
        self.live_sensor_data = defaultdict(lambda: deque(maxlen=1000))  # Keep last 1000 readings per device
        self.connected_devices = set()
        self.latest_data = {}
        self.device_stats = defaultdict(lambda: {
            'first_seen': None,
            'last_seen': None,
            'message_count': 0,
            'sensor_types': set(),
            'db_save_count': 0,
            'db_fail_count': 0
        })
        
        # Thread safety
        self.data_lock = threading.Lock()
        self.running = False
        
        # Statistics
        self.total_messages_received = 0
        self.total_db_saves = 0
        self.total_db_failures = 0
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker"""
        if rc == 0:
            print(f"[Hybrid MQTT] Connected to {self.broker}:{self.port}")
            for topic in self.topics:
                client.subscribe(topic, qos=self.qos)
                print(f"[Hybrid MQTT] Subscribed to {topic} (QoS: {self.qos})")
        else:
            print(f"[Hybrid MQTT] Connection failed with code {rc}")
    
    def on_message(self, client, userdata, msg):
        """Callback for when a message is received"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            print(f"[Hybrid MQTT] Received: {topic}")
            print(f"[Hybrid MQTT] Payload: {payload}")
            
            # Parse JSON payload
            data = json.loads(payload)
            
            # Add metadata
            data['received_at'] = datetime.now().isoformat()
            data['topic'] = topic
            data['mqtt_timestamp'] = time.time()
            
            device_id = data.get('deviceId', 'unknown')
            kind = data.get('kind', 'unknown')
            
            # Thread-safe data updates
            with self.data_lock:
                # Update real-time data structures
                self.live_sensor_data[device_id].append(data)
                self.latest_data[device_id] = data
                self.connected_devices.add(device_id)
                
                # Update device statistics
                stats = self.device_stats[device_id]
                if not stats['first_seen']:
                    stats['first_seen'] = data['received_at']
                stats['last_seen'] = data['received_at']
                stats['message_count'] += 1
                stats['sensor_types'].add(kind)
                
                # Update global statistics
                self.total_messages_received += 1
            
            # Save to database (for history)
            db_success = self.save_to_database(data)
            
            # Update database statistics
            with self.data_lock:
                if db_success:
                    self.device_stats[device_id]['db_save_count'] += 1
                    self.total_db_saves += 1
                else:
                    self.device_stats[device_id]['db_fail_count'] += 1
                    self.total_db_failures += 1
            
            print(f"[Hybrid MQTT] {device_id}: {kind} = {data.get('value', 'N/A')} {data.get('unit', '')} | DB: {'✓' if db_success else '✗'}")
            
        except json.JSONDecodeError as e:
            print(f"[Hybrid MQTT] Error parsing JSON: {e}")
            print(f"[Hybrid MQTT] Raw payload: {msg.payload}")
        except Exception as e:
            print(f"[Hybrid MQTT] Error processing message: {e}")
    
    def save_to_database(self, data):
        """Save sensor data to database"""
        try:
            # Use the existing database manager
            success = db_manager.save_sensor_data(data)
            return success
        except Exception as e:
            print(f"[Hybrid MQTT] Database save error: {e}")
            return False
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects"""
        if rc != 0:
            print(f"[Hybrid MQTT] Unexpected disconnection (rc={rc})")
        else:
            print("[Hybrid MQTT] Disconnected gracefully")
    
    def on_log(self, client, userdata, level, buf):
        """Callback for MQTT logging"""
        if level == mqtt.MQTT_LOG_ERR:
            print(f"[Hybrid MQTT] Error: {buf}")
        elif level == mqtt.MQTT_LOG_WARNING:
            print(f"[Hybrid MQTT] Warning: {buf}")
    
    def get_live_data(self, device_id=None):
        """Get live sensor data (thread-safe)"""
        with self.data_lock:
            if device_id:
                return {
                    'latest': self.latest_data.get(device_id),
                    'history': list(self.live_sensor_data.get(device_id, [])),
                    'stats': self.device_stats.get(device_id, {})
                }
            else:
                return {
                    'latest_data': dict(self.latest_data),
                    'connected_devices': list(self.connected_devices),
                    'device_stats': dict(self.device_stats),
                    'global_stats': {
                        'total_messages': self.total_messages_received,
                        'total_db_saves': self.total_db_saves,
                        'total_db_failures': self.total_db_failures
                    }
                }
    
    def get_device_list(self):
        """Get list of connected devices (thread-safe)"""
        with self.data_lock:
            return list(self.connected_devices)
    
    def get_latest_data(self):
        """Get latest data for all devices (thread-safe)"""
        with self.data_lock:
            return dict(self.latest_data)
    
    def get_device_history(self, device_id, limit=100):
        """Get historical data for a device (thread-safe)"""
        with self.data_lock:
            history = list(self.live_sensor_data.get(device_id, []))
            return history[-limit:] if limit else history
    
    def get_statistics(self):
        """Get comprehensive statistics (thread-safe)"""
        with self.data_lock:
            now = datetime.now()
            recent_threshold = now.timestamp() - 300  # 5 minutes ago
            
            # Count active devices (received data in last 5 minutes)
            active_devices = 0
            sensor_type_counts = defaultdict(int)
            room_counts = defaultdict(int)
            
            for device_id, data in self.latest_data.items():
                try:
                    last_seen = datetime.fromisoformat(data.get('received_at', ''))
                    if last_seen.timestamp() > recent_threshold:
                        active_devices += 1
                        sensor_type_counts[data.get('kind', 'unknown')] += 1
                        if data.get('roomId'):
                            room_counts[data.get('roomId')] += 1
                except:
                    pass
            
            return {
                'total_devices': len(self.connected_devices),
                'active_devices': active_devices,
                'sensor_type_counts': dict(sensor_type_counts),
                'room_counts': dict(room_counts),
                'device_list': list(self.connected_devices),
                'global_stats': {
                    'total_messages': self.total_messages_received,
                    'total_db_saves': self.total_db_saves,
                    'total_db_failures': self.total_db_failures,
                    'db_success_rate': (self.total_db_saves / max(1, self.total_messages_received)) * 100
                },
                'timestamp': now.isoformat()
            }
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n[Hybrid MQTT] Received signal {signum}, shutting down...")
        self.running = False
        self.client.disconnect()
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.running = True
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            print(f"[Hybrid MQTT] Started hybrid MQTT subscriber")
            print(f"[Hybrid MQTT] Broker: {self.broker}:{self.port}")
            print(f"[Hybrid MQTT] Topics: {self.topics}")
            print(f"[Hybrid MQTT] Database: {'Connected' if db_manager.engine else 'Not connected'}")
        except Exception as e:
            print(f"[Hybrid MQTT] Failed to start: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()
        print("[Hybrid MQTT] Disconnected")

# Global instance for use by other modules
hybrid_subscriber = None

def get_hybrid_subscriber():
    """Get the global hybrid subscriber instance"""
    global hybrid_subscriber
    if hybrid_subscriber is None:
        hybrid_subscriber = HybridMQTTSubscriber()
    return hybrid_subscriber

def main():
    """Main function to run the hybrid MQTT subscriber"""
    global hybrid_subscriber
    
    print("🚀 Starting Hybrid MQTT Subscriber...")
    print("📡 Features: Database storage + Real-time data access")
    print("=" * 60)
    
    # Create hybrid subscriber
    hybrid_subscriber = HybridMQTTSubscriber()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, hybrid_subscriber.signal_handler)
    signal.signal(signal.SIGTERM, hybrid_subscriber.signal_handler)
    
    try:
        # Connect and start listening
        hybrid_subscriber.connect()
        
        # Keep running
        while hybrid_subscriber.running:
            time.sleep(1)
            
            # Print statistics every 30 seconds
            if int(time.time()) % 30 == 0:
                stats = hybrid_subscriber.get_statistics()
                print(f"[Hybrid MQTT] Stats: {stats['total_devices']} devices, "
                      f"{stats['active_devices']} active, "
                      f"{stats['global_stats']['total_messages']} messages, "
                      f"{stats['global_stats']['db_success_rate']:.1f}% DB success rate")
    
    except KeyboardInterrupt:
        print("\n[Hybrid MQTT] Keyboard interrupt received")
    except Exception as e:
        print(f"[Hybrid MQTT] Error: {e}")
    finally:
        hybrid_subscriber.disconnect()
        print("[Hybrid MQTT] Shutdown complete")

if __name__ == "__main__":
    main()
