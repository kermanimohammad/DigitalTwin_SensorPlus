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
from flask import Flask, render_template_string, jsonify, request, make_response

# Database imports
try:
    from database import DatabaseManager
    DATABASE_AVAILABLE = True
    print("[Database] Database module imported successfully")
except ImportError as e:
    DATABASE_AVAILABLE = False
    print(f"[Database] Database module not available: {e}")
    print("[Database] Running in simulation mode only")
except Exception as e:
    DATABASE_AVAILABLE = False
    print(f"[Database] Unexpected error importing database: {e}")
    print("[Database] Running in simulation mode only")

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'no-socketio-secret')

# Enable CORS for frontend compatibility
from flask_cors import CORS
CORS(app, 
     origins=['*'], 
     methods=['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE'], 
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     supports_credentials=True,
     max_age=3600)

# Additional CORS middleware for better compatibility
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

# Handle preflight OPTIONS requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-Requested-With")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '3600')
        return response

# Global storage
latest_data = {}
start_time = time.time()
simulator_running = True

# Database manager
db_manager = None
if DATABASE_AVAILABLE:
    try:
        print("[Database] Initializing database manager...")
        db_manager = DatabaseManager()
        print("[Database] Database manager initialized successfully")
        
        # Test database connection
        print("[Database] Testing database connection...")
        session = db_manager.get_session()
        session.close()
        print("[Database] Database connection test successful")
        
    except Exception as e:
        print(f"[Database] Failed to initialize database manager: {e}")
        print(f"[Database] Error type: {type(e).__name__}")
        import traceback
        print(f"[Database] Traceback: {traceback.format_exc()}")
        DATABASE_AVAILABLE = False
        db_manager = None

