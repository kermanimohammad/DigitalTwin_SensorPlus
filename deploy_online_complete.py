#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Online Deployment Script
Includes MQTT Broker, Simulator, and Dashboard for online deployment
"""

import os
import sys
import time
import threading
import json
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt
import random

# Configuration for online deployment
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
FLASK_PORT = int(os.getenv('PORT', '5000'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'online_sensor_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global storage
latest_data = {}
connected_devices = set()
message_count = 0
start_time = time.time()

class OnlineMQTTBroker:
    """Simple MQTT Broker simulation for online deployment"""
    
    def __init__(self, port=1883):
        self.port = port
        self.subscribers = {}
        self.running = False
    
    def start(self):
        """Start the broker simulation"""
        self.running = True
        print(f"[Broker] Started on port {self.port}")
    
    def stop(self):
        """Stop the broker"""
        self.running = False
        print("[Broker] Stopped")

class OnlineMQTTSimulator:
    """MQTT Simulator for online deployment"""
    
    def __init__(self, broker_host="localhost", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.running = False
        self.interval = 5  # Send data every 5 seconds
        
        # Simulate multiple rooms with different sensors
        self.rooms = [
            {'id': 'room1', 'temp': 22.0, 'humidity': 45.0, 'co2': 400, 'light': 800},
            {'id': 'room2', 'temp': 23.5, 'humidity': 50.0, 'co2': 420, 'light': 750},
            {'id': 'room3', 'temp': 21.8, 'humidity': 48.0, 'co2': 380, 'light': 900},
            {'id': 'room4', 'temp': 24.2, 'humidity': 52.0, 'co2': 450, 'light': 650},
            {'id': 'room5', 'temp': 22.8, 'humidity': 46.0, 'co2': 410, 'light': 850}
        ]
        
        self.solar_data = {
            'power': 120.0,
            'voltage': 24.0,
            'current': 5.0,
            'on': True
        }
    
    def now_ms(self):
        return int(time.time() * 1000)
    
    def update_sensor_values(self):
        """Update sensor values with realistic variations"""
        for room in self.rooms:
            # Temperature variation
            room['temp'] += random.uniform(-0.5, 0.5)
            room['temp'] = max(18.0, min(28.0, room['temp']))
            
            # Humidity variation
            room['humidity'] += random.uniform(-2.0, 2.0)
            room['humidity'] = max(30.0, min(70.0, room['humidity']))
            
            # CO2 variation
            room['co2'] += random.randint(-10, 10)
            room['co2'] = max(350, min(600, room['co2']))
            
            # Light variation
            room['light'] += random.randint(-50, 50)
            room['light'] = max(200, min(1200, room['light']))
        
        # Solar variation
        self.solar_data['power'] += random.uniform(-5.0, 5.0)
        self.solar_data['power'] = max(80.0, min(150.0, self.solar_data['power']))
        self.solar_data['voltage'] = round(24.0 + random.uniform(-1.0, 1.0), 1)
        self.solar_data['current'] = round(self.solar_data['power'] / self.solar_data['voltage'], 2)
    
    def publish_sensor_data(self, data):
        """Publish sensor data directly to dashboard"""
        global latest_data, connected_devices, message_count
        
        device_id = data['deviceId']
        kind = data['kind']
        value = data['value']
        unit = data['unit']
        timestamp = datetime.fromtimestamp(data['ts'] / 1000)
        
        # Store data
        latest_data[device_id] = {
            'device_id': device_id,
            'kind': kind,
            'value': value,
            'unit': unit,
            'timestamp': timestamp.isoformat(),
            'room_id': data.get('roomId', ''),
            'power_w': data.get('powerW'),
            'voltage': data.get('voltage'),
            'current': data.get('current'),
            'on_status': data.get('on')
        }
        
        connected_devices.add(device_id)
        message_count += 1
        
        # Emit to WebSocket clients
        socketio.emit('sensor_data', {
            'device_id': device_id,
            'kind': kind,
            'value': value,
            'unit': unit,
            'timestamp': timestamp.isoformat()
        })
        
        print(f"[Simulator] Published: {device_id} = {value} {unit}")
    
    def run(self):
        """Run the simulator"""
        self.running = True
        print(f"[Simulator] Started publishing sensor data every {self.interval} seconds")
        
        while self.running:
            self.update_sensor_values()
            
            # Publish all sensor data
            for room in self.rooms:
                # Temperature
                temp_data = {
                    "deviceId": f"temp-{room['id'][-1]}",
                    "kind": "temperature",
                    "value": round(room['temp'], 1),
                    "unit": "°C",
                    "roomId": room['id'],
                    "ts": self.now_ms()
                }
                self.publish_sensor_data(temp_data)
                
                # Humidity
                hum_data = {
                    "deviceId": f"hum-{room['id'][-1]}",
                    "kind": "humidity",
                    "value": round(room['humidity'], 1),
                    "unit": "%",
                    "roomId": room['id'],
                    "ts": self.now_ms()
                }
                self.publish_sensor_data(hum_data)
                
                # CO2
                co2_data = {
                    "deviceId": f"co2-{room['id'][-1]}",
                    "kind": "co2",
                    "value": room['co2'],
                    "unit": "ppm",
                    "roomId": room['id'],
                    "ts": self.now_ms()
                }
                self.publish_sensor_data(co2_data)
                
                # Light
                light_data = {
                    "deviceId": f"light-{room['id'][-1]}",
                    "kind": "light",
                    "value": room['light'],
                    "unit": "lux",
                    "on": True,
                    "powerW": 15.0,
                    "roomId": room['id'],
                    "ts": self.now_ms()
                }
                self.publish_sensor_data(light_data)
            
            # Solar
            solar_data = {
                "deviceId": "solar-plant",
                "kind": "solar",
                "value": self.solar_data['power'],
                "unit": "W",
                "powerW": self.solar_data['power'],
                "voltage": self.solar_data['voltage'],
                "current": self.solar_data['current'],
                "on": self.solar_data['on'],
                "ts": self.now_ms()
            }
            self.publish_sensor_data(solar_data)
            
            time.sleep(self.interval)
    
    def stop(self):
        self.running = False

# Initialize components
broker = OnlineMQTTBroker(MQTT_PORT)
simulator = OnlineMQTTSimulator(MQTT_BROKER, MQTT_PORT)

# Dashboard HTML Template
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DigitalTwin Sensor Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            direction: ltr;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: #ffffff;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .header {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.8em;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        .header p {
            font-size: 1.1em;
            color: #7f8c8d;
        }
        .status-bar {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            color: #2c3e50;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.05);
        }
        .status-item {
            text-align: center;
        }
        .status-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #3498db;
        }
        .status-label {
            font-size: 0.9em;
            opacity: 0.8;
            color: #7f8c8d;
        }
        .connection-status {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .status-indicator {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: #e74c3c;
            animation: pulse 2s infinite;
        }
        .status-indicator.connected {
            background: #27ae60;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.4; }
            100% { opacity: 1; }
        }
        .controls {
            text-align: center;
            margin-bottom: 30px;
        }
        .btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            cursor: pointer;
            margin: 0 8px;
            font-size: 1em;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .btn:hover {
            background: #2980b9;
            transform: translateY(-2px);
        }
        .sensor-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
        }
        .sensor-card {
            background: #fdfdfd;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }
        .sensor-card:hover {
            transform: translateY(-7px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.15);
        }
        .sensor-icon {
            font-size: 3em;
            margin-bottom: 10px;
        }
        .sensor-title {
            font-weight: bold;
            color: #2c3e50;
            font-size: 1.4em;
            margin-bottom: 8px;
        }
        .sensor-value-large {
            font-size: 3em;
            font-weight: bold;
            color: #27ae60;
            margin: 10px 0;
        }
        .sensor-unit {
            color: #7f8c8d;
            font-size: 1.2em;
            margin-bottom: 15px;
        }
        .sensor-details {
            width: 100%;
            background: #ecf0f1;
            padding: 10px 15px;
            border-radius: 10px;
            font-size: 0.9em;
            color: #555;
            margin-top: 15px;
        }
        .sensor-details div {
            margin-bottom: 5px;
        }
        .sensor-details strong {
            color: #333;
        }
        .timestamp {
            color: #95a5a6;
            font-size: 0.85em;
            margin-top: 15px;
        }
        .no-data {
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            padding: 50px;
            background: #f8f9fa;
            border-radius: 15px;
            grid-column: 1 / -1;
        }
        .online-badge {
            background: #27ae60;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DigitalTwin Sensor Dashboard <span class="online-badge">ONLINE</span></h1>
            <p>Real-time sensor data monitoring with built-in simulator</p>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="connection-status">
                    <div class="status-indicator" id="connectionStatus"></div>
                    <span id="connectionText">Connecting...</span>
                </div>
            </div>
            <div class="status-item">
                <div class="status-value" id="deviceCount">0</div>
                <div class="status-label">Connected Devices</div>
            </div>
            <div class="status-item">
                <div class="status-value" id="messageCount">0</div>
                <div class="status-label">Messages Received</div>
            </div>
            <div class="status-item">
                <div class="status-value" id="uptime">00:00</div>
                <div class="status-label">Uptime</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="refreshData()">Refresh Data</button>
            <button class="btn" onclick="clearData()">Clear Display</button>
            <button class="btn" onclick="toggleSimulator()">Toggle Simulator</button>
        </div>
        
        <div class="sensor-grid" id="sensorGrid">
            <div class="no-data">Waiting for sensor data...</div>
        </div>
    </div>

    <script>
        var socket = io();
        var messageCount = 0;
        var startTime = Date.now();
        var simulatorRunning = true;

        // Socket events
        socket.on('connect', function() {
            document.getElementById('connectionStatus').classList.add('connected');
            document.getElementById('connectionText').textContent = 'Connected';
        });
        
        socket.on('disconnect', function() {
            document.getElementById('connectionStatus').classList.remove('connected');
            document.getElementById('connectionText').textContent = 'Disconnected';
        });
        
        socket.on('sensor_data', function(data) {
            messageCount++;
            updateSensorCard(data);
            updateStatus();
        });
        
        // Update status bar
        function updateStatus() {
            var sensorCards = document.querySelectorAll('.sensor-card');
            document.getElementById('deviceCount').textContent = sensorCards.length;
            document.getElementById('messageCount').textContent = messageCount;
            
            var uptime = Math.floor((Date.now() - startTime) / 1000);
            var minutes = Math.floor(uptime / 60);
            var seconds = uptime % 60;
            document.getElementById('uptime').textContent = 
                String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
        }
        
        // Sensor card management
        function updateSensorCard(data) {
            var sensorGrid = document.getElementById('sensorGrid');
            var deviceId = data.device_id;
            
            // Remove "no data" message if it exists
            var noDataMsg = sensorGrid.querySelector('.no-data');
            if (noDataMsg) {
                noDataMsg.remove();
            }
            
            // Find or create sensor card
            var sensorCard = document.getElementById('sensor-' + deviceId);
            if (!sensorCard) {
                sensorCard = createSensorCard(deviceId);
                sensorGrid.appendChild(sensorCard);
            }
            
            // Update card content
            updateSensorCardContent(sensorCard, data);
        }
        
        function createSensorCard(deviceId) {
            var card = document.createElement('div');
            card.className = 'sensor-card';
            card.id = 'sensor-' + deviceId;
            return card;
        }
        
        function updateSensorCardContent(card, data) {
            var kind = data.kind || 'unknown';
            var value = data.value !== null ? data.value : 'N/A';
            var unit = data.unit || '';
            var timestamp = new Date(data.timestamp).toLocaleString('en-US');
            
            // Get sensor icon and title
            var sensorInfo = getSensorInfo(kind);
            
            card.innerHTML = 
                '<div class="sensor-icon">' + sensorInfo.icon + '</div>' +
                '<div class="sensor-title">' + sensorInfo.title + '</div>' +
                '<div class="sensor-value-large">' + value + '</div>' +
                '<div class="sensor-unit">' + unit + '</div>' +
                '<div class="sensor-details">' +
                    '<div><strong>Device ID:</strong> ' + data.device_id + '</div>' +
                    '<div><strong>Sensor Type:</strong> ' + kind + '</div>' +
                    '<div><strong>Status:</strong> <span class="online-badge">ONLINE</span></div>' +
                '</div>' +
                '<div class="timestamp">Last Update: ' + timestamp + '</div>';
        }
        
        function getSensorInfo(kind) {
            var sensorMap = {
                'temperature': { icon: '🌡️', title: 'Temperature' },
                'humidity': { icon: '💧', title: 'Humidity' },
                'co2': { icon: '🌬️', title: 'CO2 Sensor' },
                'light': { icon: '💡', title: 'Light Sensor' },
                'solar': { icon: '☀️', title: 'Solar Panel' }
            };
            return sensorMap[kind] || { icon: '📊', title: 'Sensor' };
        }
        
        // Utility functions
        function refreshData() {
            location.reload();
        }
        
        function clearData() {
            document.getElementById('sensorGrid').innerHTML = 
                '<div class="no-data">Data cleared. Waiting for new sensor data...</div>';
            document.getElementById('deviceCount').textContent = '0';
            messageCount = 0;
            document.getElementById('messageCount').textContent = '0';
        }
        
        function toggleSimulator() {
            simulatorRunning = !simulatorRunning;
            var btn = event.target;
            btn.textContent = simulatorRunning ? 'Stop Simulator' : 'Start Simulator';
            btn.style.background = simulatorRunning ? '#3498db' : '#e74c3c';
            
            // Send toggle command to server
            fetch('/api/toggle-simulator', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({running: simulatorRunning})
            });
        }
        
        // Update status every second
        setInterval(updateStatus, 1000);
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/dashboard')
def dashboard_alt():
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/data')
def api_data():
    """API endpoint to get current sensor data"""
    return jsonify({
        'success': True,
        'devices': latest_data,
        'device_count': len(connected_devices),
        'message_count': message_count,
        'uptime': int(time.time() - start_time),
        'simulator_running': simulator.running
    })

@app.route('/api/toggle-simulator', methods=['POST'])
def toggle_simulator():
    """Toggle simulator on/off"""
    data = request.get_json()
    running = data.get('running', True)
    
    if running and not simulator.running:
        # Start simulator in background thread
        simulator_thread = threading.Thread(target=simulator.run, daemon=True)
        simulator_thread.start()
        print("[API] Simulator started")
    elif not running and simulator.running:
        simulator.stop()
        print("[API] Simulator stopped")
    
    return jsonify({'success': True, 'running': running})

@socketio.on('connect')
def handle_connect():
    print(f"[WebSocket] Client connected")
    emit('status', {'message': 'Connected to online dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[WebSocket] Client disconnected")

def start_components():
    """Start all components"""
    global start_time
    start_time = time.time()
    
    # Start broker
    broker.start()
    
    # Start simulator in background thread
    simulator_thread = threading.Thread(target=simulator.run, daemon=True)
    simulator_thread.start()
    
    print("[System] All components started")

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Complete Online System")
    print("=" * 60)
    print(f"🌐 Dashboard: http://localhost:{FLASK_PORT}")
    print(f"📡 MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print("🎯 Features:")
    print("   - Built-in MQTT Broker")
    print("   - Built-in MQTT Simulator")
    print("   - Real-time Dashboard")
    print("   - WebSocket Updates")
    print("=" * 60)
    
    # Start all components
    start_components()
    
    # Start Flask app
    socketio.run(app, host='0.0.0.0', port=FLASK_PORT, debug=False)
