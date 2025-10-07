#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid Dashboard - Real-time display with database history
- Shows live data from MQTT sensors
- Stores data in database for history
- Combines real-time updates with historical analysis
"""

from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit
from database import db_manager
from mqtt_subscriber_hybrid import get_hybrid_subscriber
import json
import threading
import time
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hybrid_sensor_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Get hybrid subscriber instance
hybrid_subscriber = get_hybrid_subscriber()

# HTML Template for Hybrid Dashboard
HYBRID_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>داشبورد ترکیبی سنسورها - Hybrid Sensor Dashboard</title>
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
            border: none;
            background: transparent;
            font-size: 1em;
        }
        .tab.active {
            background: rgba(255,255,255,0.2);
        }
        .tab:hover {
            background: rgba(255,255,255,0.15);
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
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
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .history-table {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow-x: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: right;
            border-bottom: 1px solid #eee;
        }
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f8f9fa;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌡️ داشبورد ترکیبی سنسورها</h1>
            <p>نمایش Real-time + ذخیره در دیتابیس برای تاریخچه</p>
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
                <div class="status-value" id="activeDevices">0</div>
                <div class="status-label">دستگاه‌های فعال</div>
            </div>
            <div class="status-item">
                <div class="status-value" id="dbSuccessRate">0%</div>
                <div class="status-label">نرخ موفقیت دیتابیس</div>
            </div>
            <div class="status-item">
                <div class="status-value" id="totalMessages">0</div>
                <div class="status-label">کل پیام‌ها</div>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('live')">📡 Live Data</button>
            <button class="tab" onclick="switchTab('history')">📊 History</button>
            <button class="tab" onclick="switchTab('analytics')">📈 Analytics</button>
        </div>
        
        <div class="tab-content active" id="live-tab">
            <div class="controls">
                <button class="btn" onclick="refreshLiveData()">🔄 بروزرسانی</button>
                <button class="btn" onclick="clearLiveData()">🗑️ پاک کردن</button>
            </div>
            
            <div class="devices-grid" id="devicesGrid">
                <div class="no-data">در حال انتظار برای دریافت داده از سنسورها...</div>
            </div>
        </div>
        
        <div class="tab-content" id="history-tab">
            <div class="controls">
                <button class="btn" onclick="loadHistory()">📚 بارگذاری تاریخچه</button>
                <button class="btn" onclick="exportHistory()">💾 صادرات</button>
            </div>
            
            <div class="history-table">
                <h3>تاریخچه داده‌ها از دیتابیس</h3>
                <table id="historyTable">
                    <thead>
                        <tr>
                            <th>دستگاه</th>
                            <th>نوع</th>
                            <th>اتاق</th>
                            <th>مقدار</th>
                            <th>واحد</th>
                            <th>زمان</th>
                        </tr>
                    </thead>
                    <tbody id="historyTableBody">
                        <tr>
                            <td colspan="6" style="text-align: center; padding: 20px;">
                                روی "بارگذاری تاریخچه" کلیک کنید
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="tab-content" id="analytics-tab">
            <div class="chart-container">
                <h3>آمار دستگاه‌ها</h3>
                <canvas id="deviceChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-container">
                <h3>توزیع انواع سنسور</h3>
                <canvas id="sensorChart" width="400" height="200"></canvas>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let deviceChart = null;
        let sensorChart = null;
        
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
            updateStatusBar();
        });
        
        socket.on('status_update', function(data) {
            updateStatusBar(data);
        });
        
        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
            
            // Load tab-specific data
            if (tabName === 'analytics') {
                loadAnalytics();
            }
        }
        
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
            const dbStatus = data.db_saved ? 'success' : 'error';
            const dbStatusText = data.db_saved ? 'ذخیره شد' : 'خطا';
            
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
                    <div class="detail-item">
                        <div class="detail-label">وضعیت دیتابیس</div>
                        <div class="detail-value">
                            <span class="db-status ${dbStatus}">${dbStatusText}</span>
                        </div>
                    </div>
                    ${data.powerW ? `
                    <div class="detail-item">
                        <div class="detail-label">قدرت</div>
                        <div class="detail-value">${data.powerW}W</div>
                    </div>
                    ` : ''}
                </div>
                <div class="timestamp">آخرین بروزرسانی: ${timestamp}</div>
            `;
        }
        
        function updateStatusBar(data) {
            if (data) {
                document.getElementById('deviceCount').textContent = data.total_devices || 0;
                document.getElementById('activeDevices').textContent = data.active_devices || 0;
                document.getElementById('dbSuccessRate').textContent = 
                    (data.global_stats?.db_success_rate || 0).toFixed(1) + '%';
                document.getElementById('totalMessages').textContent = data.global_stats?.total_messages || 0;
            }
        }
        
        function refreshLiveData() {
            fetch('/api/hybrid/live')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateStatusBar(data.stats);
                        // Update device cards
                        Object.keys(data.devices).forEach(deviceId => {
                            const deviceData = data.devices[deviceId];
                            updateDeviceCard({
                                device_id: deviceId,
                                data: deviceData.latest_data
                            });
                        });
                    }
                })
                .catch(error => console.error('Error:', error));
        }
        
        function clearLiveData() {
            document.getElementById('devicesGrid').innerHTML = 
                '<div class="no-data">داده‌ها پاک شدند. در حال انتظار برای دریافت داده جدید...</div>';
        }
        
        function loadHistory() {
            fetch('/api/hybrid/history?limit=50')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateHistoryTable(data.records);
                    }
                })
                .catch(error => console.error('Error:', error));
        }
        
        function updateHistoryTable(records) {
            const tbody = document.getElementById('historyTableBody');
            tbody.innerHTML = '';
            
            if (records.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px;">هیچ داده‌ای یافت نشد</td></tr>';
                return;
            }
            
            records.forEach(record => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${record.device_id}</td>
                    <td>${record.kind}</td>
                    <td>${record.room_id || '-'}</td>
                    <td>${record.value !== null ? record.value : '-'}</td>
                    <td>${record.unit || '-'}</td>
                    <td>${new Date(record.timestamp).toLocaleString('fa-IR')}</td>
                `;
                tbody.appendChild(row);
            });
        }
        
        function loadAnalytics() {
            fetch('/api/hybrid/analytics')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        createDeviceChart(data.analytics.device_stats);
                        createSensorChart(data.analytics.sensor_type_counts);
                    }
                })
                .catch(error => console.error('Error:', error));
        }
        
        function createDeviceChart(deviceStats) {
            const ctx = document.getElementById('deviceChart').getContext('2d');
            if (deviceChart) deviceChart.destroy();
            
            const labels = Object.keys(deviceStats);
            const data = Object.values(deviceStats).map(stat => stat.message_count);
            
            deviceChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'تعداد پیام‌ها',
                        data: data,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        function createSensorChart(sensorCounts) {
            const ctx = document.getElementById('sensorChart').getContext('2d');
            if (sensorChart) sensorChart.destroy();
            
            const labels = Object.keys(sensorCounts);
            const data = Object.values(sensorCounts);
            
            sensorChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.2)',
                            'rgba(54, 162, 235, 0.2)',
                            'rgba(255, 205, 86, 0.2)',
                            'rgba(75, 192, 192, 0.2)',
                            'rgba(153, 102, 255, 0.2)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 205, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true
                }
            });
        }
        
        function exportHistory() {
            fetch('/api/hybrid/export')
                .then(response => response.blob())
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'sensor_history.csv';
                    a.click();
                })
                .catch(error => console.error('Error:', error));
        }
        
        // Load initial data
        refreshLiveData();
        
        // Auto-refresh every 10 seconds
        setInterval(refreshLiveData, 10000);
    </script>
</body>
</html>
"""

