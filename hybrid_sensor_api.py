#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid Sensor API - Real-time data with database history
- Provides live data from MQTT sensors
- Stores data in database for history
- Combines real-time access with historical analysis
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from database import db_manager
from mqtt_subscriber_hybrid import get_hybrid_subscriber
import json
import threading
import time
from datetime import datetime, timedelta
import signal
import sys

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get hybrid subscriber instance
hybrid_subscriber = get_hybrid_subscriber()

@app.route('/')
def home():
    """API home page with documentation"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hybrid Sensor API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
            .endpoint h3 { margin: 0 0 10px 0; color: #007bff; }
            .endpoint a { color: #007bff; text-decoration: none; font-weight: bold; }
            .endpoint a:hover { text-decoration: underline; }
            .description { color: #666; margin: 5px 0; }
            .status { background: #d4edda; color: #155724; padding: 10px; border-radius: 5px; margin: 20px 0; }
            .feature { background: #e7f3ff; color: #004085; padding: 8px; border-radius: 3px; margin: 5px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌡️ Hybrid Sensor API</h1>
            <div class="status">
                <strong>Status:</strong> Real-time sensor data + Database storage for history
            </div>
            
            <div class="feature">
                <strong>Features:</strong> Live MQTT data + Database history + Analytics + Export
            </div>
            
            <div class="endpoint">
                <h3>📊 Live Statistics</h3>
                <a href="/api/hybrid/stats" target="_blank">GET /api/hybrid/stats</a>
                <div class="description">Get real-time statistics from live sensor data</div>
            </div>
            
            <div class="endpoint">
                <h3>🔌 Live Devices</h3>
                <a href="/api/hybrid/live/devices" target="_blank">GET /api/hybrid/live/devices</a>
                <div class="description">Get all connected devices with their latest live data</div>
            </div>
            
            <div class="endpoint">
                <h3>📱 Live Device Data</h3>
                <a href="/api/hybrid/live/device/temp-1" target="_blank">GET /api/hybrid/live/device/{device_id}</a>
                <div class="description">Get live data for a specific device</div>
            </div>
            
            <div class="endpoint">
                <h3>📈 Device History (Database)</h3>
                <a href="/api/hybrid/history/device/temp-1?limit=50" target="_blank">GET /api/hybrid/history/device/{device_id}</a>
                <div class="description">Get historical data for a device from database</div>
            </div>
            
            <div class="endpoint">
                <h3>🏠 Room Data (Live + History)</h3>
                <a href="/api/hybrid/room/room1" target="_blank">GET /api/hybrid/room/{room_id}</a>
                <div class="description">Get both live and historical data for a room</div>
            </div>
            
            <div class="endpoint">
                <h3>🌡️ Sensor Type Data</h3>
                <a href="/api/hybrid/sensors/temperature" target="_blank">GET /api/hybrid/sensors/{sensor_type}</a>
                <div class="description">Get all devices of a specific sensor type (live + history)</div>
            </div>
            
            <div class="endpoint">
                <h3>📊 Analytics</h3>
                <a href="/api/hybrid/analytics" target="_blank">GET /api/hybrid/analytics</a>
                <div class="description">Get comprehensive analytics combining live and database data</div>
            </div>
            
            <div class="endpoint">
                <h3>💾 Export Data</h3>
                <a href="/api/hybrid/export" target="_blank">GET /api/hybrid/export</a>
                <div class="description">Export historical data as CSV</div>
            </div>
            
            <div class="endpoint">
                <h3>❤️ Health Check</h3>
                <a href="/api/hybrid/health" target="_blank">GET /api/hybrid/health</a>
                <div class="description">Check API, MQTT, and database connection status</div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/api/hybrid/stats')
def hybrid_stats():
    """Get comprehensive statistics combining live and database data"""
    try:
        # Get live statistics
        live_stats = hybrid_subscriber.get_statistics()
        
        # Get database statistics
        db_records = db_manager.get_recent_data(limit=1000)
        db_total = len(db_records)
        
        # Calculate database statistics
        db_sensor_counts = {}
        db_room_counts = {}
        db_device_counts = {}
        
        for record in db_records:
            # Count by sensor type
            kind = record.kind
            db_sensor_counts[kind] = db_sensor_counts.get(kind, 0) + 1
            
            # Count by room
            if record.room_id:
                room = record.room_id
                db_room_counts[room] = db_room_counts.get(room, 0) + 1
            
            # Count by device
            device = record.device_id
            db_device_counts[device] = db_device_counts.get(device, 0) + 1
        
        # Combine statistics
        combined_stats = {
            'live': {
                'total_devices': live_stats.get('total_devices', 0),
                'active_devices': live_stats.get('active_devices', 0),
                'sensor_type_counts': live_stats.get('sensor_type_counts', {}),
                'room_counts': live_stats.get('room_counts', {}),
                'global_stats': live_stats.get('global_stats', {})
            },
            'database': {
                'total_records': db_total,
                'sensor_type_counts': db_sensor_counts,
                'room_counts': db_room_counts,
                'device_counts': db_device_counts,
                'unique_devices': len(db_device_counts),
                'unique_rooms': len(db_room_counts)
            },
            'combined': {
                'data_source': 'hybrid_live_database',
                'mqtt_status': 'connected' if hybrid_subscriber.running else 'disconnected',
                'database_status': 'connected' if db_manager.engine else 'disconnected',
                'last_update': datetime.now().isoformat()
            }
        }
        
        return jsonify({
            'success': True,
            'stats': combined_stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hybrid/live/devices')
def hybrid_live_devices():
    """Get all connected devices with their latest live data"""
    try:
        live_data = hybrid_subscriber.get_live_data()
        devices = {}
        
        for device_id, data in live_data.get('latest_data', {}).items():
            stats = live_data.get('device_stats', {}).get(device_id, {})
            devices[device_id] = {
                'latest_data': data,
                'statistics': {
                    'first_seen': stats.get('first_seen'),
                    'last_seen': stats.get('last_seen'),
                    'message_count': stats.get('message_count', 0),
                    'sensor_types': list(stats.get('sensor_types', set())),
                    'db_save_count': stats.get('db_save_count', 0),
                    'db_fail_count': stats.get('db_fail_count', 0)
                },
                'history_count': len(hybrid_subscriber.get_device_history(device_id))
            }
        
        return jsonify({
            'success': True,
            'devices': devices,
            'count': len(devices),
            'data_source': 'live_mqtt',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hybrid/live/device/<device_id>')
def hybrid_live_device_data(device_id):
    """Get latest live data for a specific device"""
    try:
        device_data = hybrid_subscriber.get_live_data(device_id)
        
        if not device_data or not device_data.get('latest'):
            return jsonify({
                'success': False,
                'error': f'Device {device_id} not found or not connected'
            }), 404
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'latest_data': device_data['latest'],
            'statistics': device_data['stats'],
            'history_count': len(device_data['history']),
            'data_source': 'live_mqtt',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hybrid/history/device/<device_id>')
def hybrid_device_history(device_id):
    """Get historical data for a specific device from database"""
    try:
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 1000)  # Cap at 1000 records
        
        # Get data from database
        records = db_manager.get_recent_data(device_id=device_id, limit=limit)
        
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
            'device_id': device_id,
            'history': history_data,
            'count': len(history_data),
            'limit': limit,
            'data_source': 'database',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hybrid/room/<room_id>')
def hybrid_room_data(room_id):
    """Get both live and historical data for a specific room"""
    try:
        # Get live data for room
        live_data = hybrid_subscriber.get_live_data()
        live_room_devices = {}
        
        for device_id, data in live_data.get('latest_data', {}).items():
            if data.get('roomId') == room_id:
                stats = live_data.get('device_stats', {}).get(device_id, {})
                live_room_devices[device_id] = {
                    'latest_data': data,
                    'statistics': stats
                }
        
        # Get historical data for room from database
        db_records = db_manager.get_room_data(room_id, limit=100)
        db_history = []
        
        for record in db_records:
            db_history.append({
                'id': record.id,
                'device_id': record.device_id,
                'kind': record.kind,
                'value': record.value,
                'unit': record.unit,
                'timestamp': record.timestamp.isoformat()
            })
        
        return jsonify({
            'success': True,
            'room_id': room_id,
            'live_devices': live_room_devices,
            'live_count': len(live_room_devices),
            'database_history': db_history,
            'db_count': len(db_history),
            'data_source': 'hybrid_live_database',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hybrid/sensors/<sensor_type>')
def hybrid_sensor_type_data(sensor_type):
    """Get all devices of a specific sensor type (live + history)"""
    try:
        # Get live data for sensor type
        live_data = hybrid_subscriber.get_live_data()
        live_type_devices = {}
        
        for device_id, data in live_data.get('latest_data', {}).items():
            if data.get('kind', '').lower() == sensor_type.lower():
                stats = live_data.get('device_stats', {}).get(device_id, {})
                live_type_devices[device_id] = {
                    'latest_data': data,
                    'statistics': stats
                }
        
        # Get historical data for sensor type from database
        db_records = db_manager.get_recent_data(kind=sensor_type, limit=100)
        db_history = []
        
        for record in db_records:
            db_history.append({
                'id': record.id,
                'device_id': record.device_id,
                'room_id': record.room_id,
                'value': record.value,
                'unit': record.unit,
                'timestamp': record.timestamp.isoformat()
            })
        
        return jsonify({
            'success': True,
            'sensor_type': sensor_type,
            'live_devices': live_type_devices,
            'live_count': len(live_type_devices),
            'database_history': db_history,
            'db_count': len(db_history),
            'data_source': 'hybrid_live_database',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hybrid/analytics')
def hybrid_analytics():
    """Get comprehensive analytics combining live and database data"""
    try:
        # Get live statistics
        live_stats = hybrid_subscriber.get_statistics()
        
        # Get database analytics
        db_records = db_manager.get_recent_data(limit=1000)
        
        # Calculate trends
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)
        
        recent_records = [r for r in db_records if r.timestamp > last_hour]
        daily_records = [r for r in db_records if r.timestamp > last_day]
        
        # Device activity analysis
        device_activity = {}
        for record in db_records:
            device_id = record.device_id
            if device_id not in device_activity:
                device_activity[device_id] = {
                    'total_records': 0,
                    'recent_records': 0,
                    'daily_records': 0,
                    'last_activity': None,
                    'sensor_types': set()
                }
            
            device_activity[device_id]['total_records'] += 1
            device_activity[device_id]['sensor_types'].add(record.kind)
            
            if record.timestamp > last_hour:
                device_activity[device_id]['recent_records'] += 1
            if record.timestamp > last_day:
                device_activity[device_id]['daily_records'] += 1
            
            if not device_activity[device_id]['last_activity'] or record.timestamp > device_activity[device_id]['last_activity']:
                device_activity[device_id]['last_activity'] = record.timestamp
        
        # Convert sets to lists for JSON serialization
        for device_id in device_activity:
            device_activity[device_id]['sensor_types'] = list(device_activity[device_id]['sensor_types'])
            device_activity[device_id]['last_activity'] = device_activity[device_id]['last_activity'].isoformat() if device_activity[device_id]['last_activity'] else None
        
        analytics = {
            'live_stats': live_stats,
            'database_stats': {
                'total_records': len(db_records),
                'recent_records': len(recent_records),
                'daily_records': len(daily_records),
                'unique_devices': len(set(r.device_id for r in db_records)),
                'unique_rooms': len(set(r.room_id for r in db_records if r.room_id)),
                'sensor_types': len(set(r.kind for r in db_records))
            },
            'device_activity': device_activity,
            'trends': {
                'hourly_activity': len(recent_records),
                'daily_activity': len(daily_records),
                'activity_rate': len(recent_records) / max(1, len(daily_records)) * 100 if daily_records else 0
            },
            'timestamp': now.isoformat()
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics
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
        
        # Get query parameters
        device_id = request.args.get('device')
        kind = request.args.get('kind')
        limit = request.args.get('limit', 10000, type=int)
        
        # Get data from database
        if device_id:
            records = db_manager.get_recent_data(device_id=device_id, limit=limit)
        elif kind:
            records = db_manager.get_recent_data(kind=kind, limit=limit)
        else:
            records = db_manager.get_recent_data(limit=limit)
        
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
        filename = f'sensor_data_{device_id or kind or "all"}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hybrid/health')
def hybrid_health():
    """Health check endpoint for hybrid system"""
    try:
        # Check MQTT status
        mqtt_status = "connected" if hybrid_subscriber.running else "disconnected"
        
        # Check database status
        db_status = "connected" if db_manager.engine else "disconnected"
        
        # Get live statistics
        live_stats = hybrid_subscriber.get_statistics()
        
        # Get database record count
        try:
            db_records = db_manager.get_recent_data(limit=1)
            db_record_count = len(db_records)
        except:
            db_record_count = 0
        
        health_data = {
            'api_status': 'healthy',
            'mqtt_status': mqtt_status,
            'database_status': db_status,
            'live_devices': live_stats.get('total_devices', 0),
            'active_devices': live_stats.get('active_devices', 0),
            'total_messages': live_stats.get('global_stats', {}).get('total_messages', 0),
            'db_saves': live_stats.get('global_stats', {}).get('total_db_saves', 0),
            'db_failures': live_stats.get('global_stats', {}).get('total_db_failures', 0),
            'db_success_rate': live_stats.get('global_stats', {}).get('db_success_rate', 0),
            'database_records': db_record_count,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'health': health_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n[Hybrid API] Received signal {signum}, shutting down...")
    hybrid_subscriber.disconnect()
    sys.exit(0)

def start_hybrid_subscriber():
    """Start hybrid MQTT subscriber in background thread"""
    try:
        hybrid_subscriber.connect()
        print("[Hybrid API] Started hybrid MQTT subscriber")
    except Exception as e:
        print(f"[Hybrid API] Failed to start MQTT subscriber: {e}")

if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Starting Hybrid Sensor API...")
    print("📡 Features: Real-time data + Database storage")
    print("🌐 API: http://localhost:5001")
    print("📊 Stats: http://localhost:5001/api/hybrid/stats")
    print("🔌 Devices: http://localhost:5001/api/hybrid/live/devices")
    print("=" * 60)
    
    # Start hybrid MQTT subscriber
    start_hybrid_subscriber()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5001, debug=True)