class RealisticSimulator:
    """Realistic simulator with gradual temperature changes"""
    
    def __init__(self):
        self.running = False
        self.interval = 5  # 5 seconds
        self.room_count = 5
        self.devices_per_room = 4  # temp, humidity, co2, light
        self.solar_devices = 1
        
        # Temperature base values for each room
        self.room_base_temps = {
            1: 22.0, 2: 21.5, 3: 23.0, 4: 22.5, 5: 21.0
        }
        
        # Current temperature values
        self.current_temps = self.room_base_temps.copy()
        
        # Major change tracking
        self.major_change_active = {i: False for i in range(1, 6)}
        self.major_change_start_time = {i: None for i in range(1, 6)}
        self.major_change_target = {i: 0 for i in range(1, 6)}
        self.major_change_duration = 300  # 5 minutes = 300 seconds
        
        # Last major change time for each room
        self.last_major_change = {i: datetime.now() for i in range(1, 6)}
        
        print(f"[Realistic Simulator] Initialized with {self.room_count} rooms")
        print(f"[Realistic Simulator] Base temperatures: {self.room_base_temps}")
        
    def get_current_season(self):
        """Determine current season based on month"""
        now = datetime.now()
        month = now.month
        
        if month in [12, 1, 2]:  # Winter
            return 'winter'
        elif month in [3, 4, 5]:  # Spring
            return 'spring'
        elif month in [6, 7, 8]:  # Summer
            return 'summer'
        else:  # Fall
            return 'fall'
    
    def is_major_change_time(self):
        """Check if it's time for major changes (not between 9 PM - 6 AM)"""
        now = datetime.now()
        hour = now.hour
        
        # No major changes between 9 PM (21:00) and 6 AM (06:00)
        if 21 <= hour or hour < 6:
            return False
        return True
    
    def should_trigger_major_change(self, room_id):
        """Check if a major change should be triggered for this room"""
        if not self.is_major_change_time():
            return False
            
        if self.major_change_active[room_id]:
            return False
            
        # Check if enough time has passed since last major change (30 minutes)
        time_since_last = datetime.now() - self.last_major_change[room_id]
        if time_since_last.total_seconds() < 1800:  # 30 minutes
            return False
            
        # 2 times per hour = 50% chance every 30 minutes
        return random.random() < 0.5
    
    def calculate_major_change(self, room_id):
        """Calculate major temperature change based on season"""
        season = self.get_current_season()
        current_temp = self.current_temps[room_id]
        
        # Major change: 5-8 degrees
        change_magnitude = random.uniform(5.0, 8.0)
        
        if season in ['summer', 'spring']:
            # Warmer seasons: opening window increases temperature
            change_direction = random.choice([1, 1, 1, -1])  # 75% increase, 25% decrease
        else:  # winter, fall
            # Colder seasons: opening window decreases temperature
            change_direction = random.choice([-1, -1, -1, 1])  # 75% decrease, 25% increase
        
        target_temp = current_temp + (change_magnitude * change_direction)
        
        # Keep temperature within reasonable bounds (15-30°C)
        target_temp = max(15.0, min(30.0, target_temp))
        
        return target_temp
    
    def update_temperature_gradually(self, room_id):
        """Update temperature gradually during major change"""
        if not self.major_change_active[room_id]:
            return
            
        elapsed = time.time() - self.major_change_start_time[room_id]
        progress = min(elapsed / self.major_change_duration, 1.0)
        
        # Smooth transition using easing function
        eased_progress = progress * progress * (3.0 - 2.0 * progress)  # Smooth step
        
        start_temp = self.room_base_temps[room_id]
        target_temp = self.major_change_target[room_id]
        
        self.current_temps[room_id] = start_temp + (target_temp - start_temp) * eased_progress
        
        # Check if major change is complete
        if progress >= 1.0:
            self.major_change_active[room_id] = False
            self.room_base_temps[room_id] = target_temp
            self.last_major_change[room_id] = datetime.now()
            print(f"[Major Change] Room {room_id} completed: {target_temp:.1f}°C")
    
    def update_temperature_normal(self, room_id):
        """Update temperature with normal fluctuations"""
        if self.major_change_active[room_id]:
            return
            
        # Normal fluctuation: 0-1°C
        fluctuation = random.uniform(-1.0, 1.0)
        new_temp = self.current_temps[room_id] + fluctuation
        
        # Keep within reasonable bounds
        new_temp = max(15.0, min(30.0, new_temp))
        self.current_temps[room_id] = new_temp
        
    def run(self):
        """Run the realistic simulator"""
        self.running = True
        print(f"[Realistic Simulator] Started with realistic temperature changes")
        
        while self.running:
            current_time = datetime.now()
            
            # Generate sensor data for all rooms
            for room_id in range(1, self.room_count + 1):
                room_name = f'room{room_id}'
                
                # Check for major change trigger
                if self.should_trigger_major_change(room_id):
                    target_temp = self.calculate_major_change(room_id)
                    self.major_change_active[room_id] = True
                    self.major_change_start_time[room_id] = time.time()
                    self.major_change_target[room_id] = target_temp
                    
                    season = self.get_current_season()
                    change_type = "increase" if target_temp > self.current_temps[room_id] else "decrease"
                    print(f"[Major Change] Room {room_id} started {change_type} to {target_temp:.1f}°C ({season})")
                
                # Update temperature
                if self.major_change_active[room_id]:
                    self.update_temperature_gradually(room_id)
                else:
                    self.update_temperature_normal(room_id)
                
                # Generate other sensor data with realistic variations
                temp = round(self.current_temps[room_id], 1)
                
                # Humidity: realistic indoor room humidity (30-60%)
                base_humidity = 45 - (temp - 22) * 1.5  # Base humidity around 45%
                humidity = round(base_humidity + random.uniform(-0.6, 0.6), 1)
                humidity = max(30, min(60, humidity))
                
                # CO2: slightly higher when temperature is higher (more activity)
                base_co2 = 400 + (temp - 20) * 10
                co2 = round(base_co2 + random.uniform(-20, 20), 0)
                co2 = max(350, min(600, co2))
                
                # Light: random but realistic
                light = round(800 + random.uniform(-200, 200), 0)
                light = max(100, min(1200, light))
                
                # Store data
                latest_data[f'temp-{room_id}'] = {
                    'device_id': f'temp-{room_id}',
                    'kind': 'temperature',
                    'value': temp,
                    'unit': '°C',
                    'room_id': room_name,
                    'timestamp': current_time.isoformat(),
                    'major_change': self.major_change_active[room_id]
                }
                
                latest_data[f'hum-{room_id}'] = {
                    'device_id': f'hum-{room_id}',
                    'kind': 'humidity',
                    'value': humidity,
                    'unit': '%',
                    'room_id': room_name,
                    'timestamp': current_time.isoformat()
                }
                
                latest_data[f'co2-{room_id}'] = {
                    'device_id': f'co2-{room_id}',
                    'kind': 'co2',
                    'value': co2,
                    'unit': 'ppm',
                    'room_id': room_name,
                    'timestamp': current_time.isoformat()
                }
                
                latest_data[f'light-{room_id}'] = {
                    'device_id': f'light-{room_id}',
                    'kind': 'light',
                    'value': light,
                    'unit': 'lux',
                    'room_id': room_name,
                    'timestamp': current_time.isoformat()
                }
            
            # Solar Panel (independent)
            solar_power = round(120 + random.uniform(-20, 20), 1)
            latest_data['solar-plant'] = {
                'device_id': 'solar-plant',
                'kind': 'solar',
                'value': solar_power,
                'unit': 'W',
                'room_id': 'solar-farm',
                'timestamp': current_time.isoformat()
            }
            
            total_devices = self.room_count * self.devices_per_room + self.solar_devices
            active_major_changes = sum(1 for active in self.major_change_active.values() if active)
            
            if active_major_changes > 0:
                print(f"[Simulator] Updated {total_devices} devices, {active_major_changes} major changes active")
            else:
                print(f"[Simulator] Updated {total_devices} devices (normal mode)")
            
            time.sleep(self.interval)
    
    def stop(self):
        self.running = False