@app.route('/')
def hybrid_dashboard():
    """Hybrid dashboard page"""
    return render_template_string(HYBRID_DASHBOARD_TEMPLATE)

@app.route('/api/hybrid/live')
def hybrid_live_data():
    """Get live data from hybrid subscriber"""
    try:
        live_data = hybrid_subscriber.get_live_data()
        stats = hybrid_subscriber.get_statistics()
        
        return jsonify({
            'success': True,
            'devices': live_data.get('latest_data', {}),
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hybrid/history')
def hybrid_history():
    """Get historical data from database"""
    try:
        limit = request.args.get('limit', 50, type=int)
        device_id = request.args.get('device')
        kind = request.args.get('kind')
        
        # Get data from database
        if device_id:
            records = db_manager.get_recent_data(device_id=device_id, limit=limit)
        elif kind:
            records = db_manager.get_recent_data(kind=kind, limit=limit)
        else:
            records = db_manager.get_recent_data(limit=limit)
        
        # Convert to JSON format
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
                'timestamp': record.timestamp.isoformat()
            })
        
        return jsonify({
            'success': True,
            'records': history_data,
            'count': len(history_data),
            'limit': limit
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hybrid/analytics')
def hybrid_analytics():
    """Get analytics data combining live and database"""
    try:
        # Get live statistics
        live_stats = hybrid_subscriber.get_statistics()
        
        # Get database statistics
        db_records = db_manager.get_recent_data(limit=1000)
        
        # Combine analytics
        analytics = {
            'device_stats': live_stats.get('device_stats', {}),
            'sensor_type_counts': live_stats.get('sensor_type_counts', {}),
            'room_counts': live_stats.get('room_counts', {}),
            'total_db_records': len(db_records),
            'live_devices': live_stats.get('total_devices', 0),
            'active_devices': live_stats.get('active_devices', 0)
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hybrid/export')
def hybrid_export():
    """Export historical data as CSV"""
    try:
        import csv
        import io
        
        # Get all records from database
        records = db_manager.get_recent_data(limit=10000)
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Device ID', 'Kind', 'Room ID', 'Value', 'Unit', 'Power W', 'Voltage', 'Current', 'On Status', 'Timestamp'])
        
        # Write data
        for record in records:
            writer.writerow([
                record.id,
                record.device_id,
                record.kind,
                record.room_id,
                record.value,
                record.unit,
                record.power_w,
                record.voltage,
                record.current,
                record.on_status,
                record.timestamp.isoformat()
            ])
        
        # Return CSV
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=sensor_history.csv'}
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"[Hybrid Dashboard] Client connected: {request.sid}")
    emit('status', {'message': 'Connected to hybrid sensor stream'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"[Hybrid Dashboard] Client disconnected: {request.sid}")

def start_hybrid_subscriber():
    """Start hybrid MQTT subscriber in background thread"""
    try:
        hybrid_subscriber.connect()
        print("[Hybrid Dashboard] Started hybrid MQTT subscriber")
    except Exception as e:
        print(f"[Hybrid Dashboard] Failed to start MQTT subscriber: {e}")

def broadcast_sensor_data():
    """Broadcast sensor data to WebSocket clients"""
    while True:
        try:
            time.sleep(1)  # Check every second
            
            # Get latest data
            latest_data = hybrid_subscriber.get_latest_data()
            
            # Broadcast to all connected clients
            for device_id, data in latest_data.items():
                socketio.emit('sensor_data', {
                    'device_id': device_id,
                    'data': data,
                    'timestamp': data.get('received_at')
                })
            
            # Broadcast status update every 10 seconds
            if int(time.time()) % 10 == 0:
                stats = hybrid_subscriber.get_statistics()
                socketio.emit('status_update', stats)
                
        except Exception as e:
            print(f"[Hybrid Dashboard] Error in broadcast loop: {e}")

if __name__ == '__main__':
    print("🚀 Starting Hybrid Sensor Dashboard...")
    print("📡 Features: Real-time display + Database storage")
    print("🌐 Dashboard: http://localhost:5000")
    print("=" * 60)
    
    # Start hybrid MQTT subscriber
    start_hybrid_subscriber()
    
    # Start broadcast thread
    broadcast_thread = threading.Thread(target=broadcast_sensor_data, daemon=True)
    broadcast_thread.start()
    
    # Start Flask-SocketIO server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
