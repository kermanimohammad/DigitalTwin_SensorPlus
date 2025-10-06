#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime

def migrate_sqlite_to_bluehost():
    """Migrate data from SQLite to Bluehost MySQL"""
    
    print("=== Migrating Data from SQLite to Bluehost MySQL ===")
    
    # Bluehost configuration
    bluehost_config = {
        'host': 'kbz.rew.mybluehost.me',
        'database': 'kbzrewmy_sensor',
        'user': 'mo_kerma',
        'password': 'Mehrafarid.5435',
        'port': 3306,
        'charset': 'utf8mb4',
        'autocommit': True
    }
    
    try:
        # Connect to SQLite
        print("1. Connecting to SQLite database...")
        sqlite_conn = sqlite3.connect('sensor_data.db')
        sqlite_cursor = sqlite_conn.cursor()
        
        # Get all records from SQLite
        sqlite_cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp")
        records = sqlite_cursor.fetchall()
        print(f"   Found {len(records)} records in SQLite")
        
        # Connect to Bluehost MySQL
        print("2. Connecting to Bluehost MySQL...")
        mysql_conn = mysql.connector.connect(**bluehost_config)
        mysql_cursor = mysql_conn.cursor()
        
        # Create table if not exists
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
        mysql_cursor.execute(create_table_sql)
        print("   Table created/verified in Bluehost MySQL")
        
        # Insert data
        print("3. Migrating data...")
        insert_sql = """
        INSERT INTO sensor_data 
        (device_id, kind, room_id, value, unit, power_w, voltage, current, on_status, timestamp, raw_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        migrated_count = 0
        for record in records:
            try:
                # Skip id field (auto-increment)
                data = record[1:]  # Remove first field (id)
                mysql_cursor.execute(insert_sql, data)
                migrated_count += 1
                
                if migrated_count % 100 == 0:
                    print(f"   Migrated {migrated_count} records...")
                    
            except Exception as e:
                print(f"   Error migrating record {record[0]}: {e}")
                continue
        
        mysql_conn.commit()
        print(f"   Successfully migrated {migrated_count} records to Bluehost MySQL")
        
        # Verify migration
        print("4. Verifying migration...")
        mysql_cursor.execute("SELECT COUNT(*) FROM sensor_data")
        mysql_count = mysql_cursor.fetchone()[0]
        print(f"   Bluehost MySQL now has {mysql_count} records")
        
        # Show sample data
        mysql_cursor.execute("SELECT device_id, kind, value, unit, timestamp FROM sensor_data ORDER BY timestamp DESC LIMIT 5")
        sample_records = mysql_cursor.fetchall()
        print("\n   Sample records in Bluehost MySQL:")
        for record in sample_records:
            print(f"     - {record[0]} ({record[1]}): {record[2]} {record[3] or ''} at {record[4]}")
        
        # Close connections
        sqlite_cursor.close()
        sqlite_conn.close()
        mysql_cursor.close()
        mysql_conn.close()
        
        print("\n=== Migration Completed Successfully ===")
        return True
        
    except Error as e:
        print(f"ERROR: Bluehost MySQL connection failed: {e}")
        print("\nPlease check:")
        print("1. IP is whitelisted in Bluehost cPanel")
        print("2. Database credentials are correct")
        print("3. Database exists")
        return False
        
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        return False

def test_bluehost_after_migration():
    """Test Bluehost connection after migration"""
    print("\n=== Testing Bluehost Connection After Migration ===")
    
    try:
        config = {
            'host': 'kbz.rew.mybluehost.me',
            'database': 'kbzrewmy_sensor',
            'user': 'mo_kerma',
            'password': 'Mehrafarid.5435',
            'port': 3306
        }
        
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Test queries
        cursor.execute("SELECT COUNT(*) FROM sensor_data")
        count = cursor.fetchone()[0]
        print(f"Total records: {count}")
        
        cursor.execute("SELECT DISTINCT kind FROM sensor_data")
        sensor_types = cursor.fetchall()
        print(f"Sensor types: {[t[0] for t in sensor_types]}")
        
        cursor.execute("SELECT DISTINCT device_id FROM sensor_data")
        devices = cursor.fetchall()
        print(f"Devices: {[d[0] for d in devices]}")
        
        cursor.close()
        connection.close()
        
        print("Bluehost connection test successful!")
        return True
        
    except Exception as e:
        print(f"Bluehost connection test failed: {e}")
        return False

if __name__ == "__main__":
    # First try to migrate
    if migrate_sqlite_to_bluehost():
        # Then test the connection
        test_bluehost_after_migration()
    else:
        print("\nMigration failed. Please check Bluehost setup guide.")
        print("File: BLUEHOST_SETUP_GUIDE.md")
