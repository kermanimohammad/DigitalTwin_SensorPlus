#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import Error

def cleanup_old_tables():
    """Remove old sensor_data table and keep only separate tables"""
    
    print("=== Cleaning up old tables ===")
    
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
        
        # Show current tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\nCurrent tables: {[table[0] for table in tables]}")
        
        # Check if old sensor_data table exists
        cursor.execute("SHOW TABLES LIKE 'sensor_data'")
        old_table_exists = cursor.fetchone()
        
        if old_table_exists:
            print("\nFound old 'sensor_data' table")
            
            # Get count of records in old table
            cursor.execute("SELECT COUNT(*) FROM sensor_data")
            old_count = cursor.fetchone()[0]
            print(f"Old table has {old_count} records")
            
            # Ask for confirmation (in real scenario)
            print("\nThe old 'sensor_data' table will be dropped.")
            print("Make sure you have backed up any important data!")
            
            # Drop the old table
            cursor.execute("DROP TABLE sensor_data")
            print("SUCCESS: Old 'sensor_data' table dropped successfully!")
        else:
            print("\nNo old 'sensor_data' table found")
        
        # Show remaining tables
        cursor.execute("SHOW TABLES")
        remaining_tables = cursor.fetchall()
        print(f"\nRemaining tables: {[table[0] for table in remaining_tables]}")
        
        # Show counts for each separate table
        print("\nRecord counts in separate tables:")
        
        separate_tables = [
            'temperature_data',
            'humidity_data', 
            'co2_data',
            'light_data',
            'solar_data'
        ]
        
        for table in separate_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} records")
            except Error as e:
                print(f"  {table}: Error - {e}")
        
        cursor.close()
        connection.close()
        
        print("\n" + "="*50)
        print("SUCCESS: Database cleanup completed successfully!")
        print("Now using only separate tables for each sensor type.")
        print("="*50)
        
        return True
        
    except Error as e:
        print(f"ERROR: Error during cleanup: {e}")
        return False

def show_final_database_structure():
    """Show the final clean database structure"""
    
    print("\n=== Final Database Structure ===")
    
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
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Show all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"Total tables: {len(tables)}")
        print("\nTable structure:")
        
        for table in tables:
            table_name = table[0]
            print(f"\n--- {table_name} ---")
            
            # Get table structure
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            for col in columns:
                col_name, col_type, null, key, default, extra = col
                print(f"  {col_name}: {col_type} {'(NOT NULL)' if null == 'NO' else ''} {'(PRIMARY KEY)' if key == 'PRI' else ''}")
            
            # Get record count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  Records: {count}")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error showing database structure: {e}")

if __name__ == "__main__":
    # Clean up old tables
    if cleanup_old_tables():
        # Show final structure
        show_final_database_structure()
        
        print("\nSUCCESS: Database is now clean and optimized!")
        print("Only separate tables for each sensor type remain.")
        print("\nNext steps:")
        print("1. Use mqtt_subscriber_separate_tables.py for data collection")
        print("2. Use sensor_api_separate_tables.py for API access")
        print("3. Old files can be removed or archived")
    else:
        print("ERROR: Cleanup failed. Please check the error messages above.")
