#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script using direct SQL queries for separate tables
"""

import sys
import os
from datetime import datetime
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DB_CONFIG, USE_SQLITE
import mysql.connector
from mysql.connector import Error

def test_direct_sql():
    """Test separate tables using direct SQL queries"""
    print("=" * 60)
    print("Testing Separate Tables with Direct SQL")
    print("=" * 60)
    
    try:
        if USE_SQLITE:
            print("❌ This test requires MySQL connection")
            return False
        
        # Connect to MySQL
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port'],
            charset=DB_CONFIG['charset']
        )
        
        cursor = connection.cursor()
        
        # Test 1: Check if tables exist
        print("\n1. Checking table existence...")
        tables = ['temperature_data', 'humidity_data', 'co2_data', 'light_data', 'solar_data']
        for table in tables:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            result = cursor.fetchone()
            if result:
                print(f"   ✅ Table {table} exists")
            else:
                print(f"   ❌ Table {table} does not exist")
        
        # Test 2: Check table structure
        print("\n2. Checking table structure...")
        for table in tables:
            try:
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                print(f"   {table}: {len(columns)} columns")
                for col in columns:
                    print(f"      - {col[0]} ({col[1]})")
            except Error as e:
                print(f"   ❌ Error describing {table}: {e}")
        
        # Test 3: Insert test data
        print("\n3. Inserting test data...")
        test_data = [
            ('temperature_data', 'temp-test-1', 'test-room', 25.5, '°C'),
            ('humidity_data', 'hum-test-1', 'test-room', 60.2, '%'),
            ('co2_data', 'co2-test-1', 'test-room', 450, 'ppm'),
            ('light_data', 'light-test-1', 'test-room', 800, 'lux'),
            ('solar_data', 'solar-test-1', 'test-room', 120.5, 'W')
        ]
        
        for table, device_id, room_id, value, unit in test_data:
            try:
                if table == 'solar_data':
                    sql = f"""
                    INSERT INTO {table} (device_id, room_id, value, unit, power_w, voltage, current, on_status, timestamp, raw_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    raw_data = json.dumps({
                        'deviceId': device_id,
                        'kind': table.replace('_data', ''),
                        'value': value,
                        'unit': unit,
                        'roomId': room_id,
                        'ts': int(datetime.now().timestamp() * 1000)
                    })
                    cursor.execute(sql, (device_id, room_id, value, unit, value, 24.0, 5.02, True, datetime.now(), raw_data))
                else:
                    sql = f"""
                    INSERT INTO {table} (device_id, room_id, value, unit, timestamp, raw_data)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    raw_data = json.dumps({
                        'deviceId': device_id,
                        'kind': table.replace('_data', ''),
                        'value': value,
                        'unit': unit,
                        'roomId': room_id,
                        'ts': int(datetime.now().timestamp() * 1000)
                    })
                    cursor.execute(sql, (device_id, room_id, value, unit, datetime.now(), raw_data))
                
                connection.commit()
                print(f"   ✅ Inserted data into {table}")
            except Error as e:
                print(f"   ❌ Error inserting into {table}: {e}")
        
        # Test 4: Query data
        print("\n4. Querying data...")
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   {table}: {count} records")
                
                cursor.execute(f"SELECT device_id, value, unit, timestamp FROM {table} ORDER BY timestamp DESC LIMIT 1")
                latest = cursor.fetchone()
                if latest:
                    print(f"      Latest: {latest[0]} = {latest[1]} {latest[2]} at {latest[3]}")
            except Error as e:
                print(f"   ❌ Error querying {table}: {e}")
        
        # Test 5: Query by room
        print("\n5. Querying by room...")
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE room_id = 'test-room'")
                count = cursor.fetchone()[0]
                print(f"   {table} (test-room): {count} records")
            except Error as e:
                print(f"   ❌ Error querying {table} by room: {e}")
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 60)
        print("✅ Direct SQL test completed!")
        print("=" * 60)
        
        return True
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_direct_sql()
