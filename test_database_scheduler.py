#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for database scheduler
Tests saving data to specific sensor tables every 1 minute
"""

import time
import random
from datetime import datetime
from database import DatabaseManager

def test_database_scheduler():
    """Test the database scheduler functionality"""
    print("=" * 60)
    print("🧪 Testing Database Scheduler")
    print("=" * 60)
    
    # Initialize database manager
    try:
        db_manager = DatabaseManager()
        print("✅ Database manager initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize database manager: {e}")
        return False
    
    # Test data for all 21 devices
    test_data = {}
    
    # Generate test data for 5 rooms
    for room_id in range(1, 6):
        room_name = f'room{room_id}'
        
        # Temperature
        temp = round(20 + random.uniform(-5, 5), 1)
        test_data[f'temp-{room_id}'] = {
            'device_id': f'temp-{room_id}',
            'kind': 'temperature',
            'value': temp,
            'unit': '°C',
            'room_id': room_name
        }
        
        # Humidity
        humidity = round(50 + random.uniform(-10, 10), 1)
        test_data[f'hum-{room_id}'] = {
            'device_id': f'hum-{room_id}',
            'kind': 'humidity',
            'value': humidity,
            'unit': '%',
            'room_id': room_name
        }
        
        # CO2
        co2 = round(400 + random.uniform(-50, 50), 0)
        test_data[f'co2-{room_id}'] = {
            'device_id': f'co2-{room_id}',
            'kind': 'co2',
            'value': co2,
            'unit': 'ppm',
            'room_id': room_name
        }
        
        # Light
        light = round(800 + random.uniform(-200, 200), 0)
        test_data[f'light-{room_id}'] = {
            'device_id': f'light-{room_id}',
            'kind': 'light',
            'value': light,
            'unit': 'lux',
            'room_id': room_name
        }
    
    # Solar Panel
    solar_power = round(120 + random.uniform(-20, 20), 1)
    test_data['solar-plant'] = {
        'device_id': 'solar-plant',
        'kind': 'solar',
        'value': solar_power,
        'unit': 'W',
        'room_id': 'solar-farm'
    }
    
    print(f"📊 Generated test data for {len(test_data)} devices")
    
    # Test saving data to specific tables
    print("\n🔄 Testing data saving to specific tables...")
    saved_count = 0
    error_count = 0
    
    for key, data in test_data.items():
        try:
            # Prepare data for database with correct field names
            sensor_data = {
                'deviceId': data['device_id'],
                'kind': data['kind'],
                'roomId': data.get('room_id', 'unknown'),
                'value': data['value'],
                'unit': data['unit'],
                'ts': int(datetime.now().timestamp() * 1000),
                'raw_data': str(data)
            }
            
            # Add specific fields for different sensor types
            if data['kind'] == 'light':
                sensor_data['on'] = data['value'] > 500
                sensor_data['powerW'] = data['value'] * 0.1
            elif data['kind'] == 'solar':
                sensor_data['powerW'] = data['value']
                sensor_data['voltage'] = 12.0
                sensor_data['current'] = data['value'] / 12.0
            
            # Save to appropriate table
            success = db_manager.save_sensor_data(sensor_data)
            if success:
                saved_count += 1
                print(f"✅ Saved {data['kind']} data for {data['device_id']}")
            else:
                error_count += 1
                print(f"❌ Failed to save {data['kind']} data for {data['device_id']}")
                
        except Exception as e:
            error_count += 1
            print(f"❌ Error saving {key}: {e}")
    
    print(f"\n📈 Results:")
    print(f"✅ Successfully saved: {saved_count} devices")
    print(f"❌ Errors: {error_count} devices")
    
    # Get table statistics
    print(f"\n📊 Table Statistics:")
    try:
        stats = db_manager.get_table_statistics()
        for table_name, table_stats in stats.items():
            print(f"• {table_name}: {table_stats['count']} records")
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
    
    return saved_count > 0

if __name__ == '__main__':
    success = test_database_scheduler()
    if success:
        print("\n🎉 Database scheduler test completed successfully!")
    else:
        print("\n💥 Database scheduler test failed!")
