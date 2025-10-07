#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
import os

app = Flask(__name__)

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'kbz.rew.mybluehost.me'),
    'database': os.environ.get('DB_NAME', 'kbzrewmy_sensor'),
    'user': os.environ.get('DB_USER', 'kbzrewmy_mo_kerma'),
    'password': os.environ.get('DB_PASSWORD', 'Mehrafarid.5435'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'charset': os.environ.get('DB_CHARSET', 'utf8mb4'),
    'autocommit': True
}

def get_db_connection():
    """Get database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def home():
    """Login page for DigitalTwin Sensor Dashboard"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DigitalTwin Sensor Login</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
            .login-container { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
            .login-header { text-align: center; margin-bottom: 30px; }
            .login-header h1 { color: #333; margin: 0; font-size: 2em; }
            .login-header p { color: #666; margin: 10px 0 0 0; }
            .form-group { margin-bottom: 20px; }
            .form-group label { display: block; margin-bottom: 8px; color: #333; font-weight: bold; }
            .form-group input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
            .form-group input:focus { outline: none; border-color: #007bff; }
            .login-btn { width: 100%; background: #007bff; color: white; border: none; padding: 12px; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 10px; }
            .login-btn:hover { background: #0056b3; }
            .error { color: #dc3545; text-align: center; margin-top: 15px; }
            .demo-credentials { background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 20px; font-size: 14px; }
            .demo-credentials h4 { margin: 0 0 10px 0; color: #333; }
            .demo-credentials p { margin: 5px 0; color: #666; }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="login-header">
                <h1>🌡️ DigitalTwin</h1>
                <p>Sensor Data Dashboard</p>
            </div>
            
            <form id="loginForm">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <button type="submit" class="login-btn">Login</button>
                
                <div id="error" class="error" style="display: none;"></div>
            </form>
            
            <div class="demo-credentials">
                <h4>Demo Credentials:</h4>
                <p><strong>Username:</strong> admin</p>
                <p><strong>Password:</strong> sensor123</p>
            </div>
        </div>
        
        <script>
            document.getElementById('loginForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                // Simple authentication (in production, use proper authentication)
                if (username === 'admin' && password === 'sensor123') {
                    // Store authentication status
                    sessionStorage.setItem('authenticated', 'true');
                    // Redirect to dashboard
                    window.location.href = '/dashboard';
                } else {
                    document.getElementById('error').style.display = 'block';
                    document.getElementById('error').textContent = 'Invalid username or password';
                }
            });
        </script>
    </body>
    </html>
    """

@app.route('/dashboard')
def dashboard():
    """Real-time sensor data dashboard"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DigitalTwin Sensor Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1400px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #333; margin: 0; }
            .header p { color: #666; margin: 10px 0; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
            .stat-card h3 { margin: 0 0 10px 0; color: #007bff; }
            .stat-value { font-size: 2em; font-weight: bold; color: #28a745; margin: 10px 0; }
            .rooms-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }
            .solar-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .room-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .room-card h3 { margin: 0 0 15px 0; color: #333; display: flex; justify-content: space-between; align-items: center; }
            .room-id { background: #007bff; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
            .sensor-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #eee; }
            .sensor-item:last-child { border-bottom: none; }
            .sensor-info { display: flex; align-items: center; gap: 10px; }
            .sensor-name { font-weight: bold; }
            .sensor-id { background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; }
            .sensor-value { color: #28a745; font-weight: bold; }
            .loading { text-align: center; color: #666; }
            .error { color: #dc3545; text-align: center; }
            .refresh-btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 10px; }
            .refresh-btn:hover { background: #0056b3; }
            .logout-btn { background: #dc3545; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; }
            .logout-btn:hover { background: #c82333; }
            .api-link { position: fixed; top: 20px; right: 20px; background: #28a745; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none; }
            .api-link:hover { background: #218838; }
            .header-controls { display: flex; justify-content: center; align-items: center; gap: 15px; }
        </style>
    </head>
    <body>
        <a href="/api/docs" class="api-link">📚 API Documentation</a>
        
        <div class="container">
            <div class="header">
                <h1>🌡️ DigitalTwin Sensor Dashboard</h1>
                <p>Real-time sensor data monitoring</p>
                <div class="header-controls">
                    <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>
                    <button class="logout-btn" onclick="logout()">🚪 Logout</button>
                </div>
            </div>
            
            <div class="stats-grid" id="statsGrid">
                <div class="loading">Loading statistics...</div>
            </div>
            
            <div class="rooms-grid" id="roomsGrid">
                <div class="loading">Loading room data...</div>
            </div>
            
            <div class="solar-section" id="solarSection" style="margin-top: 30px;">
                <h2 style="text-align: center; color: #333; margin-bottom: 20px;">☀️ Solar Panels</h2>
                <div class="solar-grid" id="solarGrid">
                    <div class="loading">Loading solar panel data...</div>
                </div>
            </div>
        </div>
        
        <script>
            // Check authentication
            if (!sessionStorage.getItem('authenticated')) {
                window.location.href = '/';
            }
            
            function logout() {
                sessionStorage.removeItem('authenticated');
                window.location.href = '/';
            }
            
            async function loadData() {
                try {
                    // Load statistics
                    const statsResponse = await fetch('/api/stats');
                    const statsData = await statsResponse.json();
                    
                    if (statsData.success) {
                        document.getElementById('statsGrid').innerHTML = `
                            <div class="stat-card">
                                <h3>📊 Total Records</h3>
                                <div class="stat-value">${statsData.stats.total_records}</div>
                            </div>
                            <div class="stat-card">
                                <h3>🌡️ Temperature</h3>
                                <div class="stat-value">${statsData.stats.sensor_counts.temperature || 0}</div>
                            </div>
                            <div class="stat-card">
                                <h3>💧 Humidity</h3>
                                <div class="stat-value">${statsData.stats.sensor_counts.humidity || 0}</div>
                            </div>
                            <div class="stat-card">
                                <h3>🌬️ CO2</h3>
                                <div class="stat-value">${statsData.stats.sensor_counts.co2 || 0}</div>
                            </div>
                            <div class="stat-card">
                                <h3>💡 Light</h3>
                                <div class="stat-value">${statsData.stats.sensor_counts.light || 0}</div>
                            </div>
                            <div class="stat-card">
                                <h3>☀️ Solar</h3>
                                <div class="stat-value">${statsData.stats.sensor_counts.solar || 0}</div>
                            </div>
                        `;
                    }
                    
                    // Load rooms data
                    const roomsResponse = await fetch('/api/rooms');
                    const roomsData = await roomsResponse.json();
                    
                    if (roomsData.success) {
                        let roomsHtml = '';
                        roomsData.rooms.forEach(room => {
                            let sensorsHtml = '';
                            Object.keys(room.sensors).forEach(sensorType => {
                                const sensor = room.sensors[sensorType];
                                let value = '';
                                switch(sensorType) {
                                    case 'temperature':
                                        value = `${sensor.temperature_c}°C`;
                                        break;
                                    case 'humidity':
                                        value = `${sensor.humidity_percent}%`;
                                        break;
                                    case 'co2':
                                        value = `${sensor.co2_ppm} ppm`;
                                        break;
                                    case 'light':
                                        value = sensor.is_on ? `ON (${sensor.power_watts}W)` : 'OFF';
                                        break;
                                    case 'solar':
                                        value = `${sensor.power_watts}W`;
                                        break;
                                }
                                sensorsHtml += `
                                    <div class="sensor-item">
                                        <div class="sensor-info">
                                            <span class="sensor-name">${sensorType.toUpperCase()}</span>
                                            <span class="sensor-id">ID: ${sensor.device_id}</span>
                                        </div>
                                        <span class="sensor-value">${value}</span>
                                    </div>
                                `;
                            });
                            
                            roomsHtml += `
                                <div class="room-card">
                                    <h3>
                                        🏠 ${room.room_id}
                                        <span class="room-id">Room ID: ${room.room_id}</span>
                                    </h3>
                                    ${sensorsHtml}
                                </div>
                            `;
                        });
                        
                        document.getElementById('roomsGrid').innerHTML = roomsHtml || '<div class="error">No room data available</div>';
                        
                        // Display solar panels
                        if (roomsData.solar_panels && roomsData.solar_panels.length > 0) {
                            let solarHtml = '';
                            roomsData.solar_panels.forEach(panel => {
                                solarHtml += `
                                    <div class="room-card">
                                        <h3>
                                            ☀️ Solar Panel
                                            <span class="room-id">ID: ${panel.device_id}</span>
                                        </h3>
                                        <div class="sensor-item">
                                            <div class="sensor-info">
                                                <span class="sensor-name">POWER</span>
                                            </div>
                                            <span class="sensor-value">${panel.power_watts}W</span>
                                        </div>
                                        <div class="sensor-item">
                                            <div class="sensor-info">
                                                <span class="sensor-name">VOLTAGE</span>
                                            </div>
                                            <span class="sensor-value">${panel.voltage_volts}V</span>
                                        </div>
                                        <div class="sensor-item">
                                            <div class="sensor-info">
                                                <span class="sensor-name">CURRENT</span>
                                            </div>
                                            <span class="sensor-value">${panel.current_amps}A</span>
                                        </div>
                                    </div>
                                `;
                            });
                            document.getElementById('solarGrid').innerHTML = solarHtml;
                        } else {
                            document.getElementById('solarGrid').innerHTML = '<div class="error">No solar panel data available</div>';
                        }
                    }
                    
                } catch (error) {
                    document.getElementById('statsGrid').innerHTML = '<div class="error">Error loading data: ' + error.message + '</div>';
                    document.getElementById('roomsGrid').innerHTML = '<div class="error">Error loading data: ' + error.message + '</div>';
                    document.getElementById('solarGrid').innerHTML = '<div class="error">Error loading data: ' + error.message + '</div>';
                }
            }
            
            // Load data on page load
            loadData();
            
            // Auto-refresh every 30 seconds
            setInterval(loadData, 30000);
        </script>
    </body>
    </html>
    """

@app.route('/api/docs')
def api_docs():
    """API documentation page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sensor Data API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
            .endpoint h3 { margin: 0 0 10px 0; color: #007bff; }
            .endpoint a { color: #007bff; text-decoration: none; font-weight: bold; }
            .endpoint a:hover { text-decoration: underline; }
            .description { color: #666; margin: 5px 0; }
            .test-btn { background: #28a745; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
            .test-btn:hover { background: #218838; }
            .dashboard-link { position: fixed; top: 20px; right: 20px; background: #007bff; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none; }
            .dashboard-link:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <a href="/" class="dashboard-link">📊 Dashboard</a>
        
        <div class="container">
            <h1>🌡️ Sensor Data API Documentation</h1>
            <p style="text-align: center; color: #666;">API for retrieving sensor data from database</p>
            
            <div class="endpoint">
                <h3>📊 Statistics</h3>
                <a href="/api/stats" target="_blank">GET /api/stats</a>
                <div class="description">Display overall statistics for all sensors</div>
                <button class="test-btn" onclick="testEndpoint('/api/stats')">Test</button>
            </div>
            
            <div class="endpoint">
                <h3>🌡️ Temperature Data</h3>
                <a href="/api/temperature" target="_blank">GET /api/temperature</a>
                <div class="description">Get latest temperature data</div>
                <button class="test-btn" onclick="testEndpoint('/api/temperature')">Test</button>
            </div>
            
            <div class="endpoint">
                <h3>💧 Humidity Data</h3>
                <a href="/api/humidity" target="_blank">GET /api/humidity</a>
                <div class="description">Get latest humidity data</div>
                <button class="test-btn" onclick="testEndpoint('/api/humidity')">Test</button>
            </div>
            
            <div class="endpoint">
                <h3>🌬️ CO2 Data</h3>
                <a href="/api/co2" target="_blank">GET /api/co2</a>
                <div class="description">Get latest CO2 data</div>
                <button class="test-btn" onclick="testEndpoint('/api/co2')">Test</button>
            </div>
            
            <div class="endpoint">
                <h3>💡 Light Data</h3>
                <a href="/api/light" target="_blank">GET /api/light</a>
                <div class="description">Get latest light data</div>
                <button class="test-btn" onclick="testEndpoint('/api/light')">Test</button>
            </div>
            
            <div class="endpoint">
                <h3>☀️ Solar Data</h3>
                <a href="/api/solar" target="_blank">GET /api/solar</a> - Get all solar panels data (separate from rooms)
                <div class="description">Get latest solar data</div>
                <button class="test-btn" onclick="testEndpoint('/api/solar')">Test</button>
            </div>
            
            <div class="endpoint">
                <h3>🏠 All Rooms Data</h3>
                <a href="/api/rooms" target="_blank">GET /api/rooms</a>
                <div class="description">Get all rooms with their sensor data</div>
                <button class="test-btn" onclick="testEndpoint('/api/rooms')">Test</button>
            </div>
            
            <div class="endpoint">
                <h3>🏠 Specific Room Data</h3>
                <a href="/api/room/room1" target="_blank">GET /api/room/room1</a>
                <div class="description">Get all data for a specific room</div>
                <button class="test-btn" onclick="testEndpoint('/api/room/room1')">Test</button>
            </div>
            
            <div class="endpoint">
                <h3>❤️ System Health</h3>
                <a href="/api/health" target="_blank">GET /api/health</a>
                <div class="description">Check database connection status</div>
                <button class="test-btn" onclick="testEndpoint('/api/health')">Test</button>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background: #e9ecef; border-radius: 5px;">
                <h4>📝 Usage:</h4>
                <ul>
                    <li>Click on any link to see JSON response</li>
                    <li>Use "Test" button to display result on this page</li>
                    <li>You can use <code>?limit=10</code> parameter to limit number of records</li>
                </ul>
            </div>
        </div>
        
        <script>
            function testEndpoint(endpoint) {
                fetch(endpoint)
                    .then(response => response.json())
                    .then(data => {
                        alert('Result: ' + JSON.stringify(data, null, 2));
                    })
                    .catch(error => {
                        alert('Error: ' + error.message);
                    });
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/stats')
def get_stats():
    """Get sensor data statistics"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Get counts from each table
        tables = ['temperature_data', 'humidity_data', 'co2_data', 'light_data', 'solar_data']
        counts = {}
        total = 0
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                counts[table.replace('_data', '')] = count
                total += count
            except Error as e:
                counts[table.replace('_data', '')] = 0
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_records': total,
                'sensor_counts': counts,
                'tables': tables,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/temperature')
def get_temperature():
    """Get temperature data"""
    return get_sensor_data('temperature_data', 'temperature_c', 'temperature')

@app.route('/api/humidity')
def get_humidity():
    """Get humidity data"""
    return get_sensor_data('humidity_data', 'humidity_percent', 'humidity')

@app.route('/api/co2')
def get_co2():
    """Get CO2 data"""
    return get_sensor_data('co2_data', 'co2_ppm', 'co2')

@app.route('/api/light')
def get_light():
    """Get light data"""
    return get_sensor_data('light_data', 'is_on,power_watts', 'light')

@app.route('/api/solar')
def get_solar():
    """Get all solar panels data"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Get all unique solar panel devices
        cursor.execute("SELECT DISTINCT device_id FROM solar_data ORDER BY device_id")
        solar_devices = [row[0] for row in cursor.fetchall()]
        
        # Get limit parameter
        limit = request.args.get('limit', 10, type=int)
        
        solar_panels = []
        for device_id in solar_devices:
            cursor.execute("SELECT device_id, power_watts, voltage_volts, current_amps, timestamp FROM solar_data WHERE device_id = %s ORDER BY timestamp DESC LIMIT %s", (device_id, limit))
            records = cursor.fetchall()
            
            panel_data = []
            for record in records:
                panel_data.append({
                    'device_id': record[0],
                    'power_watts': record[1],
                    'voltage_volts': record[2],
                    'current_amps': record[3],
                    'timestamp': record[4].isoformat()
                })
            
            if panel_data:
                solar_panels.append({
                    'device_id': device_id,
                    'latest_data': panel_data[0],
                    'all_data': panel_data
                })
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'sensor_type': 'solar',
            'total_panels': len(solar_panels),
            'panels': solar_panels,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/rooms')
def get_all_rooms():
    """Get all rooms with their sensor data"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Get all unique rooms (solar_data doesn't have room_id column)
        cursor.execute("SELECT DISTINCT room_id FROM temperature_data UNION SELECT DISTINCT room_id FROM humidity_data UNION SELECT DISTINCT room_id FROM co2_data UNION SELECT DISTINCT room_id FROM light_data WHERE room_id IS NOT NULL")
        rooms = [row[0] for row in cursor.fetchall()]
        
        rooms_data = []
        
        for room_id in rooms:
            room_data = {'room_id': room_id, 'sensors': {}}
            
            # Temperature
            cursor.execute("SELECT device_id, temperature_c, timestamp FROM temperature_data WHERE room_id = %s ORDER BY timestamp DESC LIMIT 1", (room_id,))
            temp_data = cursor.fetchone()
            if temp_data:
                room_data['sensors']['temperature'] = {
                    'device_id': temp_data[0],
                    'temperature_c': temp_data[1],
                    'timestamp': temp_data[2].isoformat()
                }
            
            # Humidity
            cursor.execute("SELECT device_id, humidity_percent, timestamp FROM humidity_data WHERE room_id = %s ORDER BY timestamp DESC LIMIT 1", (room_id,))
            hum_data = cursor.fetchone()
            if hum_data:
                room_data['sensors']['humidity'] = {
                    'device_id': hum_data[0],
                    'humidity_percent': hum_data[1],
                    'timestamp': hum_data[2].isoformat()
                }
            
            # CO2
            cursor.execute("SELECT device_id, co2_ppm, timestamp FROM co2_data WHERE room_id = %s ORDER BY timestamp DESC LIMIT 1", (room_id,))
            co2_data = cursor.fetchone()
            if co2_data:
                room_data['sensors']['co2'] = {
                    'device_id': co2_data[0],
                    'co2_ppm': co2_data[1],
                    'timestamp': co2_data[2].isoformat()
                }
            
            # Light
            cursor.execute("SELECT device_id, is_on, power_watts, timestamp FROM light_data WHERE room_id = %s ORDER BY timestamp DESC LIMIT 1", (room_id,))
            light_data = cursor.fetchone()
            if light_data:
                room_data['sensors']['light'] = {
                    'device_id': light_data[0],
                    'is_on': bool(light_data[1]),
                    'power_watts': light_data[2],
                    'timestamp': light_data[3].isoformat()
                }
            
            # Solar data is not room-specific, so we don't include it in room data
            
            rooms_data.append(room_data)
        
        # Get all solar panels (separate from rooms)
        cursor.execute("SELECT DISTINCT device_id FROM solar_data ORDER BY device_id")
        solar_devices = [row[0] for row in cursor.fetchall()]
        
        solar_panels = []
        for device_id in solar_devices:
            cursor.execute("SELECT device_id, power_watts, voltage_volts, current_amps, timestamp FROM solar_data WHERE device_id = %s ORDER BY timestamp DESC LIMIT 1", (device_id,))
            solar_data = cursor.fetchone()
            if solar_data:
                solar_panels.append({
                    'device_id': solar_data[0],
                    'power_watts': solar_data[1],
                    'voltage_volts': solar_data[2],
                    'current_amps': solar_data[3],
                    'timestamp': solar_data[4].isoformat()
                })
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'total_rooms': len(rooms_data),
            'rooms': rooms_data,
            'solar_panels': solar_panels,
            'total_solar_panels': len(solar_panels),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/room/<room_id>')
def get_room_data(room_id):
    """Get all sensor data for a specific room"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Get latest data from each sensor type for the room
        room_data = {'room_id': room_id}
        
        # Temperature
        cursor.execute("SELECT device_id, temperature_c, timestamp FROM temperature_data WHERE room_id = %s ORDER BY timestamp DESC LIMIT 1", (room_id,))
        temp_data = cursor.fetchone()
        if temp_data:
            room_data['temperature'] = {
                'device_id': temp_data[0],
                'temperature_c': temp_data[1],
                'timestamp': temp_data[2].isoformat()
            }
        
        # Humidity
        cursor.execute("SELECT device_id, humidity_percent, timestamp FROM humidity_data WHERE room_id = %s ORDER BY timestamp DESC LIMIT 1", (room_id,))
        hum_data = cursor.fetchone()
        if hum_data:
            room_data['humidity'] = {
                'device_id': hum_data[0],
                'humidity_percent': hum_data[1],
                'timestamp': hum_data[2].isoformat()
            }
        
        # CO2
        cursor.execute("SELECT device_id, co2_ppm, timestamp FROM co2_data WHERE room_id = %s ORDER BY timestamp DESC LIMIT 1", (room_id,))
        co2_data = cursor.fetchone()
        if co2_data:
            room_data['co2'] = {
                'device_id': co2_data[0],
                'co2_ppm': co2_data[1],
                'timestamp': co2_data[2].isoformat()
            }
        
        # Light
        cursor.execute("SELECT device_id, is_on, power_watts, timestamp FROM light_data WHERE room_id = %s ORDER BY timestamp DESC LIMIT 1", (room_id,))
        light_data = cursor.fetchone()
        if light_data:
            room_data['light'] = {
                'device_id': light_data[0],
                'is_on': bool(light_data[1]),
                'power_watts': light_data[2],
                'timestamp': light_data[3].isoformat()
            }
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'room_id': room_id,
            'data': room_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        connection = get_db_connection()
        if connection:
            connection.close()
            return jsonify({
                'success': True,
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'status': 'unhealthy',
                'database': 'disconnected',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def get_sensor_data(table_name, columns, sensor_type):
    """Generic function to get sensor data"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Get limit parameter
        limit = request.args.get('limit', 10, type=int)
        
        # Build query
        query = f"SELECT device_id, room_id, {columns}, timestamp FROM {table_name} ORDER BY timestamp DESC LIMIT %s"
        cursor.execute(query, (limit,))
        
        records = cursor.fetchall()
        data = []
        
        for record in records:
            record_dict = {
                'device_id': record[0],
                'room_id': record[1],
                'timestamp': record[-1].isoformat()
            }
            
            # Add sensor-specific data
            if sensor_type == 'temperature':
                record_dict['temperature_c'] = record[2]
            elif sensor_type == 'humidity':
                record_dict['humidity_percent'] = record[2]
            elif sensor_type == 'co2':
                record_dict['co2_ppm'] = record[2]
            elif sensor_type == 'light':
                record_dict['is_on'] = bool(record[2])
                record_dict['power_watts'] = record[3]
            elif sensor_type == 'solar':
                record_dict['power_watts'] = record[2]
                record_dict['voltage_volts'] = record[3]
                record_dict['current_amps'] = record[4]
            
            data.append(record_dict)
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'sensor_type': sensor_type,
            'count': len(data),
            'limit': limit,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
