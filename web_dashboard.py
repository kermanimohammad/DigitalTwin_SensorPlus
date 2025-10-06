#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, render_template_string, jsonify, request
from database import db_manager
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# HTML template for the dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>داشبورد سنسورها - Sensor Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            direction: rtl;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }
        .stat-label {
            color: #7f8c8d;
            margin-top: 5px;
        }
        .data-table {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
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
        .refresh-btn {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .refresh-btn:hover {
            background-color: #2980b9;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-left: 5px;
        }
        .status-online { background-color: #27ae60; }
        .status-offline { background-color: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <h1>داشبورد سنسورها - Sensor Dashboard</h1>
        
        <button class="refresh-btn" onclick="refreshData()">🔄 بروزرسانی</button>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="total-records">-</div>
                <div class="stat-label">کل رکوردها</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="active-devices">-</div>
                <div class="stat-label">دستگاه‌های فعال</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="last-update">-</div>
                <div class="stat-label">آخرین بروزرسانی</div>
            </div>
        </div>
        
        <div class="data-table">
            <table>
                <thead>
                    <tr>
                        <th>دستگاه</th>
                        <th>نوع</th>
                        <th>اتاق</th>
                        <th>مقدار</th>
                        <th>واحد</th>
                        <th>زمان</th>
                        <th>وضعیت</th>
                    </tr>
                </thead>
                <tbody id="data-table-body">
                    <tr>
                        <td colspan="7" style="text-align: center; padding: 20px;">
                            در حال بارگذاری...
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function refreshData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    updateStats(data.stats);
                    updateTable(data.records);
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }

        function updateStats(stats) {
            document.getElementById('total-records').textContent = stats.total_records;
            document.getElementById('active-devices').textContent = stats.active_devices;
            document.getElementById('last-update').textContent = stats.last_update;
        }

        function updateTable(records) {
            const tbody = document.getElementById('data-table-body');
            tbody.innerHTML = '';
            
            if (records.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 20px;">هیچ داده‌ای یافت نشد</td></tr>';
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
                    <td><span class="status-indicator status-online"></span>آنلاین</td>
                `;
                tbody.appendChild(row);
            });
        }

        // Load data on page load
        refreshData();
        
        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/data')
def api_data():
    """API endpoint to get sensor data"""
    try:
        # Get recent data
        records = db_manager.get_recent_data(limit=50)
        
        # Calculate stats
        total_records = len(records)
        active_devices = len(set(record.device_id for record in records))
        last_update = records[0].timestamp.strftime('%H:%M:%S') if records else 'هیچ'
        
        # Convert records to JSON-serializable format
        records_data = []
        for record in records:
            records_data.append({
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
            'stats': {
                'total_records': total_records,
                'active_devices': active_devices,
                'last_update': last_update
            },
            'records': records_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/room/<room_id>')
def api_room_data(room_id):
    """API endpoint to get data for a specific room"""
    try:
        records = db_manager.get_room_data(room_id, limit=100)
        
        records_data = []
        for record in records:
            records_data.append({
                'device_id': record.device_id,
                'kind': record.kind,
                'value': record.value,
                'unit': record.unit,
                'timestamp': record.timestamp.isoformat()
            })
        
        return jsonify({'room_id': room_id, 'records': records_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/device/<device_id>')
def api_device_data(device_id):
    """API endpoint to get data for a specific device"""
    try:
        records = db_manager.get_recent_data(device_id=device_id, limit=100)
        
        records_data = []
        for record in records:
            records_data.append({
                'kind': record.kind,
                'value': record.value,
                'unit': record.unit,
                'timestamp': record.timestamp.isoformat()
            })
        
        return jsonify({'device_id': device_id, 'records': records_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=== Starting Web Dashboard ===")
    print("Dashboard will be available at: http://localhost:5000")
    print("API endpoints:")
    print("  - GET /api/data - Get recent sensor data")
    print("  - GET /api/room/<room_id> - Get room data")
    print("  - GET /api/device/<device_id> - Get device data")
    print("================================")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
