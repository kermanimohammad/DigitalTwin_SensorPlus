#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to create separate tables for different sensor types
"""

import sys
import os
from sqlalchemy import create_engine, text

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DB_CONFIG, USE_SQLITE

def create_separate_tables():
    """Create separate tables for each sensor type"""
    print("=" * 60)
    print("Creating Separate Sensor Tables")
    print("=" * 60)
    
    try:
        if USE_SQLITE:
            # Use SQLite for local testing
            connection_string = "sqlite:///sensor_data.db"
            print("[DB] Using SQLite for local testing")
        else:
            # Create SQLAlchemy engine for MySQL
            connection_string = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
            print(f"[DB] Connecting to MySQL: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
        
        engine = create_engine(connection_string, echo=False)
        
        # Create tables
        tables_to_create = [
            {
                'name': 'temperature_data',
                'sql': '''
                CREATE TABLE IF NOT EXISTS temperature_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id VARCHAR(50) NOT NULL,
                    room_id VARCHAR(20),
                    value FLOAT,
                    unit VARCHAR(10),
                    timestamp DATETIME NOT NULL,
                    raw_data TEXT,
                    INDEX idx_device_id (device_id),
                    INDEX idx_room_id (room_id),
                    INDEX idx_timestamp (timestamp)
                )
                '''
            },
            {
                'name': 'humidity_data',
                'sql': '''
                CREATE TABLE IF NOT EXISTS humidity_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id VARCHAR(50) NOT NULL,
                    room_id VARCHAR(20),
                    value FLOAT,
                    unit VARCHAR(10),
                    timestamp DATETIME NOT NULL,
                    raw_data TEXT,
                    INDEX idx_device_id (device_id),
                    INDEX idx_room_id (room_id),
                    INDEX idx_timestamp (timestamp)
                )
                '''
            },
            {
                'name': 'co2_data',
                'sql': '''
                CREATE TABLE IF NOT EXISTS co2_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id VARCHAR(50) NOT NULL,
                    room_id VARCHAR(20),
                    value FLOAT,
                    unit VARCHAR(10),
                    timestamp DATETIME NOT NULL,
                    raw_data TEXT,
                    INDEX idx_device_id (device_id),
                    INDEX idx_room_id (room_id),
                    INDEX idx_timestamp (timestamp)
                )
                '''
            },
            {
                'name': 'light_data',
                'sql': '''
                CREATE TABLE IF NOT EXISTS light_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id VARCHAR(50) NOT NULL,
                    room_id VARCHAR(20),
                    value FLOAT,
                    unit VARCHAR(10),
                    timestamp DATETIME NOT NULL,
                    raw_data TEXT,
                    INDEX idx_device_id (device_id),
                    INDEX idx_room_id (room_id),
                    INDEX idx_timestamp (timestamp)
                )
                '''
            },
            {
                'name': 'solar_data',
                'sql': '''
                CREATE TABLE IF NOT EXISTS solar_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id VARCHAR(50) NOT NULL,
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
                    INDEX idx_room_id (room_id),
                    INDEX idx_timestamp (timestamp)
                )
                '''
            }
        ]
        
        with engine.connect() as connection:
            for table in tables_to_create:
                try:
                    print(f"\nCreating table: {table['name']}")
                    connection.execute(text(table['sql']))
                    connection.commit()
                    print(f"✅ Table {table['name']} created successfully!")
                except Exception as e:
                    print(f"❌ Error creating table {table['name']}: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Separate tables creation completed!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    create_separate_tables()
