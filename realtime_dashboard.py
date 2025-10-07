#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time Dashboard with direct sensor data streaming
This dashboard shows live data directly from MQTT sensors without database dependency
"""

from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt
import json
import threading
import time
from datetime import datetime
from collections import defaultdict, deque

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sensor_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global storage for live sensor data
live_sensor_data = defaultdict(lambda: deque(maxlen=100))  # Keep last 100 readings per device
connected_devices = set()
latest_data = {}

class MQTTLiveSubscriber:
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
            print(f"[MQTT Live] Connected to {self.broker}:{self.port}")
            for topic in self.topics:
                client.subscribe(topic)
                print(f"[MQTT Live] Subscribed to {topic}")
        else:
            print(f"[MQTT Live] Connection failed with code {rc}")
    
    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            data = json.loads(payload)
            
            # Add timestamp and topic
            data['received_at'] = datetime.now().isoformat()
            data['topic'] = topic
            
            device_id = data.get('deviceId', 'unknown')
            kind = data.get('kind', 'unknown')
            
            # Store in global data structures
            live_sensor_data[device_id].append(data)
            latest_data[device_id] = data
            connected_devices.add(device_id)
            
            # Emit to all connected WebSocket clients
            socketio.emit('sensor_data', {
                'device_id': device_id,
                'kind': kind,
                'data': data,
                'timestamp': data['received_at']
            })
            
            print(f"[MQTT Live] Received from {device_id}: {kind} = {data.get('value', 'N/A')}")
            
        except Exception as e:
            print(f"[MQTT Live] Error processing message: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        print(f"[MQTT Live] Disconnected (rc={rc})")
    
    def start(self):
        try:
            self.running = True
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            print(f"[MQTT Live] Started MQTT subscriber")
        except Exception as e:
            print(f"[MQTT Live] Failed to start: {e}")
    
    def stop(self):
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()

# Initialize MQTT subscriber
mqtt_subscriber = MQTTLiveSubscriber()

# HTML Template for Real-time Dashboard
REALTIME_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>داشبورد Real-time سنسورها</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            direction: rtl;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .status-bar {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .connection-status {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #e74c3c;
            animation: pulse 2s infinite;
        }
        .status-indicator.connected {
            background: #27ae60;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .devices-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .device-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .device-card:hover {
            transform: translateY(-5px);
        }
        .device-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        .device-id {
            font-weight: bold;
            color: #2c3e50;
            font-size: 1.2em;
        }
        .device-kind {
            background: #3498db;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        .sensor-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #27ae60;
            text-align: center;
            margin: 20px 0;
        }
        .sensor-unit {
            color: #7f8c8d;
            font-size: 1.1em;
            text-align: center;
        }
        .sensor-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }
        .detail-item {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }
        .detail-label {
            font-size: 0.9em;
            color: #7f8c8d;
            margin-bottom: 5px;
        }
        .detail-value {
            font-weight: bold;
            color: #2c3e50;
        }
        .timestamp {
            color: #95a5a6;
            font-size: 0.9em;
            text-align: center;
            margin-top: 15px;
        }
        .no-data {
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            padding: 40px;
        }
        .controls {
            text-align: center;
            margin-bottom: 20px;
        }
        .btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: 2px solid white;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            margin: 0 10px;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background: white;
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌡️ داشبورد Real-time سنسورها</h1>
            <p>نمایش زنده داده‌های سنسورها بدون وابستگی به دیتابیس</p>
        </div>
        
        <div class="status-bar">
            <div class="connection-status">
                <div class="status-indicator" id="connectionStatus"></div>
                <span id="connectionText">در حال اتصال...</span>
            </div>
            <div>
                <span>دستگاه‌های متصل: </span>
                <strong id="deviceCount">0</strong>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="clearData()">🗑️ پاک کردن داده‌ها</button>
            <button class="btn" onclick="toggleAutoRefresh()">🔄 توقف/شروع بروزرسانی</button>
        </div>
        
        <div class="devices-grid" id="devicesGrid">
            <div class="no-data">در حال انتظار برای دریافت داده از سنسورها...</div>
        </div>
    </div>

    <script>
        const socket = io();
        let autoRefresh = true;
        
        socket.on('connect', function() {
            document.getElementById('connectionStatus').classList.add('connected');
            document.getElementById('connectionText').textContent = 'متصل';
        });
        
        socket.on('disconnect', function() {
            document.getElementById('connectionStatus').classList.remove('connected');
            document.getElementById('connectionText').textContent = 'قطع شده';
        });
        
        socket.on('sensor_data', function(data) {
            updateDeviceCard(data);
            updateDeviceCount();
        });
        
        function updateDeviceCard(data) {
            const devicesGrid = document.getElementById('devicesGrid');
            const deviceId = data.device_id;
            const sensorData = data.data;
            
            // Remove "no data" message if it exists
            const noDataMsg = devicesGrid.querySelector('.no-data');
            if (noDataMsg) {
                noDataMsg.remove();
            }
            
            // Find or create device card
            let deviceCard = document.getElementById(`device-${deviceId}`);
            if (!deviceCard) {
                deviceCard = createDeviceCard(deviceId);
                devicesGrid.appendChild(deviceCard);
            }
            
            // Update card content
            updateCardContent(deviceCard, sensorData);
        }
        
        function createDeviceCard(deviceId) {
            const card = document.createElement('div');
            card.className = 'device-card';
            card.id = `device-${deviceId}`;
            return card;
        }
        
        function updateCardContent(card, data) {
            const kind = data.kind || 'unknown';
            const value = data.value !== null ? data.value : 'N/A';
            const unit = data.unit || '';
            const roomId = data.roomId || 'نامشخص';
            const timestamp = new Date(data.received_at).toLocaleString('fa-IR');
            
            card.innerHTML = `
                <div class="device-header">
                    <div class="device-id">${data.deviceId}</div>
                    <div class="device-kind">${kind.toUpperCase()}</div>
                </div>
                <div class="sensor-value">${value}</div>
                <div class="sensor-unit">${unit}</div>
                <div class="sensor-details">
                    <div class="detail-item">
                        <div class="detail-label">اتاق</div>
                        <div class="detail-value">${roomId}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">نوع سنسور</div>
                        <div class="detail-value">${kind}</div>
                    </div>
                    ${data.powerW ? `
                    <div class="detail-item">
                        <div class="detail-label">قدرت</div>
                        <div class="detail-value">${data.powerW}W</div>
                    </div>
                    ` : ''}
                    ${data.voltage ? `
                    <div class="detail-item">
                        <div class="detail-label">ولتاژ</div>
                        <div class="detail-value">${data.voltage}V</div>
                    </div>
                    ` : ''}
                </div>
                <div class="timestamp">آخرین بروزرسانی: ${timestamp}</div>
            `;
        }
        
        function updateDeviceCount() {
            const deviceCards = document.querySelectorAll('.device-card');
            document.getElementById('deviceCount').textContent = deviceCards.length;
        }
        
        function clearData() {
            document.getElementById('devicesGrid').innerHTML = 
                '<div class="no-data">داده‌ها پاک شدند. در حال انتظار برای دریافت داده جدید...</div>';
            document.getElementById('deviceCount').textContent = '0';
        }
        
        function toggleAutoRefresh() {
            autoRefresh = !autoRefresh;
            console.log('Auto refresh:', autoRefresh ? 'ON' : 'OFF');
        }
        
        // Request initial data
        socket.emit('get_latest_data');
    </script>
</body>
</html>
"""

