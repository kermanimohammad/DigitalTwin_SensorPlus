#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import Error
from datetime import datetime

def check_database_history():
    """Check the current state of database tables and their history"""
    
    print("=== Database History Check ===")
    
    # Database configuration
    config = {
        'host': 'kbz.rew.mybluehost.me',
        'database': 'kbzrewmy_sensor',
        'user': 'kbzrewmy_mo_kerma',
        'password': 'Mehrafarid.5435',
        'port': 3306,
        'charset': 'utf8mb4',
        'autocommit': True
    }
    
    try:
        # Connect to database
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("Connected to database successfully!")
        
        # Check each table
        tables = [
            'temperature_data',
            'humidity_data', 
            'co2_data',
            'light_data',
            'solar_data'
        ]
        
        print("\n=== Table History Analysis ===")
        
        for table in tables:
            print(f"\n--- {table} ---")
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total_count = cursor.fetchone()[0]
            print(f"Total records: {total_count}")
            
            if total_count > 0:
                # Get latest record
                cursor.execute(f"SELECT * FROM {table} ORDER BY timestamp DESC LIMIT 1")
                latest = cursor.fetchone()
                print(f"Latest record timestamp: {latest[4] if len(latest) > 4 else 'N/A'}")
                
                # Get oldest record
                cursor.execute(f"SELECT * FROM {table} ORDER BY timestamp ASC LIMIT 1")
                oldest = cursor.fetchone()
                print(f"Oldest record timestamp: {oldest[4] if len(oldest) > 4 else 'N/A'}")
                
                # Get records from last hour
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 HOUR)")
                recent_count = cursor.fetchone()[0]
                print(f"Records in last hour: {recent_count}")
                
                # Get records from last 24 hours
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)")
                daily_count = cursor.fetchone()[0]
                print(f"Records in last 24 hours: {daily_count}")
                
                # Show sample of recent records
                cursor.execute(f"SELECT device_id, timestamp FROM {table} ORDER BY timestamp DESC LIMIT 3")
                recent_records = cursor.fetchall()
                print("Recent records:")
                for record in recent_records:
                    print(f"  {record[0]}: {record[1]}")
            else:
                print("No records found")
        
        # Check if MQTT data is being received
        print(f"\n=== MQTT Data Reception Check ===")
        print(f"Current time: {datetime.now()}")
        
        # Check for any records in the last 5 minutes
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)")
            recent_count = cursor.fetchone()[0]
            if recent_count > 0:
                print(f"{table}: {recent_count} records in last 5 minutes - MQTT is working!")
            else:
                print(f"{table}: No records in last 5 minutes - MQTT may not be working")
        
        cursor.close()
        connection.close()
        
        print("\n" + "="*50)
        print("Database history check completed!")
        print("="*50)
        
        return True
        
    except Error as e:
        print(f"Error during database check: {e}")
        return False

if __name__ == "__main__":
    check_database_history()
