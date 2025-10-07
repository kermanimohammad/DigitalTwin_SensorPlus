#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render.com Dashboard without SocketIO
Simple Flask app with basic real-time simulation
"""

import os
import time
import random
import threading
from datetime import datetime
from flask import Flask, render_template_string, jsonify

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'no-socketio-secret')

# Global storage
latest_data = {}
start_time = time.time()
simulator_running = True

class SimpleSimulator:
    """Simple simulator without SocketIO"""
    
    def __init__(self):
        self.running = False
        self.interval = 5  # 5 seconds
        self.room_count = 5
        self.devices_per_room = 4  # temp, humidity, co2, light
        self.solar_devices = 1
        
    def run(self):
        """Run the simulator"""
        self.running = True
        print(f"[Simple Simulator] Started with {self.room_count} rooms, {self.room_count * self.devices_per_room + self.solar_devices} devices")
        
        while self.running:
            # Generate sensor data for all rooms
            for room_id in range(1, self.room_count + 1):
                room_name = f'room{room_id}'
                
                # Temperature
                temp = round(20 + random.uniform(-5, 5), 1)
                latest_data[f'temp-{room_id}'] = {
                    'device_id': f'temp-{room_id}',
                    'kind': 'temperature',
                    'value': temp,
                    'unit': '°C',
                    'room_id': room_name,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Humidity
                humidity = round(50 + random.uniform(-10, 10), 1)
                latest_data[f'hum-{room_id}'] = {
                    'device_id': f'hum-{room_id}',
                    'kind': 'humidity',
                    'value': humidity,
                    'unit': '%',
                    'room_id': room_name,
                    'timestamp': datetime.now().isoformat()
                }
                
                # CO2
                co2 = round(400 + random.uniform(-50, 50), 0)
                latest_data[f'co2-{room_id}'] = {
                    'device_id': f'co2-{room_id}',
                    'kind': 'co2',
                    'value': co2,
                    'unit': 'ppm',
                    'room_id': room_name,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Light
                light = round(800 + random.uniform(-200, 200), 0)
                latest_data[f'light-{room_id}'] = {
                    'device_id': f'light-{room_id}',
                    'kind': 'light',
                    'value': light,
                    'unit': 'lux',
                    'room_id': room_name,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Solar Panel
            solar_power = round(120 + random.uniform(-20, 20), 1)
            latest_data['solar-plant'] = {
                'device_id': 'solar-plant',
                'kind': 'solar',
                'value': solar_power,
                'unit': 'W',
                'room_id': 'solar-farm',
                'timestamp': datetime.now().isoformat()
            }
            
            total_devices = self.room_count * self.devices_per_room + self.solar_devices
            print(f"[Simulator] Updated data for {total_devices} devices")
            time.sleep(self.interval)
    
    def stop(self):
        self.running = False

# Initialize simulator
simulator = SimpleSimulator()

# HTML Template
NO_SOCKETIO_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>DigitalTwin Sensor Dashboard - All Devices</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .header { text-align: center; color: #333; margin-bottom: 20px; }
        .sensor-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .sensor-card { background: #e8f4f8; padding: 20px; border-radius: 10px; }
        .sensor-title { font-weight: bold; color: #2c3e50; margin-bottom: 10px; }
        .sensor-value { font-size: 2em; color: #27ae60; margin: 10px 0; }
        .sensor-unit { color: #7f8c8d; }
        .status { background: #d4edda; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .controls { text-align: center; margin: 20px 0; }
        .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 0 10px; }
        .btn:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DigitalTwin Sensor Dashboard</h1>
            <p>All 21 devices across 5 rooms + Solar Farm</p>
        </div>
        
        <div class="status">
            <strong>Status:</strong> <span style="color: green;">Running</span><br>
            <strong>Uptime:</strong> <span id="uptime">00:00</span><br>
            <strong>Last Update:</strong> <span id="lastUpdate">Never</span><br>
            <strong>Devices:</strong> <span id="deviceCount">0</span>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="refreshData()">Refresh Data</button>
            <button class="btn" onclick="toggleSimulator()">Toggle Simulator</button>
        </div>
        
        <div class="sensor-grid" id="sensorGrid">
            <div style="text-align: center; color: #666; padding: 40px;">
                Loading sensor data...
            </div>
        </div>
    </div>

    <script>
        var startTime = Date.now();
        var autoRefreshInterval;
        
        function refreshData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateSensorGrid(data.devices);
                        document.getElementById('lastUpdate').textContent = new Date(data.timestamp).toLocaleString();
                        document.getElementById('deviceCount').textContent = Object.keys(data.devices).length;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
        
        function updateSensorGrid(devices) {
            var sensorGrid = document.getElementById('sensorGrid');
            sensorGrid.innerHTML = '';
            
            // Group devices by room_id
            var roomGroups = {};
            Object.keys(devices).forEach(key => {
                var device = devices[key];
                var roomId = device.room_id || 'other';
                if (!roomGroups[roomId]) {
                    roomGroups[roomId] = {};
                }
                roomGroups[roomId][device.kind] = device;
            });
            
            // Create cards for each room
            Object.keys(roomGroups).forEach(roomId => {
                var room = roomGroups[roomId];
                var card = document.createElement('div');
                card.className = 'sensor-card';
                
                var html = '<div class="sensor-title">' + roomId.toUpperCase() + '</div>';
                
                if (room.temperature) {
                    html += '<div>🌡️ Temperature: <span class="sensor-value">' + room.temperature.value + '</span> <span class="sensor-unit">' + room.temperature.unit + '</span></div>';
                }
                
                if (room.humidity) {
                    html += '<div>💧 Humidity: <span class="sensor-value">' + room.humidity.value + '</span> <span class="sensor-unit">' + room.humidity.unit + '</span></div>';
                }
                
                if (room.co2) {
                    html += '<div>🌬️ CO2: <span class="sensor-value">' + room.co2.value + '</span> <span class="sensor-unit">' + room.co2.unit + '</span></div>';
                }
                
                if (room.light) {
                    html += '<div>💡 Light: <span class="sensor-value">' + room.light.value + '</span> <span class="sensor-unit">' + room.light.unit + '</span></div>';
                }
                
                if (room.solar) {
                    html += '<div>☀️ Solar: <span class="sensor-value">' + room.solar.value + '</span> <span class="sensor-unit">' + room.solar.unit + '</span></div>';
                }
                
                // Get latest timestamp
                var latestTimestamp = null;
                Object.keys(room).forEach(sensorType => {
                    if (room[sensorType] && room[sensorType].timestamp) {
                        if (!latestTimestamp || new Date(room[sensorType].timestamp) > new Date(latestTimestamp)) {
                            latestTimestamp = room[sensorType].timestamp;
                        }
                    }
                });
                
                if (latestTimestamp) {
                    html += '<div style="font-size: 0.8em; color: #666; margin-top: 10px;">Last Update: ' + new Date(latestTimestamp).toLocaleString() + '</div>';
                }
                
                card.innerHTML = html;
                sensorGrid.appendChild(card);
            });
        }
        
        function toggleSimulator() {
            fetch('/api/toggle-simulator', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Simulator ' + (data.running ? 'started' : 'stopped'));
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
        
        // Update uptime
        setInterval(function() {
            var uptime = Math.floor((Date.now() - startTime) / 1000);
            var minutes = Math.floor(uptime / 60);
            var seconds = uptime % 60;
            document.getElementById('uptime').textContent = 
                String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
        }, 1000);
        
        // Auto refresh every 5 seconds
        autoRefreshInterval = setInterval(refreshData, 5000);
        
        // Initial load
        refreshData();
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(NO_SOCKETIO_TEMPLATE)

@app.route('/api/data')
def api_data():
    """API endpoint for sensor data"""
    return jsonify({
        'success': True,
        'devices': latest_data,
        'timestamp': datetime.now().isoformat(),
        'uptime': int(time.time() - start_time),
        'simulator_running': simulator.running
    })

@app.route('/api/toggle-simulator', methods=['POST'])
def toggle_simulator():
    """Toggle simulator on/off"""
    global simulator_running
    simulator_running = not simulator_running
    
    if simulator_running and not simulator.running:
        # Start simulator in background thread
        simulator_thread = threading.Thread(target=simulator.run, daemon=True)
        simulator_thread.start()
        print("[API] Simulator started")
    elif not simulator_running and simulator.running:
        simulator.stop()
        print("[API] Simulator stopped")
    
    return jsonify({'success': True, 'running': simulator_running})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'uptime': int(time.time() - start_time),
        'timestamp': datetime.now().isoformat(),
        'simulator_running': simulator.running
    })

def start_simulator():
    """Start the simulator"""
    global start_time
    start_time = time.time()
    
    # Start simulator in background thread
    simulator_thread = threading.Thread(target=simulator.run, daemon=True)
    simulator_thread.start()
    
    print("[System] Simple simulator started")

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Sensor Dashboard (No SocketIO)")
    print("=" * 60)
    
    # Start simulator
    start_simulator()
    
    # Get port from environment
    port = int(os.getenv('PORT', 5000))
    
    print(f"🌐 Dashboard: http://localhost:{port}")
    print(f"🔍 Health Check: http://localhost:{port}/health")
    print("=" * 60)
    
    # Start Flask app
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"Error starting app: {e}")
        raise
