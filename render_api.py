#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
import os

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'kbz.rew.mybluehost.me',
    'database': 'kbzrewmy_sensor',
    'user': 'kbzrewmy_mo_kerma',
    'password': 'Mehrafarid.5435',
    'port': 3306,
    'charset': 'utf8mb4',
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
    """Home page with API documentation"""
    return """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sensor Data API</title>
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌡️ Sensor Data API</h1>
            <p style="text-align: center; color: #666;">API برای دریافت اطلاعات سنسورها از دیتابیس</p>
            
            <div class="endpoint">
                <h3>📊 آمار کلی</h3>
                <a href="/api/stats" target="_blank">GET /api/stats</a>
                <div class="description">نمایش آمار کلی تمام سنسورها</div>
                <button class="test-btn" onclick="testEndpoint('/api/stats')">تست</button>
            </div>
            
            <div class="endpoint">
                <h3>🌡️ داده‌های دما</h3>
                <a href="/api/temperature" target="_blank">GET /api/temperature</a>
                <div class="description">دریافت آخرین داده‌های دما</div>
                <button class="test-btn" onclick="testEndpoint('/api/temperature')">تست</button>
            </div>
            
            <div class="endpoint">
                <h3>💧 داده‌های رطوبت</h3>
                <a href="/api/humidity" target="_blank">GET /api/humidity</a>
                <div class="description">دریافت آخرین داده‌های رطوبت</div>
                <button class="test-btn" onclick="testEndpoint('/api/humidity')">تست</button>
            </div>
            
            <div class="endpoint">
                <h3>🌬️ داده‌های CO2</h3>
                <a href="/api/co2" target="_blank">GET /api/co2</a>
                <div class="description">دریافت آخرین داده‌های CO2</div>
                <button class="test-btn" onclick="testEndpoint('/api/co2')">تست</button>
            </div>
            
            <div class="endpoint">
                <h3>💡 داده‌های نور</h3>
                <a href="/api/light" target="_blank">GET /api/light</a>
                <div class="description">دریافت آخرین داده‌های نور</div>
                <button class="test-btn" onclick="testEndpoint('/api/light')">تست</button>
            </div>
            
            <div class="endpoint">
                <h3>☀️ داده‌های خورشیدی</h3>
                <a href="/api/solar" target="_blank">GET /api/solar</a>
                <div class="description">دریافت آخرین داده‌های خورشیدی</div>
                <button class="test-btn" onclick="testEndpoint('/api/solar')">تست</button>
            </div>
            
            <div class="endpoint">
                <h3>🏠 داده‌های اتاق</h3>
                <a href="/api/room/room1" target="_blank">GET /api/room/room1</a>
                <div class="description">دریافت تمام داده‌های یک اتاق</div>
                <button class="test-btn" onclick="testEndpoint('/api/room/room1')">تست</button>
            </div>
            
            <div class="endpoint">
                <h3>❤️ وضعیت سیستم</h3>
                <a href="/api/health" target="_blank">GET /api/health</a>
                <div class="description">بررسی وضعیت اتصال به دیتابیس</div>
                <button class="test-btn" onclick="testEndpoint('/api/health')">تست</button>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background: #e9ecef; border-radius: 5px;">
                <h4>📝 نحوه استفاده:</h4>
                <ul>
                    <li>روی هر لینک کلیک کنید تا JSON response را ببینید</li>
                    <li>از دکمه "تست" برای نمایش نتیجه در همین صفحه استفاده کنید</li>
                    <li>می‌توانید از پارامتر <code>?limit=10</code> برای محدود کردن تعداد رکوردها استفاده کنید</li>
                </ul>
            </div>
        </div>
        
        <script>
            function testEndpoint(endpoint) {
                fetch(endpoint)
                    .then(response => response.json())
                    .then(data => {
                        alert('نتیجه: ' + JSON.stringify(data, null, 2));
                    })
                    .catch(error => {
                        alert('خطا: ' + error.message);
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
    """Get solar data"""
    return get_sensor_data('solar_data', 'power_watts,voltage_volts,current_amps', 'solar')

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
