#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import Error
import socket

def get_public_ip():
    """Get your public IP address"""
    try:
        # Connect to a service that returns your public IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Get public IP
        import urllib.request
        public_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
        return local_ip, public_ip
    except:
        return "Unknown", "Unknown"

def test_bluehost_connection_with_different_configs():
    """Test Bluehost connection with different configurations"""
    
    print("=== Bluehost MySQL Connection Troubleshooting ===")
    
    # Get IP information
    local_ip, public_ip = get_public_ip()
    print(f"Local IP: {local_ip}")
    print(f"Public IP: {public_ip}")
    print(f"Hostname: {socket.gethostname()}")
    
    # Base configuration
    base_config = {
        'host': 'kbz.rew.mybluehost.me',
        'database': 'kbzrewmy_sensor',
        'user': 'mo_kerma',
        'password': 'Mehrafarid.5435',
        'port': 3306,
        'charset': 'utf8mb4',
        'autocommit': True
    }
    
    # Test different configurations
    configs_to_test = [
        {
            'name': 'Standard Configuration',
            'config': base_config
        },
        {
            'name': 'With SSL',
            'config': {**base_config, 'ssl_disabled': False, 'ssl_verify_cert': False}
        },
        {
            'name': 'With Connection Timeout',
            'config': {**base_config, 'connection_timeout': 30, 'autocommit': True}
        },
        {
            'name': 'With Different Port (3307)',
            'config': {**base_config, 'port': 3307}
        },
        {
            'name': 'With Different Port (3308)',
            'config': {**base_config, 'port': 3308}
        }
    ]
    
    for test_config in configs_to_test:
        print(f"\n--- Testing: {test_config['name']} ---")
        try:
            connection = mysql.connector.connect(**test_config['config'])
            if connection.is_connected():
                print("SUCCESS: Connection established!")
                
                # Test basic operations
                cursor = connection.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"MySQL Version: {version[0]}")
                
                cursor.execute("SELECT DATABASE()")
                db_name = cursor.fetchone()
                print(f"Connected to database: {db_name[0]}")
                
                # Check if sensor_data table exists
                cursor.execute("SHOW TABLES LIKE 'sensor_data'")
                table_exists = cursor.fetchone()
                if table_exists:
                    print("Table 'sensor_data' exists!")
                    
                    # Count records
                    cursor.execute("SELECT COUNT(*) FROM sensor_data")
                    count = cursor.fetchone()[0]
                    print(f"Records in sensor_data: {count}")
                else:
                    print("Table 'sensor_data' does not exist - will create it")
                
                cursor.close()
                connection.close()
                return test_config['config']
                
        except Error as e:
            print(f"FAILED: {e}")
            if "Access denied" in str(e):
                print("  -> This is an IP whitelist issue")
            elif "Can't connect" in str(e):
                print("  -> This is a network/port issue")
            else:
                print(f"  -> Other error: {e}")
        except Exception as e:
            print(f"FAILED: {e}")
    
    return None

def create_bluehost_database_manager():
    """Create a database manager that only uses Bluehost"""
    
    print("\n=== Creating Bluehost-Only Database Manager ===")
    
    # Test connection first
    working_config = test_bluehost_connection_with_different_configs()
    
    if not working_config:
        print("\n❌ No working configuration found!")
        print("\n🔧 SOLUTIONS:")
        print("1. Go to Bluehost cPanel → Remote MySQL")
        print("2. Add your IP to whitelist:")
        print(f"   - Your public IP: {get_public_ip()[1]}")
        print("   - Or use '%' for all IPs (less secure)")
        print("3. Make sure database 'kbzrewmy_sensor' exists")
        print("4. Verify user 'mo_kerma' has proper permissions")
        return None
    
    print(f"\n✅ Working configuration found!")
    
    # Create a Bluehost-only database manager
    class BluehostOnlyManager:
        def __init__(self, config):
            self.config = config
            self.connection = None
            
        def connect(self):
            try:
                self.connection = mysql.connector.connect(**self.config)
                return True
            except Exception as e:
                print(f"Connection failed: {e}")
                return False
                
        def create_table(self):
            if not self.connection:
                return False
                
            cursor = self.connection.cursor()
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
            self.connection.commit()
            cursor.close()
            return True
            
        def save_sensor_data(self, data_dict):
            if not self.connection:
                return False
                
            try:
                cursor = self.connection.cursor()
                
                # Parse timestamp
                from datetime import datetime
                timestamp = datetime.fromtimestamp(data_dict.get('ts', 0) / 1000)
                
                insert_sql = """
                INSERT INTO sensor_data 
                (device_id, kind, room_id, value, unit, power_w, voltage, current, on_status, timestamp, raw_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                import json
                data = (
                    data_dict.get('deviceId', ''),
                    data_dict.get('kind', ''),
                    data_dict.get('roomId'),
                    data_dict.get('value'),
                    data_dict.get('unit'),
                    data_dict.get('powerW'),
                    data_dict.get('voltage'),
                    data_dict.get('current'),
                    data_dict.get('on'),
                    timestamp,
                    json.dumps(data_dict)
                )
                
                cursor.execute(insert_sql, data)
                self.connection.commit()
                cursor.close()
                return True
                
            except Exception as e:
                print(f"Error saving data: {e}")
                return False
                
        def get_recent_data(self, limit=100):
            if not self.connection:
                return []
                
            try:
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute("""
                    SELECT * FROM sensor_data 
                    ORDER BY timestamp DESC 
                    LIMIT %s
                """, (limit,))
                results = cursor.fetchall()
                cursor.close()
                return results
            except Exception as e:
                print(f"Error retrieving data: {e}")
                return []
                
        def close(self):
            if self.connection:
                self.connection.close()
    
    # Create and test the manager
    manager = BluehostOnlyManager(working_config)
    if manager.connect():
        print("✅ Bluehost database manager created successfully!")
        if manager.create_table():
            print("✅ Table 'sensor_data' created/verified!")
        return manager
    else:
        print("❌ Failed to create Bluehost database manager")
        return None

if __name__ == "__main__":
    manager = create_bluehost_database_manager()
    
    if manager:
        print("\n🎉 SUCCESS! You can now use Bluehost MySQL database!")
        print("\nTo use this in your MQTT subscriber:")
        print("1. Replace the database import in mqtt_subscriber.py")
        print("2. Use this Bluehost-only manager")
        print("3. No more SQLite fallback!")
        
        # Test saving sample data
        print("\nTesting data save...")
        sample_data = {
            "deviceId": "test-device",
            "kind": "temperature",
            "roomId": "test-room",
            "ts": 1703123456789,
            "value": 25.5,
            "unit": "C"
        }
        
        if manager.save_sensor_data(sample_data):
            print("✅ Sample data saved successfully!")
            
            # Show recent data
            recent = manager.get_recent_data(5)
            print(f"Recent records: {len(recent)}")
            for record in recent:
                print(f"  - {record['device_id']} ({record['kind']}): {record['value']} {record['unit'] or ''}")
        else:
            print("❌ Failed to save sample data")
            
        manager.close()
    else:
        print("\n❌ Please fix the Bluehost connection issues first!")
        print("Check the solutions above and try again.")
