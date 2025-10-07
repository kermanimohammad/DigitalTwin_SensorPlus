#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Check and Repair Script
Checks all tables and recreates missing ones
"""

import sys
import os
from datetime import datetime
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, DB_CONFIG, USE_SQLITE
import mysql.connector
from mysql.connector import Error

def check_database_tables():
    """Check all database tables and their status"""
    print("=" * 60)
    print("Database Tables Check and Repair")
    print("=" * 60)
    
    try:
        if USE_SQLITE:
            print("❌ This script requires MySQL connection")
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
        
        # List of required tables
        required_tables = [
            'sensor_data',      # Legacy table
            'temperature_data', # Separate tables
            'humidity_data',
            'co2_data',
            'light_data',
            'solar_data'
        ]
        
        print("\n1. Checking table existence...")
        existing_tables = []
        missing_tables = []
        
        for table in required_tables:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            result = cursor.fetchone()
            if result:
                existing_tables.append(table)
                print(f"   ✅ Table {table} exists")
            else:
                missing_tables.append(table)
                print(f"   ❌ Table {table} is missing")
        
        # Check table structures
        print("\n2. Checking table structures...")
        for table in existing_tables:
            try:
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                print(f"   {table}: {len(columns)} columns")
                
                # Check for specific columns
                column_names = [col[0] for col in columns]
                if table == 'sensor_data':
                    required_columns = ['id', 'device_id', 'kind', 'value', 'timestamp']
                elif table == 'temperature_data':
                    required_columns = ['id', 'device_id', 'temperature_c', 'timestamp']
                elif table == 'humidity_data':
                    required_columns = ['id', 'device_id', 'humidity_percent', 'timestamp']
                elif table == 'co2_data':
                    required_columns = ['id', 'device_id', 'co2_ppm', 'timestamp']
                elif table == 'light_data':
                    required_columns = ['id', 'device_id', 'is_on', 'power_watts', 'timestamp']
                elif table == 'solar_data':
                    required_columns = ['id', 'device_id', 'power_watts', 'voltage_volts', 'current_amps', 'timestamp']
                
                missing_columns = [col for col in required_columns if col not in column_names]
                if missing_columns:
                    print(f"      ⚠️  Missing columns: {missing_columns}")
                else:
                    print(f"      ✅ All required columns present")
                    
            except Error as e:
                print(f"   ❌ Error describing {table}: {e}")
        
        # Check data counts
        print("\n3. Checking data counts...")
        for table in existing_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   {table}: {count} records")
            except Error as e:
                print(f"   ❌ Error counting {table}: {e}")
        
        # Recreate missing tables
        if missing_tables:
            print(f"\n4. Recreating {len(missing_tables)} missing tables...")
            recreate_missing_tables(cursor, missing_tables)
        else:
            print("\n4. ✅ All tables exist - no recreation needed")
        
        # Test data insertion
        print("\n5. Testing data insertion...")
        test_data_insertion()
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 60)
        print("✅ Database check and repair completed!")
        print("=" * 60)
        
        return True
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def recreate_missing_tables(cursor, missing_tables):
    """Recreate missing tables"""
    
    table_definitions = {
        'sensor_data': '''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            device_id VARCHAR(50) NOT NULL,
            kind VARCHAR(20) NOT NULL,
            room_id VARCHAR(20),
            value FLOAT,
            unit VARCHAR(10),
            power_w FLOAT,
            voltage FLOAT,
            current FLOAT,
            on_status BOOLEAN,
            timestamp DATETIME NOT NULL,
            raw_data TEXT,
            INDEX idx_device_id (device_id),
            INDEX idx_kind (kind),
            INDEX idx_room_id (room_id),
            INDEX idx_timestamp (timestamp)
        )
        ''',
        'temperature_data': '''
        CREATE TABLE IF NOT EXISTS temperature_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            device_id VARCHAR(50) NOT NULL,
            room_id VARCHAR(20),
            temperature_c FLOAT,
            timestamp DATETIME NOT NULL,
            raw_data TEXT,
            INDEX idx_device_id (device_id),
            INDEX idx_room_id (room_id),
            INDEX idx_timestamp (timestamp)
        )
        ''',
        'humidity_data': '''
        CREATE TABLE IF NOT EXISTS humidity_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            device_id VARCHAR(50) NOT NULL,
            room_id VARCHAR(20),
            humidity_percent FLOAT,
            timestamp DATETIME NOT NULL,
            raw_data TEXT,
            INDEX idx_device_id (device_id),
            INDEX idx_room_id (room_id),
            INDEX idx_timestamp (timestamp)
        )
        ''',
        'co2_data': '''
        CREATE TABLE IF NOT EXISTS co2_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            device_id VARCHAR(50) NOT NULL,
            room_id VARCHAR(20),
            co2_ppm INT,
            timestamp DATETIME NOT NULL,
            raw_data TEXT,
            INDEX idx_device_id (device_id),
            INDEX idx_room_id (room_id),
            INDEX idx_timestamp (timestamp)
        )
        ''',
        'light_data': '''
        CREATE TABLE IF NOT EXISTS light_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            device_id VARCHAR(50) NOT NULL,
            room_id VARCHAR(20),
            is_on BOOLEAN,
            power_watts FLOAT,
            timestamp DATETIME NOT NULL,
            raw_data TEXT,
            INDEX idx_device_id (device_id),
            INDEX idx_room_id (room_id),
            INDEX idx_timestamp (timestamp)
        )
        ''',
        'solar_data': '''
        CREATE TABLE IF NOT EXISTS solar_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            device_id VARCHAR(50) NOT NULL,
            power_watts FLOAT,
            voltage_volts FLOAT,
            current_amps FLOAT,
            timestamp DATETIME NOT NULL,
            raw_data TEXT,
            INDEX idx_device_id (device_id),
            INDEX idx_timestamp (timestamp)
        )
        '''
    }
    
    for table in missing_tables:
        if table in table_definitions:
            try:
                print(f"   Creating table: {table}")
                cursor.execute(table_definitions[table])
                print(f"   ✅ Table {table} created successfully")
            except Error as e:
                print(f"   ❌ Error creating {table}: {e}")
        else:
            print(f"   ⚠️  No definition found for {table}")

def test_data_insertion():
    """Test data insertion into all tables"""
    
    test_data = [
        {
            'deviceId': 'temp-repair-test',
            'kind': 'temperature',
            'value': 25.0,
            'unit': '°C',
            'roomId': 'test-room',
            'ts': int(datetime.now().timestamp() * 1000)
        },
        {
            'deviceId': 'hum-repair-test',
            'kind': 'humidity',
            'value': 60.0,
            'unit': '%',
            'roomId': 'test-room',
            'ts': int(datetime.now().timestamp() * 1000)
        },
        {
            'deviceId': 'co2-repair-test',
            'kind': 'co2',
            'value': 450,
            'unit': 'ppm',
            'roomId': 'test-room',
            'ts': int(datetime.now().timestamp() * 1000)
        },
        {
            'deviceId': 'light-repair-test',
            'kind': 'light',
            'value': 800,
            'unit': 'lux',
            'on': True,
            'powerW': 15.0,
            'roomId': 'test-room',
            'ts': int(datetime.now().timestamp() * 1000)
        },
        {
            'deviceId': 'solar-repair-test',
            'kind': 'solar',
            'value': 120.0,
            'unit': 'W',
            'powerW': 120.0,
            'voltage': 24.0,
            'current': 5.0,
            'on': True,
            'ts': int(datetime.now().timestamp() * 1000)
        }
    ]
    
    for data in test_data:
        success = db_manager.save_sensor_data(data)
        if success:
            print(f"   ✅ Test data saved: {data['kind']} - {data['deviceId']}")
        else:
            print(f"   ❌ Failed to save test data: {data['kind']} - {data['deviceId']}")

def show_final_status():
    """Show final database status"""
    print("\n6. Final database status...")
    
    try:
        if USE_SQLITE:
            print("❌ Cannot show status for SQLite")
            return
        
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
        
        tables = ['sensor_data', 'temperature_data', 'humidity_data', 'co2_data', 'light_data', 'solar_data']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   {table}: {count} records")
            except Error as e:
                print(f"   {table}: ❌ Error - {e}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error showing final status: {e}")

if __name__ == "__main__":
    success = check_database_tables()
    if success:
        show_final_status()
    else:
        print("❌ Database check and repair failed!")
