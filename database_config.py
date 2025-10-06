#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from database import DatabaseManager

class BluehostDatabaseManager(DatabaseManager):
    """Database manager specifically configured for Bluehost"""
    
    def __init__(self, force_bluehost=False):
        self.force_bluehost = force_bluehost
        super().__init__()
    
    def connect(self):
        """Create database connection with Bluehost-specific settings"""
        try:
            if self.force_bluehost:
                # Force Bluehost connection
                connection_string = "mysql+mysqlconnector://mo_kerma:Mehrafarid.5435@kbz.rew.mybluehost.me:3306/kbzrewmy_sensor?charset=utf8mb4"
                print("[DB] Forcing Bluehost connection...")
            else:
                # Use environment variables or fallback to SQLite
                if USE_SQLITE:
                    connection_string = "sqlite:///sensor_data.db"
                    print("[DB] Using SQLite for local testing")
                else:
                    connection_string = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
                    print(f"[DB] Connecting to MySQL: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
            
            self.engine = create_engine(connection_string, echo=False)
            self.Session = sessionmaker(bind=self.engine)
            Base.metadata.create_all(self.engine)
            
            if self.force_bluehost:
                print(f"[DB] Connected to Bluehost MySQL: kbzrewmy_sensor")
            elif USE_SQLITE:
                print(f"[DB] Connected to SQLite: sensor_data.db")
            else:
                print(f"[DB] Connected to MySQL: {DB_CONFIG['database']}")
            
        except Exception as e:
            print(f"[DB] Error connecting to database: {e}")
            if not self.force_bluehost and not USE_SQLITE:
                print("[DB] Falling back to SQLite for local testing...")
                self._fallback_to_sqlite()
            else:
                raise

def test_connection_options():
    """Test different connection options"""
    print("=== Testing Database Connection Options ===")
    
    # Test 1: SQLite (should always work)
    print("\n1. Testing SQLite connection...")
    try:
        os.environ['USE_SQLITE'] = 'true'
        from database import db_manager
        if db_manager.test_connection():
            print("   SUCCESS: SQLite connection successful")
        else:
            print("   FAILED: SQLite connection failed")
    except Exception as e:
        print(f"   ERROR: SQLite error: {e}")
    
    # Test 2: Bluehost MySQL
    print("\n2. Testing Bluehost MySQL connection...")
    try:
        os.environ['USE_SQLITE'] = 'false'
        bluehost_db = BluehostDatabaseManager(force_bluehost=True)
        if bluehost_db.test_connection():
            print("   SUCCESS: Bluehost MySQL connection successful")
            return bluehost_db
        else:
            print("   FAILED: Bluehost MySQL connection failed")
    except Exception as e:
        print(f"   ERROR: Bluehost MySQL error: {e}")
    
    # Test 3: Fallback to SQLite
    print("\n3. Using SQLite fallback...")
    try:
        os.environ['USE_SQLITE'] = 'true'
        from database import db_manager
        if db_manager.test_connection():
            print("   SUCCESS: SQLite fallback successful")
            return db_manager
    except Exception as e:
        print(f"   ERROR: SQLite fallback error: {e}")
    
    return None

if __name__ == "__main__":
    # Import required modules
    from database import USE_SQLITE, DB_CONFIG, Base, create_engine, sessionmaker
    
    # Test all connection options
    db_manager = test_connection_options()
    
    if db_manager:
        print("\n=== Database Ready ===")
        print("You can now use the database manager for storing sensor data.")
    else:
        print("\n=== Database Setup Failed ===")
        print("Please check the Bluehost setup guide: BLUEHOST_SETUP_GUIDE.md")
