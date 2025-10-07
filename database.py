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

# Separate tables for each sensor type - matching actual database structure
class TemperatureData(Base):
    __tablename__ = 'temperature_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), nullable=False, index=True)
    room_id = Column(String(20), nullable=True, index=True)
    temperature_c = Column(Float, nullable=True)  # Actual column name in DB
    timestamp = Column(DateTime, nullable=False, index=True)
    raw_data = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<TemperatureData(device_id='{self.device_id}', temperature_c={self.temperature_c}, timestamp='{self.timestamp}')>"

class HumidityData(Base):
    __tablename__ = 'humidity_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), nullable=False, index=True)
    room_id = Column(String(20), nullable=True, index=True)
    humidity_percent = Column(Float, nullable=True)  # Actual column name in DB
    timestamp = Column(DateTime, nullable=False, index=True)
    raw_data = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<HumidityData(device_id='{self.device_id}', humidity_percent={self.humidity_percent}, timestamp='{self.timestamp}')>"

class CO2Data(Base):
    __tablename__ = 'co2_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), nullable=False, index=True)
    room_id = Column(String(20), nullable=True, index=True)
    co2_ppm = Column(Integer, nullable=True)  # Actual column name in DB
    timestamp = Column(DateTime, nullable=False, index=True)
    raw_data = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<CO2Data(device_id='{self.device_id}', co2_ppm={self.co2_ppm}, timestamp='{self.timestamp}')>"

class LightData(Base):
    __tablename__ = 'light_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), nullable=False, index=True)
    room_id = Column(String(20), nullable=True, index=True)
    is_on = Column(Boolean, nullable=True)  # Actual column name in DB
    power_watts = Column(Float, nullable=True)  # Actual column name in DB
    timestamp = Column(DateTime, nullable=False, index=True)
    raw_data = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<LightData(device_id='{self.device_id}', is_on={self.is_on}, power_watts={self.power_watts}, timestamp='{self.timestamp}')>"

class SolarData(Base):
    __tablename__ = 'solar_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), nullable=False, index=True)
    power_watts = Column(Float, nullable=True)  # Actual column name in DB
    voltage_volts = Column(Float, nullable=True)  # Actual column name in DB
    current_amps = Column(Float, nullable=True)  # Actual column name in DB
    timestamp = Column(DateTime, nullable=False, index=True)
    raw_data = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<SolarData(device_id='{self.device_id}', power_watts={self.power_watts}, timestamp='{self.timestamp}')>"

