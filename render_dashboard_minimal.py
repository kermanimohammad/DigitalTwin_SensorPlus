#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal Render.com Dashboard - Ultra Simple Version
No complex features, just basic functionality
"""

import os
import time
import threading
import random
from datetime import datetime
from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO, emit

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'simple-secret-key')

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Global storage
latest_data = {}
message_count = 0
start_time = time.time()

class MinimalSimulator:
    """Minimal simulator for testing"""
    
    def __init__(self):
        self.running = False
        self.interval = 3  # 3 seconds
        
    def run(self):
        """Run the simulator"""
        self.running = True
        print(f"[Minimal Simulator] Started")
        
        device_id = 1
        while self.running:
            # Generate simple data
            temp = round(20 + random.uniform(-5, 5), 1)
            humidity = round(50 + random.uniform(-10, 10), 1)
            
            data = {
                'device_id': f'device-{device_id}',
                'kind': 'temperature',
                'value': temp,
                'unit': '°C',
                'timestamp': datetime.now().isoformat()
            }
            
            # Store data
            latest_data[f'device-{device_id}'] = data
            
            # Emit to WebSocket
            socketio.emit('sensor_data', data)
            
            print(f"[Simulator] Sent: device-{device_id} = {temp}°C")
            
            device_id = (device_id % 5) + 1  # Cycle through 5 devices
            time.sleep(self.interval)
    
    def stop(self):
        self.running = False

# Initialize simulator
simulator = MinimalSimulator()

# Simple HTML Template
SIMPLE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Simple Sensor Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .header { text-align: center; color: #333; margin-bottom: 20px; }
        .sensor-card { background: #e8f4f8; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .status { background: #d4edda; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
        .no-data { text-align: center; color: #666; padding: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Simple Sensor Dashboard</h1>
            <p>Minimal version for testing</p>
        </div>
        
        <div class="status">
            <strong>Status:</strong> <span id="status">Connecting...</span><br>
            <strong>Messages:</strong> <span id="messageCount">0</span><br>
            <strong>Uptime:</strong> <span id="uptime">00:00</span>
        </div>
        
        <div id="sensorGrid">
            <div class="no-data">Waiting for sensor data...</div>
        </div>
    </div>

    <script>
        var socket = io();
        var messageCount = 0;
        var startTime = Date.now();

        socket.on('connect', function() {
            document.getElementById('status').textContent = 'Connected';
            document.getElementById('status').style.color = 'green';
        });
        
        socket.on('disconnect', function() {
            document.getElementById('status').textContent = 'Disconnected';
            document.getElementById('status').style.color = 'red';
        });
        
        socket.on('sensor_data', function(data) {
            messageCount++;
            document.getElementById('messageCount').textContent = messageCount;
            updateSensorCard(data);
        });
        
        function updateSensorCard(data) {
            var sensorGrid = document.getElementById('sensorGrid');
            var deviceId = data.device_id;
            
            // Remove "no data" message
            var noDataMsg = sensorGrid.querySelector('.no-data');
            if (noDataMsg) {
                noDataMsg.remove();
            }
            
            // Find or create sensor card
            var sensorCard = document.getElementById('sensor-' + deviceId);
            if (!sensorCard) {
                sensorCard = document.createElement('div');
                sensorCard.className = 'sensor-card';
                sensorCard.id = 'sensor-' + deviceId;
                sensorGrid.appendChild(sensorCard);
            }
            
            // Update card content
            sensorCard.innerHTML = 
                '<strong>' + data.device_id + '</strong><br>' +
                'Temperature: ' + data.value + ' ' + data.unit + '<br>' +
                'Time: ' + new Date(data.timestamp).toLocaleString();
        }
        
        // Update uptime
        setInterval(function() {
            var uptime = Math.floor((Date.now() - startTime) / 1000);
            var minutes = Math.floor(uptime / 60);
            var seconds = uptime % 60;
            document.getElementById('uptime').textContent = 
                String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
        }, 1000);
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(SIMPLE_TEMPLATE)

@app.route('/api/data')
def api_data():
    """Simple API endpoint"""
    return jsonify({
        'success': True,
        'devices': latest_data,
        'message_count': message_count,
        'uptime': int(time.time() - start_time)
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'uptime': int(time.time() - start_time)})

@socketio.on('connect')
def handle_connect():
    print(f"[WebSocket] Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[WebSocket] Client disconnected")

def start_simulator():
    """Start the simulator"""
    global start_time
    start_time = time.time()
    
    # Start simulator in background thread
    simulator_thread = threading.Thread(target=simulator.run, daemon=True)
    simulator_thread.start()
    
    print("[System] Minimal simulator started")

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting Minimal Dashboard")
    print("=" * 50)
    
    # Start simulator
    start_simulator()
    
    # Get port from environment
    port = int(os.getenv('PORT', 5000))
    
    print(f"🌐 Dashboard: http://localhost:{port}")
    print(f"🔍 Health Check: http://localhost:{port}/health")
    print("=" * 50)
    
    # Start Flask app
    try:
        socketio.run(app, host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"Error starting app: {e}")
        raise
