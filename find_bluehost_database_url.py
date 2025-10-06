#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import Error

def test_different_bluehost_urls():
    """Test different possible Bluehost database URLs"""
    
    print("=== Testing Different Bluehost Database URLs ===")
    
    # Different possible hostnames for Bluehost
    possible_hosts = [
        'localhost',  # If running on same server
        'kbz.rew.mybluehost.me',  # Your current URL
        'mysql.kbz.rew.mybluehost.me',  # Common MySQL subdomain
        'db.kbz.rew.mybluehost.me',  # Common database subdomain
        'kbzrewmy.mysql.bluehost.com',  # Bluehost MySQL format
        'mysql.bluehost.com',  # General Bluehost MySQL
        'localhost:3306',  # With port
        '127.0.0.1',  # Local IP
    ]
    
    # Database configuration
    base_config = {
        'database': 'kbzrewmy_sensor',
        'user': 'mo_kerma',
        'password': 'Mehrafarid.5435',
        'port': 3306,
        'charset': 'utf8mb4',
        'autocommit': True
    }
    
    successful_connections = []
    
    for host in possible_hosts:
        print(f"\n--- Testing host: {host} ---")
        
        config = {**base_config, 'host': host}
        
        try:
            connection = mysql.connector.connect(**config)
            if connection.is_connected():
                print(f"SUCCESS: Connected to {host}!")
                
                cursor = connection.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"MySQL Version: {version[0]}")
                
                cursor.execute("SELECT DATABASE()")
                db_name = cursor.fetchone()
                print(f"Connected to database: {db_name[0]}")
                
                # Test if we can create tables
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print(f"Existing tables: {[table[0] for table in tables]}")
                
                cursor.close()
                connection.close()
                
                successful_connections.append(host)
                
        except Error as e:
            print(f"FAILED: {e}")
        except Exception as e:
            print(f"FAILED: {e}")
    
    return successful_connections

def check_bluehost_cpanel_info():
    """Guide to find correct database info from cPanel"""
    
    print("\n" + "="*60)
    print("HOW TO FIND CORRECT DATABASE INFO IN BLUEHOST CPANEL")
    print("="*60)
    
    print("\n1. Go to cPanel → MySQL Databases")
    print("   - Look for 'Current Databases' section")
    print("   - Find your database: kbzrewmy_sensor")
    
    print("\n2. Go to cPanel → MySQL Users")
    print("   - Look for user: mo_kerma")
    print("   - Check if password is correct")
    
    print("\n3. Go to cPanel → Remote MySQL")
    print("   - Add your IP: 142.115.175.25")
    print("   - Or use: % (for all IPs)")
    
    print("\n4. Check cPanel → phpMyAdmin")
    print("   - Try to login with:")
    print("     Username: mo_kerma")
    print("     Password: Mehrafarid.5435")
    print("     Server: localhost (usually)")
    
    print("\n5. Common Bluehost database hostnames:")
    print("   - localhost (if on same server)")
    print("   - yourdomain.com")
    print("   - mysql.yourdomain.com")
    print("   - yourusername.mysql.bluehost.com")
    
    print("\n6. Check your domain settings:")
    print("   - Your domain: kbz.rew.mybluehost.me")
    print("   - Try: mysql.kbz.rew.mybluehost.me")
    print("   - Try: db.kbz.rew.mybluehost.me")

def create_connection_test_script(successful_hosts):
    """Create a script to test the successful connections"""
    
    if not successful_hosts:
        print("\nNo successful connections found.")
        return
    
    print(f"\n=== Creating test script for successful hosts ===")
    
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime

def test_bluehost_connection():
    """Test connection to Bluehost MySQL with correct hostname"""
    
    # Successful hosts from testing
    successful_hosts = ''' + str(successful_hosts) + '''
    
    config = {
        'host': successful_hosts[0],  # Use first successful host
        'database': 'kbzrewmy_sensor',
        'user': 'mo_kerma',
        'password': 'Mehrafarid.5435',
        'port': 3306,
        'charset': 'utf8mb4',
        'autocommit': True
    }
    
    print(f"Testing connection to: {config['host']}")
    
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print("SUCCESS: Connected to Bluehost MySQL!")
            
            cursor = connection.cursor()
            
            # Create sensor_data table
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
            print("Table 'sensor_data' created successfully!")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_bluehost_connection()
'''
    
    with open('test_correct_bluehost.py', 'w') as f:
        f.write(script_content)
    
    print(f"Created test_correct_bluehost.py with successful host: {successful_hosts[0]}")

if __name__ == "__main__":
    # Test different URLs
    successful_hosts = test_different_bluehost_urls()
    
    # Show guide
    check_bluehost_cpanel_info()
    
    # Create test script if successful
    if successful_hosts:
        create_connection_test_script(successful_hosts)
        print(f"\n✅ Found working host: {successful_hosts[0]}")
        print("Run: python test_correct_bluehost.py")
    else:
        print("\n❌ No working hosts found.")
        print("Please check the cPanel guide above and verify:")
        print("1. Database name: kbzrewmy_sensor")
        print("2. Username: mo_kerma")
        print("3. Password: Mehrafarid.5435")
        print("4. IP whitelist in Remote MySQL")
