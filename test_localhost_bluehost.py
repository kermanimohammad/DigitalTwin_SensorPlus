#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import Error

def test_localhost_connection():
    """Test connection using localhost (most common for Bluehost)"""
    
    print("=== Testing Bluehost with localhost ===")
    print("This is the most common hostname for Bluehost databases")
    print("=" * 50)
    
    config = {
        'host': 'localhost',
        'database': 'kbzrewmy_sensor',
        'user': 'mo_kerma',
        'password': 'Mehrafarid.5435',
        'port': 3306,
        'charset': 'utf8mb4',
        'autocommit': True
    }
    
    try:
        print("Connecting to localhost...")
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            print("SUCCESS: Connected to Bluehost MySQL via localhost!")
            
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"MySQL Version: {version[0]}")
            
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()
            print(f"Connected to database: {db_name[0]}")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"ERROR: {e}")
        
        if "Access denied" in str(e):
            print("\nSOLUTION:")
            print("1. Go to cPanel -> Remote MySQL")
            print("2. Add IP: 142.115.175.25")
            print("3. Or add: % (for all IPs)")
            print("4. Run this test again")
        elif "Can't connect" in str(e):
            print("\nSOLUTION:")
            print("1. Check if you're running this on the Bluehost server")
            print("2. If not, use the external hostname instead")
            print("3. Try: kbz.rew.mybluehost.me")
            
        return False

if __name__ == "__main__":
    success = test_localhost_connection()
    
    if not success:
        print("\nNext steps:")
        print("1. First add your IP to Remote MySQL in cPanel")
        print("2. Then try this test again")
        print("3. If still fails, check the database name and credentials")
