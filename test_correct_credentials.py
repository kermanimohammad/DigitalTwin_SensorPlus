#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime

def test_bluehost_with_correct_credentials():
    """Test connection with correct credentials from help.txt"""
    
    print("=== Testing Bluehost with Correct Credentials ===")
    print("From help.txt:")
    print("URL: kbz.rew.mybluehost.me")
    print("Database: kbzrewmy_sensor")
    print("User: kbzrewmy_mo_kerma")
    print("Password: Mehrafarid.5435")
    print("=" * 60)
    
    # Correct configuration from help.txt
    config = {
        'host': 'kbz.rew.mybluehost.me',
        'database': 'kbzrewmy_sensor',
        'user': 'kbzrewmy_mo_kerma',  # Correct username
        'password': 'Mehrafarid.5435',
        'port': 3306,
        'charset': 'utf8mb4',
        'autocommit': True
    }
    
    try:
        print("Connecting to Bluehost MySQL...")
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            print("SUCCESS: Connected to Bluehost MySQL!")
            
            cursor = connection.cursor()
            
            # Get server info
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"MySQL Version: {version[0]}")
            
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()
            print(f"Connected to database: {db_name[0]}")
            
            # Check existing tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"Existing tables: {[table[0] for table in tables]}")
            
            # Create sensor_data table
            print("\nCreating sensor_data table...")
            create_table_sql = """
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
            );
            """
            cursor.execute(create_table_sql)
            connection.commit()
            print("Table 'sensor_data' created/verified successfully!")
            
            # Test inserting sample data
            print("\nTesting data insertion...")
            sample_data = {
                "deviceId": "test-temp-1",
                "kind": "temperature",
                "roomId": "test-room",
                "ts": int(datetime.now().timestamp() * 1000),
                "value": 23.5,
                "unit": "C"
            }
            
            insert_sql = """
            INSERT INTO sensor_data 
            (device_id, kind, room_id, value, unit, power_w, voltage, current, on_status, timestamp, raw_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            timestamp = datetime.fromtimestamp(sample_data['ts'] / 1000)
            data = (
                sample_data['deviceId'],
                sample_data['kind'],
                sample_data['roomId'],
                sample_data['value'],
                sample_data['unit'],
                None,  # power_w
                None,  # voltage
                None,  # current
                None,  # on_status
                timestamp,
                json.dumps(sample_data)
            )
            
            cursor.execute(insert_sql, data)
            connection.commit()
            print("Sample data inserted successfully!")
            
            # Test retrieving data
            print("\nTesting data retrieval...")
            cursor.execute("SELECT COUNT(*) FROM sensor_data")
            count = cursor.fetchone()[0]
            print(f"Total records in sensor_data: {count}")
            
            cursor.execute("""
                SELECT device_id, kind, value, unit, timestamp 
                FROM sensor_data 
                ORDER BY timestamp DESC 
                LIMIT 5
            """)
            recent_records = cursor.fetchall()
            print("\nRecent records:")
            for record in recent_records:
                print(f"  - {record[0]} ({record[1]}): {record[2]} {record[3] or ''} at {record[4]}")
            
            cursor.close()
            connection.close()
            
            print("\n" + "=" * 60)
            print("SUCCESS: Bluehost MySQL is working perfectly!")
            print("You can now use this database for your sensor data.")
            print("=" * 60)
            
            return True
            
    except Error as e:
        print(f"ERROR: {e}")
        
        if "Access denied" in str(e):
            print("\nSOLUTION:")
            print("1. Go to Bluehost cPanel")
            print("2. Find 'Remote MySQL' section")
            print("3. Add this IP to whitelist: 142.115.175.25")
            print("4. Or use '%' for all IPs (less secure)")
            print("5. Run this test again")
        elif "Can't connect" in str(e):
            print("\nSOLUTION:")
            print("1. Check your internet connection")
            print("2. Verify the hostname: kbz.rew.mybluehost.me")
            print("3. Check if MySQL service is running on Bluehost")
        else:
            print(f"\nOther error: {e}")
            
        return False
        
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_bluehost_with_correct_credentials()
    
    if success:
        print("\nNext steps:")
        print("1. Update your MQTT subscriber to use correct credentials")
        print("2. Update database.py with correct username")
        print("3. Start collecting sensor data in Bluehost!")
    else:
        print("\nPlease fix the connection issue first!")
        print("Most likely you need to add your IP to Remote MySQL whitelist.")