@app.route('/')
def realtime_dashboard():
    """Real-time dashboard page"""
    return render_template_string(REALTIME_DASHBOARD_TEMPLATE)

@app.route('/api/live/stats')
def live_stats():
    """Get live statistics from MQTT data"""
    try:
        stats = {
            'total_devices': len(connected_devices),
            'device_list': list(connected_devices),
            'latest_updates': {},
            'sensor_types': defaultdict(int)
        }
        
        for device_id, data in latest_data.items():
            stats['latest_updates'][device_id] = {
                'kind': data.get('kind'),
                'value': data.get('value'),
                'unit': data.get('unit'),
                'timestamp': data.get('received_at')
            }
            stats['sensor_types'][data.get('kind', 'unknown')] += 1
        
        return jsonify({
            'success': True,
            'stats': dict(stats),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/live/devices')
def live_devices():
    """Get live device data"""
    try:
        devices = {}
        for device_id, data_deque in live_sensor_data.items():
            if data_deque:
                latest = data_deque[-1]
                devices[device_id] = {
                    'latest': latest,
                    'history_count': len(data_deque),
                    'first_seen': data_deque[0].get('received_at'),
                    'last_seen': latest.get('received_at')
                }
        
        return jsonify({
            'success': True,
            'devices': devices,
            'count': len(devices)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@socketio.on('get_latest_data')
def handle_get_latest_data():
    """Send latest data to newly connected client"""
    for device_id, data in latest_data.items():
        emit('sensor_data', {
            'device_id': device_id,
            'kind': data.get('kind'),
            'data': data,
            'timestamp': data.get('received_at')
        })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"[WebSocket] Client connected: {request.sid}")
    emit('status', {'message': 'Connected to real-time sensor stream'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"[WebSocket] Client disconnected: {request.sid}")

def start_mqtt_subscriber():
    """Start MQTT subscriber in background thread"""
    mqtt_subscriber.start()

if __name__ == '__main__':
    print("🚀 Starting Real-time Sensor Dashboard...")
    print("📡 MQTT Broker: localhost:1883")
    print("🌐 Dashboard: http://localhost:5000")
    print("📊 API Stats: http://localhost:5000/api/live/stats")
    print("🔌 WebSocket: ws://localhost:5000/socket.io/")
    
    # Start MQTT subscriber
    start_mqtt_subscriber()
    
    # Start Flask-SocketIO server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
