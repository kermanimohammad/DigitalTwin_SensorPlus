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
        
    def run(self):
        """Run the simulator"""
        self.running = True
        print(f"[Simple Simulator] Started")
        
        device_id = 1
        while self.running:
            # Generate sensor data for 5 devices
            for i in range(5):
                device_name = f'device-{i+1}'
                
                # Temperature
                temp = round(20 + random.uniform(-5, 5), 1)
                latest_data[f'{device_name}-temp'] = {
                    'device_id': device_name,
                    'kind': 'temperature',
                    'value': temp,
                    'unit': '°C',
                    'timestamp': datetime.now().isoformat()
                }
                
                # Humidity
                humidity = round(50 + random.uniform(-10, 10), 1)
                latest_data[f'{device_name}-humidity'] = {
                    'device_id': device_name,
                    'kind': 'humidity',
                    'value': humidity,
                    'unit': '%',
                    'timestamp': datetime.now().isoformat()
                }
            
            print(f"[Simulator] Updated data for 5 devices")
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
    <title>Sensor Dashboard (No SocketIO)</title>
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
            <h1>Sensor Dashboard (No SocketIO)</h1>
            <p>Simple Flask app with basic real-time simulation</p>
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
            
            // Group devices by device_id
            var deviceGroups = {};
            Object.keys(devices).forEach(key => {
                var device = devices[key];
                var deviceId = device.device_id;
                if (!deviceGroups[deviceId]) {
                    deviceGroups[deviceId] = {};
                }
                deviceGroups[deviceId][device.kind] = device;
            });
            
            // Create cards for each device
            Object.keys(deviceGroups).forEach(deviceId => {
                var device = deviceGroups[deviceId];
                var card = document.createElement('div');
                card.className = 'sensor-card';
                
                var html = '<div class="sensor-title">' + deviceId + '</div>';
                
                if (device.temperature) {
                    html += '<div>Temperature: <span class="sensor-value">' + device.temperature.value + '</span> <span class="sensor-unit">' + device.temperature.unit + '</span></div>';
                }
                
                if (device.humidity) {
                    html += '<div>Humidity: <span class="sensor-value">' + device.humidity.value + '</span> <span class="sensor-unit">' + device.humidity.unit + '</span></div>';
                }
                
                html += '<div style="font-size: 0.8em; color: #666; margin-top: 10px;">Last Update: ' + new Date(device.temperature?.timestamp || device.humidity?.timestamp).toLocaleString() + '</div>';
                
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
