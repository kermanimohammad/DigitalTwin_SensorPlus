#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import Error
import os

def test_bluehost_connection():
    """Test direct connection to Bluehost MySQL database"""
    
    # Database configuration from help.txt
    config = {
        'host': 'kbz.rew.mybluehost.me',
        'database': 'kbzrewmy_sensor',
        'user': 'mo_kerma',
        'password': 'Mehrafarid.5435',
        'port': 3306,
        'charset': 'utf8mb4',
        'autocommit': True,
        'connect_timeout': 10,
        'use_unicode': True
    }
    
    print("=== Testing Bluehost MySQL Connection ===")
    print(f"Host: {config['host']}")
    print(f"Database: {config['database']}")
    print(f"User: {config['user']}")
    print(f"Port: {config['port']}")
    print("=" * 50)
    
    try:
        # Test connection
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"SUCCESS: Connected to MySQL Server version {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            database_name = cursor.fetchone()
            print(f"Connected to database: {database_name[0]}")
            
            # Check if sensor_data table exists
            cursor.execute("SHOW TABLES LIKE 'sensor_data';")
            table_exists = cursor.fetchone()
            
            if table_exists:
                print("Table 'sensor_data' exists!")
                
                # Get table structure
                cursor.execute("DESCRIBE sensor_data;")
                columns = cursor.fetchall()
                print("\nTable structure:")
                for col in columns:
                    print(f"  {col[0]}: {col[1]} {'(NOT NULL)' if col[2] == 'NO' else ''} {'(PRIMARY KEY)' if col[3] == 'PRI' else ''}")
                
                # Count records
                cursor.execute("SELECT COUNT(*) FROM sensor_data;")
                count = cursor.fetchone()[0]
                print(f"\nTotal records in sensor_data: {count}")
                
                # Show recent records
                cursor.execute("SELECT device_id, kind, value, unit, timestamp FROM sensor_data ORDER BY timestamp DESC LIMIT 5;")
                recent_records = cursor.fetchall()
                print("\nRecent records:")
                for record in recent_records:
                    print(f"  - {record[0]} ({record[1]}): {record[2]} {record[3] or ''} at {record[4]}")
                    
            else:
                print("Table 'sensor_data' does not exist!")
                print("Creating table...")
                create_table_sql = """
                CREATE TABLE sensor_data (
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
                );
                """
                cursor.execute(create_table_sql)
                print("Table 'sensor_data' created successfully!")
            
            cursor.close()
            connection.close()
            print("\nConnection closed successfully!")
            return True
            
    except Error as e:
        print(f"ERROR: {e}")
        print("\nPossible solutions:")
        print("1. Check if your IP is whitelisted in Bluehost cPanel")
        print("2. Verify database credentials")
        print("3. Check if database exists")
        print("4. Try connecting from Bluehost cPanel MySQL section")
        return False

if __name__ == "__main__":
    test_bluehost_connection()
