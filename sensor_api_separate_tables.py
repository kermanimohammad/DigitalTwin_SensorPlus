#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from database_separate_tables import separate_db_manager
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    """Home page with API documentation"""
    return """
    <h1>Sensor Data API - Separate Tables</h1>
    <h2>Available Endpoints:</h2>
    <ul>
        <li><a href="/api/temperature">GET /api/temperature</a> - Get temperature data</li>
        <li><a href="/api/humidity">GET /api/humidity</a> - Get humidity data</li>
        <li><a href="/api/co2">GET /api/co2</a> - Get CO2 data</li>
        <li><a href="/api/light">GET /api/light</a> - Get light data</li>
        <li><a href="/api/solar">GET /api/solar</a> - Get solar data</li>
        <li><a href="/api/room/room1">GET /api/room/room1</a> - Get all data for a room</li>
        <li><a href="/api/stats">GET /api/stats</a> - Get statistics</li>
        <li><a href="/api/health">GET /api/health</a> - Health check</li>
    </ul>
    <h3>Query Parameters:</h3>
    <ul>
        <li>?limit=10 - Limit number of records</li>
        <li>?room=room1 - Filter by room</li>
    </ul>
    """

@app.route('/api/temperature')
def get_temperature_data():
    """Get temperature sensor data"""
    try:
        limit = request.args.get('limit', 50, type=int)
        room_id = request.args.get('room')
        
        records = separate_db_manager.get_temperature_data(room_id=room_id, limit=limit)
        
        data = []
        for record in records:
            data.append({
                'id': record.id,
                'device_id': record.device_id,
                'room_id': record.room_id,
                'temperature_c': record.temperature_c,
                'timestamp': record.timestamp.isoformat(),
                'raw_data': json.loads(record.raw_data) if record.raw_data else None
            })
        
        return jsonify({
            'success': True,
            'sensor_type': 'temperature',
            'count': len(data),
            'filters': {'limit': limit, 'room_id': room_id},
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/humidity')
def get_humidity_data():
    """Get humidity sensor data"""
    try:
        limit = request.args.get('limit', 50, type=int)
        room_id = request.args.get('room')
        
        records = separate_db_manager.get_humidity_data(room_id=room_id, limit=limit)
        
        data = []
        for record in records:
            data.append({
                'id': record.id,
                'device_id': record.device_id,
                'room_id': record.room_id,
                'humidity_percent': record.humidity_percent,
                'timestamp': record.timestamp.isoformat(),
                'raw_data': json.loads(record.raw_data) if record.raw_data else None
            })
        
        return jsonify({
            'success': True,
            'sensor_type': 'humidity',
            'count': len(data),
            'filters': {'limit': limit, 'room_id': room_id},
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/co2')
def get_co2_data():
    """Get CO2 sensor data"""
    try:
        limit = request.args.get('limit', 50, type=int)
        room_id = request.args.get('room')
        
        records = separate_db_manager.get_co2_data(room_id=room_id, limit=limit)
        
        data = []
        for record in records:
            data.append({
                'id': record.id,
                'device_id': record.device_id,
                'room_id': record.room_id,
                'co2_ppm': record.co2_ppm,
                'timestamp': record.timestamp.isoformat(),
                'raw_data': json.loads(record.raw_data) if record.raw_data else None
            })
        
        return jsonify({
            'success': True,
            'sensor_type': 'co2',
            'count': len(data),
            'filters': {'limit': limit, 'room_id': room_id},
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/light')
def get_light_data():
    """Get light sensor data"""
    try:
        limit = request.args.get('limit', 50, type=int)
        room_id = request.args.get('room')
        
        records = separate_db_manager.get_light_data(room_id=room_id, limit=limit)
        
        data = []
        for record in records:
            data.append({
                'id': record.id,
                'device_id': record.device_id,
                'room_id': record.room_id,
                'is_on': record.is_on,
                'power_watts': record.power_watts,
                'timestamp': record.timestamp.isoformat(),
                'raw_data': json.loads(record.raw_data) if record.raw_data else None
            })
        
        return jsonify({
            'success': True,
            'sensor_type': 'light',
            'count': len(data),
            'filters': {'limit': limit, 'room_id': room_id},
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/solar')
def get_solar_data():
    """Get solar sensor data"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        records = separate_db_manager.get_solar_data(limit=limit)
        
        data = []
        for record in records:
            data.append({
                'id': record.id,
                'device_id': record.device_id,
                'power_watts': record.power_watts,
                'voltage_volts': record.voltage_volts,
                'current_amps': record.current_amps,
                'timestamp': record.timestamp.isoformat(),
                'raw_data': json.loads(record.raw_data) if record.raw_data else None
            })
        
        return jsonify({
            'success': True,
            'sensor_type': 'solar',
            'count': len(data),
            'filters': {'limit': limit},
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/room/<room_id>')
def get_room_data(room_id):
    """Get all sensor data for a specific room"""
    try:
        summary = separate_db_manager.get_room_summary(room_id)
        
        if not summary:
            return jsonify({
                'success': False,
                'error': f'No data found for room {room_id}'
            }), 404
        
        # Convert to JSON format
        room_data = {
            'room_id': room_id,
            'temperature': None,
            'humidity': None,
            'co2': None,
            'light': None
        }
        
        if summary['temperature']:
            room_data['temperature'] = {
                'device_id': summary['temperature'].device_id,
                'temperature_c': summary['temperature'].temperature_c,
                'timestamp': summary['temperature'].timestamp.isoformat()
            }
        
        if summary['humidity']:
            room_data['humidity'] = {
                'device_id': summary['humidity'].device_id,
                'humidity_percent': summary['humidity'].humidity_percent,
                'timestamp': summary['humidity'].timestamp.isoformat()
            }
        
        if summary['co2']:
            room_data['co2'] = {
                'device_id': summary['co2'].device_id,
                'co2_ppm': summary['co2'].co2_ppm,
                'timestamp': summary['co2'].timestamp.isoformat()
            }
        
        if summary['light']:
            room_data['light'] = {
                'device_id': summary['light'].device_id,
                'is_on': summary['light'].is_on,
                'power_watts': summary['light'].power_watts,
                'timestamp': summary['light'].timestamp.isoformat()
            }
        
        return jsonify({
            'success': True,
            'room_id': room_id,
            'data': room_data
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
        # Get counts from each table
        temp_count = len(separate_db_manager.get_temperature_data(limit=1000))
        hum_count = len(separate_db_manager.get_humidity_data(limit=1000))
        co2_count = len(separate_db_manager.get_co2_data(limit=1000))
        light_count = len(separate_db_manager.get_light_data(limit=1000))
        solar_count = len(separate_db_manager.get_solar_data(limit=1000))
        
        stats = {
            'total_records': temp_count + hum_count + co2_count + light_count + solar_count,
            'sensor_counts': {
                'temperature': temp_count,
                'humidity': hum_count,
                'co2': co2_count,
                'light': light_count,
                'solar': solar_count
            },
            'tables': [
                'temperature_data',
                'humidity_data', 
                'co2_data',
                'light_data',
                'solar_data'
            ]
        }
        
        return jsonify({
            'success': True,
            'stats': stats
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
        separate_db_manager.test_connection()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'database': 'connected',
            'tables': 'separate_tables',
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
    print("=== Sensor Data API Server - Separate Tables ===")
    print("Available endpoints:")
    print("  - GET /api/temperature - Get temperature data")
    print("  - GET /api/humidity - Get humidity data")
    print("  - GET /api/co2 - Get CO2 data")
    print("  - GET /api/light - Get light data")
    print("  - GET /api/solar - Get solar data")
    print("  - GET /api/room/<room_id> - Get all data for a room")
    print("  - GET /api/stats - Get statistics")
    print("  - GET /api/health - Health check")
    print("=" * 60)
    print("Server starting on: http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
