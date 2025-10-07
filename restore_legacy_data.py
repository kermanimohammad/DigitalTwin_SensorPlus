#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restore Legacy Data Script
Moves data from separate tables back to legacy sensor_data table if needed
"""

import sys
import os
from datetime import datetime
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, DB_CONFIG, USE_SQLITE, SensorData
import mysql.connector
from mysql.connector import Error

def restore_legacy_data():
    """Restore data from separate tables to legacy sensor_data table"""
    print("=" * 60)
    print("Restore Legacy Data from Separate Tables")
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
        
        # Check current data in separate tables
        print("\n1. Checking data in separate tables...")
        separate_tables = {
            'temperature_data': 'temperature',
            'humidity_data': 'humidity', 
            'co2_data': 'co2',
            'light_data': 'light',
            'solar_data': 'solar'
        }
        
        total_records = 0
        for table, kind in separate_tables.items():
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                total_records += count
                print(f"   {table}: {count} records")
            except Error as e:
                print(f"   ❌ Error counting {table}: {e}")
        
        if total_records == 0:
            print("   ⚠️  No data found in separate tables")
            return True
        
        # Check current data in legacy table
        print("\n2. Checking legacy sensor_data table...")
        try:
            cursor.execute("SELECT COUNT(*) FROM sensor_data")
            legacy_count = cursor.fetchone()[0]
            print(f"   sensor_data: {legacy_count} records")
        except Error as e:
            print(f"   ❌ Error counting sensor_data: {e}")
            return False
        
        # Ask user if they want to restore
        if legacy_count > 0:
            print(f"\n⚠️  Legacy table already has {legacy_count} records.")
            print("   This operation will add more records to the legacy table.")
        
        print(f"\n📊 Found {total_records} records in separate tables.")
        print("   This will create corresponding records in the legacy sensor_data table.")
        
        # Restore data from separate tables
        print("\n3. Restoring data to legacy table...")
        restored_count = 0
        
        for table, kind in separate_tables.items():
            try:
                if table == 'temperature_data':
                    cursor.execute("""
                        INSERT INTO sensor_data (device_id, kind, room_id, value, unit, timestamp, raw_data)
                        SELECT device_id, 'temperature', room_id, temperature_c, '°C', timestamp, raw_data
                        FROM temperature_data
                    """)
                elif table == 'humidity_data':
                    cursor.execute("""
                        INSERT INTO sensor_data (device_id, kind, room_id, value, unit, timestamp, raw_data)
                        SELECT device_id, 'humidity', room_id, humidity_percent, '%', timestamp, raw_data
                        FROM humidity_data
                    """)
                elif table == 'co2_data':
                    cursor.execute("""
                        INSERT INTO sensor_data (device_id, kind, room_id, value, unit, timestamp, raw_data)
                        SELECT device_id, 'co2', room_id, co2_ppm, 'ppm', timestamp, raw_data
                        FROM co2_data
                    """)
                elif table == 'light_data':
                    cursor.execute("""
                        INSERT INTO sensor_data (device_id, kind, room_id, value, unit, power_w, on_status, timestamp, raw_data)
                        SELECT device_id, 'light', room_id, 
                               CASE WHEN is_on THEN power_watts ELSE 0 END, 
                               'lux', power_watts, is_on, timestamp, raw_data
                        FROM light_data
                    """)
                elif table == 'solar_data':
                    cursor.execute("""
                        INSERT INTO sensor_data (device_id, kind, value, unit, power_w, voltage, current, on_status, timestamp, raw_data)
                        SELECT device_id, 'solar', power_watts, 'W', power_watts, voltage_volts, current_amps, 
                               CASE WHEN power_watts > 0 THEN 1 ELSE 0 END, timestamp, raw_data
                        FROM solar_data
                    """)
                
                affected_rows = cursor.rowcount
                restored_count += affected_rows
                print(f"   ✅ Restored {affected_rows} records from {table}")
                
            except Error as e:
                print(f"   ❌ Error restoring from {table}: {e}")
        
        # Commit changes
        connection.commit()
        
        # Show final status
        print("\n4. Final status...")
        try:
            cursor.execute("SELECT COUNT(*) FROM sensor_data")
            final_count = cursor.fetchone()[0]
            print(f"   sensor_data: {final_count} records (added {restored_count})")
        except Error as e:
            print(f"   ❌ Error getting final count: {e}")
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 60)
        print("✅ Legacy data restoration completed!")
        print(f"📊 Restored {restored_count} records to sensor_data table")
        print("=" * 60)
        
        return True
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_data_summary():
    """Show summary of all data"""
    print("\n5. Data summary...")
    
    try:
        if USE_SQLITE:
            print("❌ Cannot show summary for SQLite")
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
        
        # Show data by sensor type in legacy table
        print("   Data in sensor_data table by type:")
        cursor.execute("""
            SELECT kind, COUNT(*) as count, 
                   MIN(timestamp) as earliest, 
                   MAX(timestamp) as latest
            FROM sensor_data 
            GROUP BY kind 
            ORDER BY count DESC
        """)
        
        results = cursor.fetchall()
        for kind, count, earliest, latest in results:
            print(f"     {kind}: {count} records ({earliest} to {latest})")
        
        # Show data in separate tables
        print("   Data in separate tables:")
        separate_tables = ['temperature_data', 'humidity_data', 'co2_data', 'light_data', 'solar_data']
        for table in separate_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"     {table}: {count} records")
            except Error as e:
                print(f"     {table}: ❌ Error - {e}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error showing summary: {e}")

if __name__ == "__main__":
    success = restore_legacy_data()
    if success:
        show_data_summary()
    else:
        print("❌ Legacy data restoration failed!")
