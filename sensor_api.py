#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from database import db_manager
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    """Home page with API documentation"""
    return """
    <h1>Sensor Data API</h1>
    <h2>Available Endpoints:</h2>
    <ul>
        <li><a href="/api/sensors">GET /api/sensors</a> - Get latest sensor data</li>
        <li><a href="/api/sensors?limit=10">GET /api/sensors?limit=10</a> - Get latest 10 records</li>
        <li><a href="/api/sensors?room=room1">GET /api/sensors?room=room1</a> - Get data for specific room</li>
        <li><a href="/api/sensors?device=temp-1">GET /api/sensors?device=temp-1</a> - Get data for specific device</li>
        <li><a href="/api/sensors?kind=temperature">GET /api/sensors?kind=temperature</a> - Get data for specific sensor type</li>
        <li><a href="/api/stats">GET /api/stats</a> - Get statistics</li>
    </ul>
    """

@app.route('/api/sensors')
def get_sensor_data():
    """Get latest sensor data with optional filters"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        room_id = request.args.get('room')
        device_id = request.args.get('device')
        kind = request.args.get('kind')
        
        # Get data from database
        if room_id:
            records = db_manager.get_room_data(room_id, limit=limit)
        elif device_id:
            records = db_manager.get_recent_data(device_id=device_id, limit=limit)
        elif kind:
            records = db_manager.get_recent_data(kind=kind, limit=limit)
        else:
            records = db_manager.get_recent_data(limit=limit)
        
        # Convert to JSON format
        sensor_data = []
        for record in records:
            data = {
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
                'raw_data': json.loads(record.raw_data) if record.raw_data else None
            }
            sensor_data.append(data)
        
        return jsonify({
            'success': True,
            'count': len(sensor_data),
            'filters': {
                'limit': limit,
                'room_id': room_id,
                'device_id': device_id,
                'kind': kind
            },
            'data': sensor_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
def get_stats():
    """Get sensor data statistics"""
    try:
        # Get all recent data
        all_records = db_manager.get_recent_data(limit=1000)
        
        # Calculate statistics
        stats = {
            'total_records': len(all_records),
            'sensor_types': {},
            'devices': {},
            'rooms': {},
            'latest_update': None
        }
        
        # Group by sensor type
        for record in all_records:
            kind = record.kind
            if kind not in stats['sensor_types']:
                stats['sensor_types'][kind] = 0
            stats['sensor_types'][kind] += 1
            
            # Group by device
            device = record.device_id
            if device not in stats['devices']:
                stats['devices'][device] = 0
            stats['devices'][device] += 1
            
            # Group by room
            if record.room_id:
                room = record.room_id
                if room not in stats['rooms']:
                    stats['rooms'][room] = 0
                stats['rooms'][room] += 1
            
            # Find latest update
            if not stats['latest_update'] or record.timestamp > stats['latest_update']:
                stats['latest_update'] = record.timestamp.isoformat()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/rooms')
def get_rooms():
    """Get list of all rooms with latest data"""
    try:
        rooms = {}
        all_records = db_manager.get_recent_data(limit=1000)
        
        # Group by room
        for record in all_records:
            if record.room_id:
                room_id = record.room_id
                if room_id not in rooms:
                    rooms[room_id] = {
                        'room_id': room_id,
                        'sensors': {},
                        'latest_update': None
                    }
                
                # Store latest value for each sensor type
                if record.kind not in rooms[room_id]['sensors'] or \
                   record.timestamp > rooms[room_id]['sensors'][record.kind]['timestamp']:
                    rooms[room_id]['sensors'][record.kind] = {
                        'device_id': record.device_id,
                        'value': record.value,
                        'unit': record.unit,
                        'timestamp': record.timestamp.isoformat()
                    }
                
                # Update latest update time
                if not rooms[room_id]['latest_update'] or \
                   record.timestamp > datetime.fromisoformat(rooms[room_id]['latest_update'].replace('Z', '+00:00')):
                    rooms[room_id]['latest_update'] = record.timestamp.isoformat()
        
        return jsonify({
            'success': True,
            'rooms': list(rooms.values())
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_manager.test_connection()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("=== Sensor Data API Server ===")
    print("Available endpoints:")
    print("  - GET /api/sensors - Get latest sensor data")
    print("  - GET /api/sensors?limit=10 - Get latest 10 records")
    print("  - GET /api/sensors?room=room1 - Get data for specific room")
    print("  - GET /api/sensors?device=temp-1 - Get data for specific device")
    print("  - GET /api/sensors?kind=temperature - Get data for specific sensor type")
    print("  - GET /api/stats - Get statistics")
    print("  - GET /api/rooms - Get room data")
    print("  - GET /api/health - Health check")
    print("=" * 50)
    print("Server starting on: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
