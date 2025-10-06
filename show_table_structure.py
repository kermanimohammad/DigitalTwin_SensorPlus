#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
from database import db_manager

def show_table_structure():
    """Show sensor_data table structure"""
    print("=== sensor_data Table Structure ===")
    
    # Show table structure from SQLite
    try:
        conn = sqlite3.connect('sensor_data.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(sensor_data)")
        columns = cursor.fetchall()
        
        print("\nTable Fields:")
        for col in columns:
            col_id, name, data_type, not_null, default, pk = col
            print(f"  {name}: {data_type} {'(NOT NULL)' if not_null else ''} {'(PRIMARY KEY)' if pk else ''}")
        
        conn.close()
    except Exception as e:
        print(f"Error showing table structure: {e}")
    
    # Show data statistics
    print("\n=== Data Statistics ===")
    try:
        records = db_manager.get_recent_data(limit=1000)
        print(f"Total records: {len(records)}")
        
        # Group by sensor type
        sensor_types = {}
        for record in records:
            kind = record.kind
            sensor_types[kind] = sensor_types.get(kind, 0) + 1
        
        print("\nRecords by sensor type:")
        for kind, count in sensor_types.items():
            print(f"  {kind}: {count} records")
        
        # Show last 5 records
        print("\nLast 5 records:")
        for record in records[:5]:
            print(f"  - {record.device_id} ({record.kind}): {record.value} {record.unit or ''} at {record.timestamp}")
            
    except Exception as e:
        print(f"Error showing statistics: {e}")

if __name__ == "__main__":
    show_table_structure()