class DatabaseScheduler:
    """Database scheduler to save data every 5 minutes to specific sensor tables"""
    
    def __init__(self):
        self.running = False
        self.interval = 300  # 5 minutes = 300 seconds
        self.save_count = 0
        self.error_count = 0
        
    def run(self):
        """Run the database scheduler"""
        self.running = True
        print(f"[Database Scheduler] Started - saving data every {self.interval} seconds (5 minutes)")
        
        while self.running:
            try:
                if DATABASE_AVAILABLE and db_manager and latest_data:
                    # Save all current sensor data to database
                    saved_devices = 0
                    for key, data in latest_data.items():
                        try:
                            # Prepare data for database with correct field names
                            sensor_data = {
                                'deviceId': data['device_id'],  # Use deviceId (not device_id)
                                'kind': data['kind'],
                                'roomId': data.get('room_id', 'unknown'),  # Use roomId (not room_id)
                                'value': data['value'],
                                'unit': data['unit'],
                                'ts': int(datetime.now().timestamp() * 1000),  # Use timestamp in milliseconds
                                'raw_data': str(data)
                            }
                            
                            # Add specific fields for different sensor types
                            if data['kind'] == 'light':
                                # For light sensors, we need is_on and power_watts
                                sensor_data['on'] = data['value'] > 500  # Assume light is on if > 500 lux
                                sensor_data['powerW'] = data['value'] * 0.1  # Convert lux to watts (approximate)
                            elif data['kind'] == 'solar':
                                # For solar sensors, we need power, voltage, current
                                sensor_data['powerW'] = data['value']
                                sensor_data['voltage'] = 12.0  # Assume 12V system
                                sensor_data['current'] = data['value'] / 12.0  # Calculate current
                            
                            # Save to appropriate table (only specific tables, not sensor_data)
                            success = db_manager.save_sensor_data(sensor_data)
                            if success:
                                saved_devices += 1
                            else:
                                self.error_count += 1
                                
                        except Exception as e:
                            print(f"[Database Scheduler] Error saving {key}: {e}")
                            self.error_count += 1
                    
                    self.save_count += 1
                    print(f"[Database Scheduler] Save #{self.save_count}: {saved_devices} devices saved to specific sensor tables")
                    
                else:
                    print("[Database Scheduler] Database not available, skipping save")
                    
            except Exception as e:
                print(f"[Database Scheduler] Error in save cycle: {e}")
                self.error_count += 1
            
            # Wait for next save cycle
            time.sleep(self.interval)
    
    def stop(self):
        self.running = False
        print(f"[Database Scheduler] Stopped - Total saves: {self.save_count}, Errors: {self.error_count}")

