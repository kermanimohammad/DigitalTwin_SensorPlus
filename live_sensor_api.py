#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live Sensor API - Direct sensor data without database dependency
This API provides real-time sensor data directly from MQTT without storing in database
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import paho.mqtt.client as mqtt
import json
import threading
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque
import signal
import sys

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global storage for live sensor data
live_sensor_data = defaultdict(lambda: deque(maxlen=1000))  # Keep last 1000 readings per device
connected_devices = set()
latest_data = {}
device_stats = defaultdict(lambda: {
    'first_seen': None,
    'last_seen': None,
    'message_count': 0,
    'sensor_types': set()
})

class LiveMQTTSubscriber:
    def __init__(self, broker="localhost", port=1883, topics=["building/demo/#"]):
        self.broker = broker
        self.port = port
        self.topics = topics
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.running = False
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[Live MQTT] Connected to {self.broker}:{self.port}")
            for topic in self.topics:
                client.subscribe(topic)
                print(f"[Live MQTT] Subscribed to {topic}")
        else:
            print(f"[Live MQTT] Connection failed with code {rc}")
    
    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            data = json.loads(payload)
            
            # Add metadata
            data['received_at'] = datetime.now().isoformat()
            data['topic'] = topic
            data['mqtt_timestamp'] = time.time()
            
            device_id = data.get('deviceId', 'unknown')
            kind = data.get('kind', 'unknown')
            
            # Update global data structures
            live_sensor_data[device_id].append(data)
            latest_data[device_id] = data
            connected_devices.add(device_id)
            
            # Update device statistics
            stats = device_stats[device_id]
            if not stats['first_seen']:
                stats['first_seen'] = data['received_at']
            stats['last_seen'] = data['received_at']
            stats['message_count'] += 1
            stats['sensor_types'].add(kind)
            
            print(f"[Live MQTT] {device_id}: {kind} = {data.get('value', 'N/A')} {data.get('unit', '')}")
            
        except Exception as e:
            print(f"[Live MQTT] Error processing message: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        print(f"[Live MQTT] Disconnected (rc={rc})")
    
    def start(self):
        try:
            self.running = True
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            print(f"[Live MQTT] Started live MQTT subscriber")
        except Exception as e:
            print(f"[Live MQTT] Failed to start: {e}")
    
    def stop(self):
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()

# Initialize MQTT subscriber
mqtt_subscriber = LiveMQTTSubscriber()

@app.route('/')
def home():
    """API home page with documentation"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Live Sensor API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
            .endpoint h3 { margin: 0 0 10px 0; color: #007bff; }
            .endpoint a { color: #007bff; text-decoration: none; font-weight: bold; }
            .endpoint a:hover { text-decoration: underline; }
            .description { color: #666; margin: 5px 0; }
            .status { background: #d4edda; color: #155724; padding: 10px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌡️ Live Sensor API</h1>
            <div class="status">
                <strong>Status:</strong> Real-time sensor data streaming (no database dependency)
            </div>
            
            <div class="endpoint">
                <h3>📊 Live Statistics</h3>
                <a href="/api/live/stats" target="_blank">GET /api/live/stats</a>
                <div class="description">Get real-time statistics from live sensor data</div>
            </div>
            
            <div class="endpoint">
                <h3>🔌 Live Devices</h3>
                <a href="/api/live/devices" target="_blank">GET /api/live/devices</a>
                <div class="description">Get all connected devices with their latest data</div>
            </div>
            
            <div class="endpoint">
                <h3>📱 Device Data</h3>
                <a href="/api/live/device/temp-1" target="_blank">GET /api/live/device/{device_id}</a>
                <div class="description">Get live data for a specific device</div>
            </div>
            
            <div class="endpoint">
                <h3>📈 Device History</h3>
                <a href="/api/live/device/temp-1/history?limit=50" target="_blank">GET /api/live/device/{device_id}/history</a>
                <div class="description">Get historical data for a device (last N readings)</div>
            </div>
            
            <div class="endpoint">
                <h3>🏠 Room Data</h3>
                <a href="/api/live/room/room1" target="_blank">GET /api/live/room/{room_id}</a>
                <div class="description">Get all devices in a specific room</div>
            </div>
            
            <div class="endpoint">
                <h3>🌡️ Sensor Type Data</h3>
                <a href="/api/live/sensors/temperature" target="_blank">GET /api/live/sensors/{sensor_type}</a>
                <div class="description">Get all devices of a specific sensor type</div>
            </div>
            
            <div class="endpoint">
                <h3>❤️ Health Check</h3>
                <a href="/api/live/health" target="_blank">GET /api/live/health</a>
                <div class="description">Check API and MQTT connection status</div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/api/live/stats')
def live_stats():
    """Get live statistics from MQTT data"""
    try:
        now = datetime.now()
        recent_threshold = now - timedelta(minutes=5)
        
        # Count active devices (received data in last 5 minutes)
        active_devices = 0
        sensor_type_counts = defaultdict(int)
        room_counts = defaultdict(int)
        
        for device_id, data in latest_data.items():
            try:
                last_seen = datetime.fromisoformat(data.get('received_at', ''))
                if last_seen > recent_threshold:
                    active_devices += 1
                    sensor_type_counts[data.get('kind', 'unknown')] += 1
                    if data.get('roomId'):
                        room_counts[data.get('roomId')] += 1
            except:
                pass
        
        stats = {
            'total_devices': len(connected_devices),
            'active_devices': active_devices,
            'sensor_type_counts': dict(sensor_type_counts),
            'room_counts': dict(room_counts),
            'device_list': list(connected_devices),
            'timestamp': now.isoformat(),
            'data_source': 'live_mqtt'
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/live/devices')
def live_devices():
    """Get all connected devices with their latest data"""
    try:
        devices = {}
        for device_id in connected_devices:
            if device_id in latest_data:
                data = latest_data[device_id]
                stats = device_stats[device_id]
                
                devices[device_id] = {
                    'latest_data': data,
                    'statistics': {
                        'first_seen': stats['first_seen'],
                        'last_seen': stats['last_seen'],
                        'message_count': stats['message_count'],
                        'sensor_types': list(stats['sensor_types'])
                    },
                    'history_count': len(live_sensor_data[device_id])
                }
        
        return jsonify({
            'success': True,
            'devices': devices,
            'count': len(devices),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/live/device/<device_id>')
def live_device_data(device_id):
    """Get latest data for a specific device"""
    try:
        if device_id not in connected_devices:
            return jsonify({
                'success': False,
                'error': f'Device {device_id} not found or not connected'
            }), 404
        
        data = latest_data.get(device_id)
        stats = device_stats[device_id]
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'latest_data': data,
            'statistics': {
                'first_seen': stats['first_seen'],
                'last_seen': stats['last_seen'],
                'message_count': stats['message_count'],
                'sensor_types': list(stats['sensor_types'])
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/live/device/<device_id>/history')
def live_device_history(device_id):
    """Get historical data for a specific device"""
    try:
        if device_id not in connected_devices:
            return jsonify({
                'success': False,
                'error': f'Device {device_id} not found or not connected'
            }), 404
        
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 1000)  # Cap at 1000 records
        
        history = list(live_sensor_data[device_id])[-limit:]
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'history': history,
            'count': len(history),
            'limit': limit,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/live/room/<room_id>')
def live_room_data(room_id):
    """Get all devices in a specific room"""
    try:
        room_devices = {}
        
        for device_id, data in latest_data.items():
            if data.get('roomId') == room_id:
                stats = device_stats[device_id]
                room_devices[device_id] = {
                    'latest_data': data,
                    'statistics': {
                        'first_seen': stats['first_seen'],
                        'last_seen': stats['last_seen'],
                        'message_count': stats['message_count'],
                        'sensor_types': list(stats['sensor_types'])
                    }
                }
        
        return jsonify({
            'success': True,
            'room_id': room_id,
            'devices': room_devices,
            'count': len(room_devices),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/live/sensors/<sensor_type>')
def live_sensor_type_data(sensor_type):
    """Get all devices of a specific sensor type"""
    try:
        type_devices = {}
        
        for device_id, data in latest_data.items():
            if data.get('kind', '').lower() == sensor_type.lower():
                stats = device_stats[device_id]
                type_devices[device_id] = {
                    'latest_data': data,
                    'statistics': {
                        'first_seen': stats['first_seen'],
                        'last_seen': stats['last_seen'],
                        'message_count': stats['message_count'],
                        'sensor_types': list(stats['sensor_types'])
                    }
                }
        
        return jsonify({
            'success': True,
            'sensor_type': sensor_type,
            'devices': type_devices,
            'count': len(type_devices),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/live/health')
def live_health():
    """Health check endpoint"""
    try:
        mqtt_status = "connected" if mqtt_subscriber.running else "disconnected"
        
        health_data = {
            'api_status': 'healthy',
            'mqtt_status': mqtt_status,
            'connected_devices': len(connected_devices),
            'total_messages': sum(stats['message_count'] for stats in device_stats.values()),
            'uptime': 'N/A',  # Could be implemented with start time tracking
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'health': health_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n[Live API] Received signal {signum}, shutting down...")
    mqtt_subscriber.stop()
    sys.exit(0)

def start_mqtt_subscriber():
    """Start MQTT subscriber in background thread"""
    mqtt_subscriber.start()

if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Starting Live Sensor API...")
    print("📡 MQTT Broker: localhost:1883")
    print("🌐 API: http://localhost:5001")
    print("📊 Stats: http://localhost:5001/api/live/stats")
    print("🔌 Devices: http://localhost:5001/api/live/devices")
    
    # Start MQTT subscriber
    start_mqtt_subscriber()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5001, debug=True)
