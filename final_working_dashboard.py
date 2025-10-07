#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Working Dashboard - Simple and Reliable
- Saves data to database
- Shows real-time data
- All features working
"""

from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt
import json
import threading
import time
from datetime import datetime
from collections import defaultdict, deque

# Import database manager
from database import db_manager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'final_dashboard_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global data storage
sensor_data = defaultdict(lambda: deque(maxlen=100))
latest_data = {}
connected_devices = set()
db_save_count = 0
db_fail_count = 0

class FinalMQTTSubscriber:
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
            
            # Store data globally (for real-time display)
            sensor_data[device_id].append(data)
            latest_data[device_id] = data
            connected_devices.add(device_id)
            
            # Save to database
            global db_save_count, db_fail_count
            try:
                db_success = db_manager.save_sensor_data(data)
                if db_success:
                    db_save_count += 1
                    data['db_saved'] = True
                    print(f"💾 Saved to DB: {device_id}")
                else:
                    db_fail_count += 1
                    data['db_saved'] = False
                    print(f"❌ DB Save Failed: {device_id}")
            except Exception as e:
                db_fail_count += 1
                data['db_saved'] = False
                print(f"❌ DB Error: {e}")
            
            # Emit to WebSocket clients
            socketio.emit('sensor_data', {
                'device_id': device_id,
                'kind': kind,
                'value': value,
                'unit': unit,
                'timestamp': data['received_at'],
                'db_saved': data['db_saved']
            })
            
            db_status = "✓" if data['db_saved'] else "✗"
            print(f"📨 {device_id}: {kind} = {value} {unit} | DB: {db_status}")
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
    
    def start(self):
        try:
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            print("🚀 Final MQTT Subscriber started")
        except Exception as e:
            print(f"❌ Failed to start MQTT subscriber: {e}")

# Initialize MQTT subscriber
mqtt_subscriber = FinalMQTTSubscriber()

# HTML Template
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>داشبورد سنسورها - Sensor Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .status-item {
            text-align: center;
        }
        .status-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #27ae60;
        }
        .status-label {
            font-size: 0.9em;
            opacity: 0.8;
        }
        .connection-status {
            display: flex;
            align-items: center;
            justify-content: center;
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
        .db-status {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .db-status.success {
            background: #d4edda;
            color: #155724;
        }
        .db-status.error {
            background: #f8d7da;
            color: #721c24;
        }
        .sensor-chart {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .chart-container {
            position: relative;
            height: 300px;
            margin: 20px 0;
        }
        .sensor-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .sensor-card {
            background: white;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .sensor-card:hover {
            transform: translateY(-3px);
        }
        .sensor-icon {
            font-size: 2em;
            text-align: center;
            margin-bottom: 10px;
        }
        .sensor-title {
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }
        .sensor-value-large {
            font-size: 2em;
            font-weight: bold;
            text-align: center;
            margin: 10px 0;
        }
        .temperature { color: #e74c3c; }
        .humidity { color: #3498db; }
        .co2 { color: #f39c12; }
        .light { color: #f1c40f; }
        .solar { color: #e67e22; }
        .room-info {
            background: #ecf0f1;
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
            text-align: center;
            font-size: 0.9em;
            color: #7f8c8d;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin: 2px;
        }
        .status-online { background: #d4edda; color: #155724; }
        .status-offline { background: #f8d7da; color: #721c24; }
        .status-warning { background: #fff3cd; color: #856404; }
        .tabs {
            display: flex;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        .tab {
            flex: 1;
            padding: 15px;
            text-align: center;
            color: white;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        .tab.active {
            background: rgba(255,255,255,0.2);
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌡️ داشبورد سنسورها</h1>
            <p>نمایش اطلاعات دریافتی از سنسورها - Real-time Sensor Data</p>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('realtime')">📊 نمایش زنده</div>
            <div class="tab" onclick="switchTab('charts')">📈 نمودارها</div>
            <div class="tab" onclick="switchTab('history')">📋 تاریخچه</div>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="connection-status">
                    <div class="status-indicator" id="connectionStatus"></div>
                    <span id="connectionText">در حال اتصال...</span>
                </div>
            </div>
            <div class="status-item">
                <div class="status-value" id="deviceCount">0</div>
                <div class="status-label">دستگاه‌های متصل</div>
            </div>
            <div class="status-item">
                <div class="status-value" id="dbSaves">0</div>
                <div class="status-label">ذخیره در دیتابیس</div>
            </div>
            <div class="status-item">
                <div class="status-value" id="dbFails">0</div>
                <div class="status-label">خطاهای دیتابیس</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="refreshData()">🔄 بروزرسانی</button>
            <button class="btn" onclick="testDatabase()">🗄️ تست دیتابیس</button>
            <button class="btn" onclick="clearData()">🗑️ پاک کردن</button>
        </div>
        
        <!-- Real-time Tab -->
        <div id="realtime" class="tab-content active">
            <div class="sensor-grid" id="sensorGrid">
                <div class="no-data">در حال انتظار برای دریافت داده از سنسورها...</div>
            </div>
        </div>
        
        <!-- Charts Tab -->
        <div id="charts" class="tab-content">
            <div class="sensor-chart">
                <h3>📈 نمودار تغییرات دما</h3>
                <div class="chart-container">
                    <canvas id="temperatureChart"></canvas>
                </div>
            </div>
            <div class="sensor-chart">
                <h3>💧 نمودار رطوبت</h3>
                <div class="chart-container">
                    <canvas id="humidityChart"></canvas>
                </div>
            </div>
            <div class="sensor-chart">
                <h3>🌬️ نمودار CO2</h3>
                <div class="chart-container">
                    <canvas id="co2Chart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- History Tab -->
        <div id="history" class="tab-content">
            <div class="sensor-chart">
                <h3>📋 تاریخچه داده‌ها</h3>
                <div id="historyData">
                    <div class="no-data">در حال بارگذاری تاریخچه...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let charts = {};
        let sensorDataHistory = {
            temperature: [],
            humidity: [],
            co2: [],
            light: [],
            solar: []
        };
        
        // Socket events
        socket.on('connect', function() {
            document.getElementById('connectionStatus').classList.add('connected');
            document.getElementById('connectionText').textContent = 'متصل';
        });
        
        socket.on('disconnect', function() {
            document.getElementById('connectionStatus').classList.remove('connected');
            document.getElementById('connectionText').textContent = 'قطع شده';
        });
        
        socket.on('sensor_data', function(data) {
            updateSensorCard(data);
            updateCharts(data);
            updateDeviceCount();
        });
        
        // Tab switching
        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            // Initialize charts if charts tab is selected
            if (tabName === 'charts') {
                initializeCharts();
            } else if (tabName === 'history') {
                loadHistoryData();
            }
        }
        
        // Sensor card management
        function updateSensorCard(data) {
            const sensorGrid = document.getElementById('sensorGrid');
            const deviceId = data.device_id;
            
            // Remove "no data" message if it exists
            const noDataMsg = sensorGrid.querySelector('.no-data');
            if (noDataMsg) {
                noDataMsg.remove();
            }
            
            // Find or create sensor card
            let sensorCard = document.getElementById(`sensor-${deviceId}`);
            if (!sensorCard) {
                sensorCard = createSensorCard(deviceId);
                sensorGrid.appendChild(sensorCard);
            }
            
            // Update card content
            updateSensorCardContent(sensorCard, data);
        }
        
        function createSensorCard(deviceId) {
            const card = document.createElement('div');
            card.className = 'sensor-card';
            card.id = `sensor-${deviceId}`;
            return card;
        }
        
        function updateSensorCardContent(card, data) {
            const kind = data.kind || 'unknown';
            const value = data.value !== null ? data.value : 'N/A';
            const unit = data.unit || '';
            const timestamp = new Date(data.timestamp).toLocaleString('fa-IR');
            const dbStatus = data.db_saved ? 'success' : 'error';
            const dbStatusText = data.db_saved ? 'ذخیره شد' : 'خطا';
            
            // Get sensor icon and color
            const sensorInfo = getSensorInfo(kind);
            
            card.innerHTML = `
                <div class="sensor-icon ${kind}">${sensorInfo.icon}</div>
                <div class="sensor-title">${sensorInfo.title}</div>
                <div class="sensor-value-large ${kind}">${value}</div>
                <div class="sensor-unit">${unit}</div>
                <div class="room-info">
                    <div><strong>دستگاه:</strong> ${data.device_id}</div>
                    <div><strong>نوع:</strong> ${kind}</div>
                    <div><strong>وضعیت:</strong> <span class="db-status ${dbStatus}">${dbStatusText}</span></div>
                </div>
                <div class="timestamp">آخرین بروزرسانی: ${timestamp}</div>
            `;
        }
        
        function getSensorInfo(kind) {
            const sensorMap = {
                'temperature': { icon: '🌡️', title: 'دماسنج' },
                'humidity': { icon: '💧', title: 'رطوبت‌سنج' },
                'co2': { icon: '🌬️', title: 'سنسور CO2' },
                'light': { icon: '💡', title: 'نور' },
                'solar': { icon: '☀️', title: 'انرژی خورشیدی' }
            };
            return sensorMap[kind] || { icon: '📊', title: 'سنسور' };
        }
        
        // Chart management
        function initializeCharts() {
            if (Object.keys(charts).length > 0) return; // Already initialized
            
            const chartConfig = {
                type: 'line',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'زمان'
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: 'مقدار'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    }
                }
            };
            
            // Temperature Chart
            const tempCtx = document.getElementById('temperatureChart').getContext('2d');
            charts.temperature = new Chart(tempCtx, {
                ...chartConfig,
                data: {
                    labels: [],
                    datasets: [{
                        label: 'دما (°C)',
                        data: [],
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        tension: 0.4
                    }]
                }
            });
            
            // Humidity Chart
            const humCtx = document.getElementById('humidityChart').getContext('2d');
            charts.humidity = new Chart(humCtx, {
                ...chartConfig,
                data: {
                    labels: [],
                    datasets: [{
                        label: 'رطوبت (%)',
                        data: [],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4
                    }]
                }
            });
            
            // CO2 Chart
            const co2Ctx = document.getElementById('co2Chart').getContext('2d');
            charts.co2 = new Chart(co2Ctx, {
                ...chartConfig,
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CO2 (ppm)',
                        data: [],
                        borderColor: '#f39c12',
                        backgroundColor: 'rgba(243, 156, 18, 0.1)',
                        tension: 0.4
                    }]
                }
            });
        }
        
        function updateCharts(data) {
            if (!charts[data.kind]) return;
            
            const chart = charts[data.kind];
            const now = new Date().toLocaleTimeString('fa-IR');
            
            // Add new data point
            chart.data.labels.push(now);
            chart.data.datasets[0].data.push(data.value);
            
            // Keep only last 20 data points
            if (chart.data.labels.length > 20) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }
            
            chart.update('none');
        }
        
        // History data
        function loadHistoryData() {
            fetch('/api/history')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        displayHistoryData(data.records);
                    } else {
                        document.getElementById('historyData').innerHTML = 
                            '<div class="no-data">خطا در بارگذاری تاریخچه</div>';
                    }
                })
                .catch(error => {
                    console.error('Error loading history:', error);
                    document.getElementById('historyData').innerHTML = 
                        '<div class="no-data">خطا در بارگذاری تاریخچه</div>';
                });
        }
        
        function displayHistoryData(records) {
            const historyDiv = document.getElementById('historyData');
            if (records.length === 0) {
                historyDiv.innerHTML = '<div class="no-data">هیچ رکوردی یافت نشد</div>';
                return;
            }
            
            let html = '<div class="sensor-grid">';
            records.forEach(record => {
                const sensorInfo = getSensorInfo(record.kind);
                html += `
                    <div class="sensor-card">
                        <div class="sensor-icon ${record.kind}">${sensorInfo.icon}</div>
                        <div class="sensor-title">${sensorInfo.title}</div>
                        <div class="sensor-value-large ${record.kind}">${record.value}</div>
                        <div class="sensor-unit">${record.unit || ''}</div>
                        <div class="room-info">
                            <div><strong>دستگاه:</strong> ${record.device_id}</div>
                            <div><strong>زمان:</strong> ${new Date(record.timestamp).toLocaleString('fa-IR')}</div>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            historyDiv.innerHTML = html;
        }
        
        // Utility functions
        function updateDeviceCount() {
            const sensorCards = document.querySelectorAll('.sensor-card');
            document.getElementById('deviceCount').textContent = sensorCards.length;
        }
        
        function refreshData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateDeviceCount();
                        document.getElementById('dbSaves').textContent = data.db_saves || 0;
                        document.getElementById('dbFails').textContent = data.db_fails || 0;
                        
                        // Update existing cards
                        Object.keys(data.devices).forEach(deviceId => {
                            const deviceData = data.devices[deviceId];
                            updateSensorCard({
                                device_id: deviceId,
                                kind: deviceData.kind,
                                value: deviceData.value,
                                unit: deviceData.unit,
                                timestamp: deviceData.timestamp,
                                db_saved: deviceData.db_saved
                            });
                        });
                    }
                })
                .catch(error => console.error('Error:', error));
        }
        
        function testDatabase() {
            fetch('/api/test-db')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ دیتابیس کار می‌کند!\n' + 
                              `رکوردها: ${data.record_count}\n` +
                              `آخرین: ${data.latest_record}`);
                    } else {
                        alert('❌ مشکل در دیتابیس: ' + data.error);
                    }
                })
                .catch(error => {
                    alert('❌ خطا در تست دیتابیس: ' + error.message);
                });
        }
        
        function clearData() {
            document.getElementById('sensorGrid').innerHTML = 
                '<div class="no-data">داده‌ها پاک شدند. در حال انتظار برای دریافت داده جدید...</div>';
            document.getElementById('deviceCount').textContent = '0';
            
            // Clear charts
            Object.values(charts).forEach(chart => {
                chart.data.labels = [];
                chart.data.datasets[0].data = [];
                chart.update();
            });
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
                'timestamp': data.get('received_at'),
                'db_saved': data.get('db_saved', False)
            }
        
        return jsonify({
            'success': True,
            'devices': devices,
            'count': len(devices),
            'db_saves': db_save_count,
            'db_fails': db_fail_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test-db')
def test_database():
    """Test database connection and get recent records"""
    try:
        records = db_manager.get_recent_data(limit=5)
        record_count = len(records)
        
        latest_record = None
        if records:
            latest = records[0]
            latest_record = f"{latest.device_id} - {latest.kind}: {latest.value} {latest.unit}"
        
        return jsonify({
            'success': True,
            'record_count': record_count,
            'latest_record': latest_record,
            'message': 'Database is working correctly'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history')
def api_history():
    """API endpoint to get historical sensor data"""
    try:
        limit = request.args.get('limit', 50, type=int)
        device_id = request.args.get('device_id')
        kind = request.args.get('kind')
        
        records = db_manager.get_recent_data(device_id=device_id, kind=kind, limit=limit)
        
        # Convert records to JSON-serializable format
        history_data = []
        for record in records:
            history_data.append({
                'id': record.id,
                'device_id': record.device_id,
                'kind': record.kind,
                'room_id': record.room_id,
                'value': record.value,
                'unit': record.unit,
                'power_w': record.power_w,
                'voltage': record.voltage,
                'current': record.current,
                'on_status': record.on_status,
                'timestamp': record.timestamp.isoformat(),
                'raw_data': record.raw_data
            })
        
        return jsonify({
            'success': True,
            'records': history_data,
            'count': len(history_data)
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
    print("🚀 Starting Final Working Dashboard...")
    print("📡 MQTT Broker: test.mosquitto.org:1883")
    print("🗄️ Database: Connected")
    print("🌐 Dashboard: http://localhost:5000")
    print("=" * 60)
    
    # Start MQTT subscriber
    start_mqtt_subscriber()
    
    # Start Flask-SocketIO server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
