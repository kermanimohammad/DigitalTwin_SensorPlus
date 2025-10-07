#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Dashboard for MQTT sensor data
"""

from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt
import json
import threading
import time
from datetime import datetime
from collections import defaultdict, deque

app = Flask(__name__)
app.config['SECRET_KEY'] = 'simple_dashboard_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global data storage
sensor_data = defaultdict(lambda: deque(maxlen=100))
latest_data = {}
connected_devices = set()

class SimpleMQTTSubscriber:
    def __init__(self, broker="test.mosquitto.org", port=1883):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        self.running = False
        
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
            
            # Add timestamp
            data['received_at'] = datetime.now().isoformat()
            
            # Store data globally
            sensor_data[device_id].append(data)
            latest_data[device_id] = data
            connected_devices.add(device_id)
            
            # Emit to WebSocket clients
            socketio.emit('sensor_data', {
                'device_id': device_id,
                'kind': kind,
                'value': value,
                'unit': unit,
                'timestamp': data['received_at']
            })
            
            print(f"📨 {device_id}: {kind} = {value} {unit}")
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
    
    def start(self):
        try:
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            print("🚀 MQTT Subscriber started")
        except Exception as e:
            print(f"❌ Failed to start MQTT subscriber: {e}")

# Initialize MQTT subscriber
mqtt_subscriber = SimpleMQTTSubscriber()

# HTML Template
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>داشبورد ساده سنسورها</title>
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
            max-width: 1200px;
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
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
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
            background: white;
            border-radius: 15px;
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
            <h1>🌡️ داشبورد ساده سنسورها</h1>
            <p>نمایش Real-time داده‌های MQTT</p>
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
            <button class="btn" onclick="refreshData()">🔄 بروزرسانی</button>
            <button class="btn" onclick="clearData()">🗑️ پاک کردن</button>
        </div>
        
        <div class="devices-grid" id="devicesGrid">
            <div class="no-data">در حال انتظار برای دریافت داده از سنسورها...</div>
        </div>
    </div>

    <script>
        const socket = io();
        
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
            updateCardContent(deviceCard, data);
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
            const timestamp = new Date(data.timestamp).toLocaleString('fa-IR');
            
            card.innerHTML = `
                <div class="device-header">
                    <div class="device-id">${data.device_id}</div>
                    <div class="device-kind">${kind.toUpperCase()}</div>
                </div>
                <div class="sensor-value">${value}</div>
                <div class="sensor-unit">${unit}</div>
                <div class="timestamp">آخرین بروزرسانی: ${timestamp}</div>
            `;
        }
        
        function updateDeviceCount() {
            const deviceCards = document.querySelectorAll('.device-card');
            document.getElementById('deviceCount').textContent = deviceCards.length;
        }
        
        function refreshData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateDeviceCount();
                        // Update existing cards
                        Object.keys(data.devices).forEach(deviceId => {
                            const deviceData = data.devices[deviceId];
                            updateDeviceCard({
                                device_id: deviceId,
                                kind: deviceData.kind,
                                value: deviceData.value,
                                unit: deviceData.unit,
                                timestamp: deviceData.timestamp
                            });
                        });
                    }
                })
                .catch(error => console.error('Error:', error));
        }
        
        function clearData() {
            document.getElementById('devicesGrid').innerHTML = 
                '<div class="no-data">داده‌ها پاک شدند. در حال انتظار برای دریافت داده جدید...</div>';
            document.getElementById('deviceCount').textContent = '0';
        }
        
        // Load initial data
        refreshData();
        
        // Auto-refresh every 10 seconds
        setInterval(refreshData, 10000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Dashboard page"""
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/data')
def api_data():
    """API endpoint to get current data"""
    try:
        devices = {}
        for device_id, data in latest_data.items():
            devices[device_id] = {
                'kind': data.get('kind'),
                'value': data.get('value'),
                'unit': data.get('unit'),
                'timestamp': data.get('received_at')
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

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

def start_mqtt_subscriber():
    """Start MQTT subscriber in background thread"""
    mqtt_subscriber.start()

if __name__ == '__main__':
    print("🚀 Starting Simple Sensor Dashboard...")
    print("📡 MQTT Broker: test.mosquitto.org:1883")
    print("🌐 Dashboard: http://localhost:5000")
    print("=" * 60)
    
    # Start MQTT subscriber
    start_mqtt_subscriber()
    
    # Start Flask-SocketIO server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