# Initialize simulator and database scheduler
simulator = RealisticSimulator()
db_scheduler = DatabaseScheduler()

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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DigitalTwin Sensor Dashboard</h1>
            <p>All 21 devices across 5 rooms + Solar Farm | Realistic temperature simulation | Auto-save every 5 minutes</p>
        </div>
        
        <div class="status">
            <strong>Status:</strong> <span style="color: green;">Running</span><br>
            <strong>Uptime:</strong> <span id="uptime">00:00</span><br>
            <strong>Last Update:</strong> <span id="lastUpdate">Never</span><br>
            <strong>Devices:</strong> <span id="deviceCount">0</span><br>
            <strong>Database:</strong> <span id="dbStatus">Checking...</span><br>
            <strong>DB Saves:</strong> <span id="dbSaves">0</span> | <strong>DB Errors:</strong> <span id="dbErrors">0</span>
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
        
        
        
        
        // Update uptime
        setInterval(function() {
            var uptime = Math.floor((Date.now() - startTime) / 1000);
            var minutes = Math.floor(uptime / 60);
            var seconds = uptime % 60;
            document.getElementById('uptime').textContent = 
                String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
        }, 1000);
        
        // Auto refresh every 5 seconds
        autoRefreshInterval = setInterval(function() {
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
            
            // Update database status
            fetch('/api/database-status')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('dbStatus').textContent = 'Connected';
                        document.getElementById('dbStatus').style.color = 'green';
                        document.getElementById('dbSaves').textContent = data.total_saves;
                        document.getElementById('dbErrors').textContent = data.total_errors;
                    } else {
                        document.getElementById('dbStatus').textContent = 'Not Available';
                        document.getElementById('dbStatus').style.color = 'red';
                        document.getElementById('dbSaves').textContent = '0';
                        document.getElementById('dbErrors').textContent = '0';
                    }
                })
                .catch(error => {
                    document.getElementById('dbStatus').textContent = 'Error';
                    document.getElementById('dbStatus').style.color = 'red';
                    console.error('Database status error:', error);
                });
        }, 5000);
        
        // Initial load
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
        
        // Initial database status
        fetch('/api/database-status')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('dbStatus').textContent = 'Connected';
                    document.getElementById('dbStatus').style.color = 'green';
                    document.getElementById('dbSaves').textContent = data.total_saves;
                    document.getElementById('dbErrors').textContent = data.total_errors;
                } else {
                    document.getElementById('dbStatus').textContent = 'Not Available';
                    document.getElementById('dbStatus').style.color = 'red';
                    document.getElementById('dbSaves').textContent = '0';
                    document.getElementById('dbErrors').textContent = '0';
                }
            })
            .catch(error => {
                document.getElementById('dbStatus').textContent = 'Error';
                document.getElementById('dbStatus').style.color = 'red';
                console.error('Database status error:', error);
            });
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

@app.route('/api/proxy/data')
def api_proxy_data():
    """Proxy endpoint for frontend compatibility"""
    return jsonify({
        'success': True,
        'devices': latest_data,
        'total_devices': len(latest_data),
        'timestamp': datetime.now().isoformat(),
        'uptime': int(time.time() - start_time),
        'simulator_running': simulator.running,
        'db_saves': db_scheduler.save_count if 'db_scheduler' in globals() else 0,
        'db_fails': db_scheduler.error_count if 'db_scheduler' in globals() else 0
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
        'simulator_running': simulator.running,
        'database_available': DATABASE_AVAILABLE,
        'db_saves': db_scheduler.save_count if 'db_scheduler' in globals() else 0,
        'db_errors': db_scheduler.error_count if 'db_scheduler' in globals() else 0
    })

@app.route('/api/health')
def api_health():
    """API health check endpoint for frontend"""
    return jsonify({
        'status': 'ok',
        'database': 'connected' if DATABASE_AVAILABLE else 'disconnected',
        'timestamp': datetime.now().isoformat(),
        'uptime': int(time.time() - start_time),
        'simulator_running': simulator.running,
        'total_devices': len(latest_data)
    })

@app.route('/api/database-status')
def database_status():
    """Get database status and statistics"""
    if not DATABASE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Database not available - module import failed',
            'database_available': False,
            'db_manager': None
        })
    
    if not db_manager:
        return jsonify({
            'success': False,
            'error': 'Database manager not initialized',
            'database_available': True,
            'db_manager': None
        })
    
    try:
        # Get database statistics
        stats = db_manager.get_table_statistics()
        return jsonify({
            'success': True,
            'database_available': True,
            'db_manager': 'Available',
            'scheduler_running': db_scheduler.running if 'db_scheduler' in globals() else False,
            'total_saves': db_scheduler.save_count if 'db_scheduler' in globals() else 0,
            'total_errors': db_scheduler.error_count if 'db_scheduler' in globals() else 0,
            'table_statistics': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'database_available': True,
            'db_manager': 'Available but error occurred'
        })

