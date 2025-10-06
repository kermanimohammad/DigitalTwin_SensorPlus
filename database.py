#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# Database configuration - can be overridden by environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'kbz.rew.mybluehost.me'),
    'database': os.getenv('DB_NAME', 'kbzrewmy_sensor'),
    'user': os.getenv('DB_USER', 'kbzrewmy_mo_kerma'),  # Correct username
    'password': os.getenv('DB_PASSWORD', 'Mehrafarid.5435'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'charset': 'utf8mb4',
    'autocommit': True
}

# Use SQLite for local testing if MySQL is not available
USE_SQLITE = os.getenv('USE_SQLITE', 'false').lower() == 'true'

Base = declarative_base()

class SensorData(Base):
    __tablename__ = 'sensor_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), nullable=False, index=True)
    kind = Column(String(20), nullable=False, index=True)  # temperature, humidity, co2, light, solar
    room_id = Column(String(20), nullable=True, index=True)
    value = Column(Float, nullable=True)
    unit = Column(String(10), nullable=True)
    power_w = Column(Float, nullable=True)
    voltage = Column(Float, nullable=True)
    current = Column(Float, nullable=True)
    on_status = Column(Boolean, nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    raw_data = Column(Text, nullable=True)  # Store complete JSON payload
    
    def __repr__(self):
        return f"<SensorData(device_id='{self.device_id}', kind='{self.kind}', value={self.value}, timestamp='{self.timestamp}')>"

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.Session = None
        self.connect()
    
    def connect(self):
        """Create database connection and session"""
        try:
            if USE_SQLITE:
                # Use SQLite for local testing
                connection_string = "sqlite:///sensor_data.db"
                print("[DB] Using SQLite for local testing")
            else:
                # Create SQLAlchemy engine for MySQL
                connection_string = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
                print(f"[DB] Connecting to MySQL: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
            
            self.engine = create_engine(connection_string, echo=False)
            
            # Create session factory
            self.Session = sessionmaker(bind=self.engine)
            
            # Create tables if they don't exist
            Base.metadata.create_all(self.engine)
            
            if USE_SQLITE:
                print(f"[DB] Connected to SQLite database: sensor_data.db")
            else:
                print(f"[DB] Connected to MySQL database: {DB_CONFIG['database']}")
            
        except Exception as e:
            print(f"[DB] Error connecting to database: {e}")
            if not USE_SQLITE:
                print("[DB] Falling back to SQLite for local testing...")
                self._fallback_to_sqlite()
            else:
                raise
    
    def _fallback_to_sqlite(self):
        """Fallback to SQLite if MySQL connection fails"""
        try:
            connection_string = "sqlite:///sensor_data.db"
            self.engine = create_engine(connection_string, echo=False)
            self.Session = sessionmaker(bind=self.engine)
            Base.metadata.create_all(self.engine)
            print(f"[DB] Fallback: Connected to SQLite database: sensor_data.db")
        except Exception as e:
            print(f"[DB] Fallback to SQLite also failed: {e}")
            raise
    
    def get_session(self):
        """Get a new database session"""
        return self.Session()
    
    def save_sensor_data(self, data_dict):
        """Save sensor data to database"""
        session = self.get_session()
        try:
            # Parse timestamp
            timestamp = datetime.fromtimestamp(data_dict.get('ts', 0) / 1000)
            
            # Create sensor data record
            sensor_data = SensorData(
                device_id=data_dict.get('deviceId', ''),
                kind=data_dict.get('kind', ''),
                room_id=data_dict.get('roomId'),
                value=data_dict.get('value'),
                unit=data_dict.get('unit'),
                power_w=data_dict.get('powerW'),
                voltage=data_dict.get('voltage'),
                current=data_dict.get('current'),
                on_status=data_dict.get('on'),
                timestamp=timestamp,
                raw_data=json.dumps(data_dict)
            )
            
            session.add(sensor_data)
            session.commit()
            print(f"[DB] Saved {sensor_data.kind} data for device {sensor_data.device_id}")
            return True
            
        except Exception as e:
            session.rollback()
            print(f"[DB] Error saving sensor data: {e}")
            return False
        finally:
            session.close()
    
    def get_recent_data(self, device_id=None, kind=None, limit=100):
        """Get recent sensor data"""
        session = self.get_session()
        try:
            query = session.query(SensorData)
            
            if device_id:
                query = query.filter(SensorData.device_id == device_id)
            if kind:
                query = query.filter(SensorData.kind == kind)
            
            results = query.order_by(SensorData.timestamp.desc()).limit(limit).all()
            return results
            
        except Exception as e:
            print(f"[DB] Error retrieving data: {e}")
            return []
        finally:
            session.close()
    
    def get_room_data(self, room_id, limit=50):
        """Get data for a specific room"""
        session = self.get_session()
        try:
            results = session.query(SensorData).filter(
                SensorData.room_id == room_id
            ).order_by(SensorData.timestamp.desc()).limit(limit).all()
            return results
            
        except Exception as e:
            print(f"[DB] Error retrieving room data: {e}")
            return []
        finally:
            session.close()
    
    def test_connection(self):
        """Test database connection"""
        try:
            from sqlalchemy import text
            session = self.get_session()
            session.execute(text("SELECT 1"))
            session.close()
            print("[DB] Connection test successful")
            return True
        except Exception as e:
            print(f"[DB] Connection test failed: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()

if __name__ == "__main__":
    # Test the database connection
    db = DatabaseManager()
    if db.test_connection():
        print("Database setup completed successfully!")
    else:
        print("Database setup failed!")
