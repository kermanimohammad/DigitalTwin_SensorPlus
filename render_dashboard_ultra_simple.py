#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra Simple Render.com Dashboard
No health checks, no complex features - just basic Flask app
"""

import os
import time
import random
from datetime import datetime
from flask import Flask, render_template_string, jsonify

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ultra-simple-secret')

# Global storage
latest_data = {}
start_time = time.time()

# Simple HTML Template
ULTRA_SIMPLE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Ultra Simple Dashboard</title>
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
            <h1>Ultra Simple Sensor Dashboard</h1>
            <p>Basic version for testing</p>
        </div>
        
        <div class="status">
            <strong>Status:</strong> <span style="color: green;">Running</span><br>
            <strong>Uptime:</strong> <span id="uptime">00:00</span><br>
            <strong>Last Update:</strong> <span id="lastUpdate">Never</span>
        </div>
        
        <div id="sensorGrid">
            <div class="sensor-card">
                <strong>Temperature Sensor</strong><br>
                Value: <span id="tempValue">--</span> °C<br>
                Time: <span id="tempTime">--</span>
            </div>
            <div class="sensor-card">
                <strong>Humidity Sensor</strong><br>
                Value: <span id="humValue">--</span> %<br>
                Time: <span id="humTime">--</span>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 20px;">
            <button onclick="refreshData()" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">
                Refresh Data
            </button>
        </div>
    </div>

    <script>
        var startTime = Date.now();
        
        function refreshData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('tempValue').textContent = data.temperature.toFixed(1);
                        document.getElementById('tempTime').textContent = new Date(data.timestamp).toLocaleString();
                        document.getElementById('humValue').textContent = data.humidity.toFixed(1);
                        document.getElementById('humTime').textContent = new Date(data.timestamp).toLocaleString();
                        document.getElementById('lastUpdate').textContent = new Date(data.timestamp).toLocaleString();
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
        setInterval(refreshData, 5000);
        
        // Initial load
        refreshData();
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(ULTRA_SIMPLE_TEMPLATE)

@app.route('/api/data')
def api_data():
    """Simple API endpoint"""
    # Generate simple sensor data
    temp = round(20 + random.uniform(-5, 5), 1)
    humidity = round(50 + random.uniform(-10, 10), 1)
    
    return jsonify({
        'success': True,
        'temperature': temp,
        'humidity': humidity,
        'timestamp': datetime.now().isoformat(),
        'uptime': int(time.time() - start_time)
    })

@app.route('/health')
def health():
    """Simple health check"""
    return jsonify({
        'status': 'healthy',
        'uptime': int(time.time() - start_time),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/ping')
def ping():
    """Simple ping endpoint"""
    return "pong"

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting Ultra Simple Dashboard")
    print("=" * 50)
    
    # Get port from environment
    port = int(os.getenv('PORT', 5000))
    
    print(f"🌐 Dashboard: http://localhost:{port}")
    print(f"🔍 Health Check: http://localhost:{port}/health")
    print(f"🏓 Ping: http://localhost:{port}/ping")
    print("=" * 50)
    
    # Start Flask app
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"Error starting app: {e}")
        raise