# Legacy table for backward compatibility
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
        """Save sensor data to appropriate table based on sensor type"""
        session = self.get_session()
        try:
            # Parse timestamp
            timestamp = datetime.fromtimestamp(data_dict.get('ts', 0) / 1000)
            
            # Get sensor type
            kind = data_dict.get('kind', '').lower()
            
            # Create appropriate sensor data record based on type
            if kind == 'temperature':
                sensor_data = TemperatureData(
                    device_id=data_dict.get('deviceId', ''),
                    room_id=data_dict.get('roomId'),
                    temperature_c=data_dict.get('value'),  # Use actual column name
                    timestamp=timestamp,
                    raw_data=json.dumps(data_dict)
                )
            elif kind == 'humidity':
                sensor_data = HumidityData(
                    device_id=data_dict.get('deviceId', ''),
                    room_id=data_dict.get('roomId'),
                    humidity_percent=data_dict.get('value'),  # Use actual column name
                    timestamp=timestamp,
                    raw_data=json.dumps(data_dict)
                )
            elif kind == 'co2':
                sensor_data = CO2Data(
                    device_id=data_dict.get('deviceId', ''),
                    room_id=data_dict.get('roomId'),
                    co2_ppm=int(data_dict.get('value', 0)) if data_dict.get('value') is not None else None,  # Use actual column name
                    timestamp=timestamp,
                    raw_data=json.dumps(data_dict)
                )
            elif kind == 'light':
                sensor_data = LightData(
                    device_id=data_dict.get('deviceId', ''),
                    room_id=data_dict.get('roomId'),
                    is_on=data_dict.get('on'),  # Use actual column name
                    power_watts=data_dict.get('powerW'),  # Use actual column name
                    timestamp=timestamp,
                    raw_data=json.dumps(data_dict)
                )
            elif kind == 'solar':
                sensor_data = SolarData(
                    device_id=data_dict.get('deviceId', ''),
                    power_watts=data_dict.get('powerW'),  # Use actual column name
                    voltage_volts=data_dict.get('voltage'),  # Use actual column name
                    current_amps=data_dict.get('current'),  # Use actual column name
                    timestamp=timestamp,
                    raw_data=json.dumps(data_dict)
                )
            else:
                # Fallback to legacy table for unknown sensor types
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
            print(f"[DB] Saved {kind} data for device {sensor_data.device_id} to {sensor_data.__tablename__}")
            return True
            
        except Exception as e:
            session.rollback()
            print(f"[DB] Error saving sensor data: {e}")
            return False
        finally:
            session.close()
    
    def get_recent_data(self, device_id=None, kind=None, limit=100):
        """Get recent sensor data from appropriate table"""
        session = self.get_session()
        try:
            # Get the appropriate table class based on sensor type
            if kind:
                kind = kind.lower()
                if kind == 'temperature':
                    table_class = TemperatureData
                elif kind == 'humidity':
                    table_class = HumidityData
                elif kind == 'co2':
                    table_class = CO2Data
                elif kind == 'light':
                    table_class = LightData
                elif kind == 'solar':
                    table_class = SolarData
                else:
                    # Fallback to legacy table
                    table_class = SensorData
            else:
                # If no kind specified, search all tables
                return self._get_recent_data_from_all_tables(device_id, limit)
            
            query = session.query(table_class)
            
            if device_id:
                query = query.filter(table_class.device_id == device_id)
            
            results = query.order_by(table_class.timestamp.desc()).limit(limit).all()
            return results
            
        except Exception as e:
            print(f"[DB] Error retrieving data: {e}")
            return []
        finally:
            session.close()
    
    def _get_recent_data_from_all_tables(self, device_id=None, limit=100):
        """Get recent data from all sensor tables"""
        session = self.get_session()
        try:
            all_results = []
            tables = [TemperatureData, HumidityData, CO2Data, LightData, SolarData, SensorData]
            
            for table_class in tables:
                query = session.query(table_class)
                if device_id:
                    query = query.filter(table_class.device_id == device_id)
                
                results = query.order_by(table_class.timestamp.desc()).limit(limit).all()
                all_results.extend(results)
            
            # Sort by timestamp and limit
            all_results.sort(key=lambda x: x.timestamp, reverse=True)
            return all_results[:limit]
            
        except Exception as e:
            print(f"[DB] Error retrieving data from all tables: {e}")
            return []
        finally:
            session.close()
    
    def get_room_data(self, room_id, limit=50):
        """Get data for a specific room from all sensor tables"""
        session = self.get_session()
        try:
            all_results = []
            tables = [TemperatureData, HumidityData, CO2Data, LightData, SolarData, SensorData]
            
            for table_class in tables:
                results = session.query(table_class).filter(
                    table_class.room_id == room_id
                ).order_by(table_class.timestamp.desc()).limit(limit).all()
                all_results.extend(results)
            
            # Sort by timestamp and limit
            all_results.sort(key=lambda x: x.timestamp, reverse=True)
            return all_results[:limit]
            
        except Exception as e:
            print(f"[DB] Error retrieving room data: {e}")
            return []
        finally:
            session.close()
    
    def get_table_statistics(self):
        """Get statistics from all sensor tables"""
        session = self.get_session()
        try:
            stats = {}
            tables = [
                ('temperature', TemperatureData),
                ('humidity', HumidityData),
                ('co2', CO2Data),
                ('light', LightData),
                ('solar', SolarData),
                ('legacy', SensorData)
            ]
            
            for table_name, table_class in tables:
                try:
                    count = session.query(table_class).count()
                    latest = session.query(table_class).order_by(table_class.timestamp.desc()).first()
                    stats[table_name] = {
                        'count': count,
                        'latest_timestamp': latest.timestamp if latest else None,
                        'latest_device': latest.device_id if latest else None
                    }
                except Exception as e:
                    stats[table_name] = {'error': str(e)}
            
            return stats
            
        except Exception as e:
            print(f"[DB] Error getting table statistics: {e}")
            return {}
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