@app.route('/api/debug-database')
def debug_database():
    """Debug database connection"""
    debug_info = {
        'timestamp': datetime.now().isoformat(),
        'database_available': DATABASE_AVAILABLE,
        'db_manager_available': db_manager is not None,
        'environment_vars': {
            'DB_HOST': os.getenv('DB_HOST', 'NOT_SET'),
            'DB_NAME': os.getenv('DB_NAME', 'NOT_SET'),
            'DB_USER': os.getenv('DB_USER', 'NOT_SET'),
            'DB_PASSWORD': 'SET' if os.getenv('DB_PASSWORD') else 'NOT_SET',
            'DB_PORT': os.getenv('DB_PORT', 'NOT_SET')
        }
    }
    
    if DATABASE_AVAILABLE and db_manager:
        try:
            # Test connection
            session = db_manager.get_session()
            session.close()
            debug_info['connection_test'] = 'SUCCESS'
            
            # Get stats
            stats = db_manager.get_table_statistics()
            debug_info['table_statistics'] = stats
            
        except Exception as e:
            debug_info['connection_test'] = f'FAILED: {str(e)}'
            debug_info['error_type'] = type(e).__name__
    
    return jsonify(debug_info)

@app.route('/api/devices')
def api_devices():
    """Get list of all available devices"""
    devices = []
    for device_id, device_data in latest_data.items():
        devices.append({
            'device_id': device_id,
            'kind': device_data.get('kind'),
            'room_id': device_data.get('room_id'),
            'last_seen': device_data.get('timestamp')
        })
    
    return jsonify({
        'success': True,
        'devices': devices,
        'total_count': len(devices),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/devices/<device_id>')
def api_device_detail(device_id):
    """Get detailed information for a specific device"""
    if device_id in latest_data:
        device_data = latest_data[device_id]
        return jsonify({
            'success': True,
            'device': device_data,
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Device not found',
            'device_id': device_id
        }), 404

@app.route('/api/history/<sensor_type>/<device_id>')
def api_sensor_history(sensor_type, device_id):
    """Get historical data for a specific sensor"""
    if not DATABASE_AVAILABLE or not db_manager:
        return jsonify({
            'success': False,
            'error': 'Database not available'
        }), 503
    
    try:
        # Get hours parameter (default 24)
        hours = int(request.args.get('hours', 24))
        
        # Get historical data from database
        history_data = db_manager.get_recent_data(device_id=device_id, kind=sensor_type, limit=1000)
        
        # Format data for frontend
        formatted_data = []
        for record in history_data:
            if hasattr(record, 'timestamp'):
                formatted_data.append({
                    'timestamp': record.timestamp.isoformat(),
                    'value': getattr(record, f'{sensor_type}_c', None) or 
                            getattr(record, f'{sensor_type}_percent', None) or
                            getattr(record, f'{sensor_type}_ppm', None) or
                            getattr(record, 'power_watts', None) or
                            getattr(record, 'value', None),
                    'device_id': record.device_id,
                    'room_id': getattr(record, 'room_id', None)
                })
        
        return jsonify({
            'success': True,
            'data': formatted_data,
            'count': len(formatted_data),
            'sensor_type': sensor_type,
            'device_id': device_id,
            'hours': hours
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Database query failed: {str(e)}'
        }), 500

def start_simulator():
    """Start the simulator and database scheduler"""
    global start_time
    start_time = time.time()
    
    # Start simulator in background thread
    simulator_thread = threading.Thread(target=simulator.run, daemon=True)
    simulator_thread.start()
    print("[System] Realistic simulator started")
    
    # Start database scheduler in background thread
    if DATABASE_AVAILABLE:
        db_scheduler_thread = threading.Thread(target=db_scheduler.run, daemon=True)
        db_scheduler_thread.start()
        print("[System] Database scheduler started - saving data every 5 minutes to specific tables")
    else:
        print("[System] Database scheduler not started - database not available")

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
