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

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'kbz.rew.mybluehost.me'),
    'database': os.getenv('DB_NAME', 'kbzrewmy_sensor'),
    'user': os.getenv('DB_USER', 'kbzrewmy_mo_kerma'),
    'password': os.getenv('DB_PASSWORD', 'Mehrafarid.5435'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'charset': 'utf8mb4',
    'autocommit': True
}

Base = declarative_base()

# جدول برای سنسورهای دما
class TemperatureData(Base):
    __tablename__ = 'temperature_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), nullable=False, index=True)
    room_id = Column(String(20), nullable=True, index=True)
    temperature_c = Column(Float, nullable=False)  # دما به سانتی‌گراد
    timestamp = Column(DateTime, nullable=False, index=True)
    raw_data = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<TemperatureData(device_id='{self.device_id}', temp={self.temperature_c}°C, room='{self.room_id}')>"

# جدول برای سنسورهای رطوبت
class HumidityData(Base):
    __tablename__ = 'humidity_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), nullable=False, index=True)
    room_id = Column(String(20), nullable=True, index=True)
    humidity_percent = Column(Float, nullable=False)  # رطوبت به درصد
    timestamp = Column(DateTime, nullable=False, index=True)
    raw_data = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<HumidityData(device_id='{self.device_id}', humidity={self.humidity_percent}%, room='{self.room_id}')>"

# جدول برای سنسورهای CO2
class CO2Data(Base):
    __tablename__ = 'co2_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), nullable=False, index=True)
    room_id = Column(String(20), nullable=True, index=True)
    co2_ppm = Column(Integer, nullable=False)  # CO2 به ppm
    timestamp = Column(DateTime, nullable=False, index=True)
    raw_data = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<CO2Data(device_id='{self.device_id}', co2={self.co2_ppm}ppm, room='{self.room_id}')>"

# جدول برای سنسورهای نور
class LightData(Base):
    __tablename__ = 'light_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), nullable=False, index=True)
    room_id = Column(String(20), nullable=True, index=True)
    is_on = Column(Boolean, nullable=False)  # وضعیت روشن/خاموش
    power_watts = Column(Float, nullable=True)  # توان به وات
    timestamp = Column(DateTime, nullable=False, index=True)
    raw_data = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<LightData(device_id='{self.device_id}', on={self.is_on}, power={self.power_watts}W, room='{self.room_id}')>"

# جدول برای سنسورهای خورشیدی
class SolarData(Base):
    __tablename__ = 'solar_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), nullable=False, index=True)
    power_watts = Column(Float, nullable=False)  # توان تولیدی به وات
    voltage_volts = Column(Float, nullable=False)  # ولتاژ به ولت
    current_amps = Column(Float, nullable=False)  # جریان به آمپر
    timestamp = Column(DateTime, nullable=False, index=True)
    raw_data = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<SolarData(device_id='{self.device_id}', power={self.power_watts}W, voltage={self.voltage_volts}V, current={self.current_amps}A)>"

class SeparateTablesDatabaseManager:
    def __init__(self):
        self.engine = None
        self.Session = None
        self.connect()
    
    def connect(self):
        """Create database connection and session"""
        try:
            connection_string = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
            self.engine = create_engine(connection_string, echo=False)
            self.Session = sessionmaker(bind=self.engine)
            
            # Create all tables
            Base.metadata.create_all(self.engine)
            print(f"[DB] Connected to MySQL database: {DB_CONFIG['database']}")
            print("[DB] Created separate tables for each sensor type")
            
        except Exception as e:
            print(f"[DB] Error connecting to database: {e}")
            raise
    
    def get_session(self):
        """Get a new database session"""
        return self.Session()
    
    def save_temperature_data(self, data_dict):
        """Save temperature sensor data"""
        session = self.get_session()
        try:
            timestamp = datetime.fromtimestamp(data_dict.get('ts', 0) / 1000)
            
            temp_data = TemperatureData(
                device_id=data_dict.get('deviceId', ''),
                room_id=data_dict.get('roomId'),
                temperature_c=data_dict.get('value'),
                timestamp=timestamp,
                raw_data=json.dumps(data_dict)
            )
            
            session.add(temp_data)
            session.commit()
            print(f"[DB] Saved temperature data: {temp_data.temperature_c}°C from {temp_data.device_id}")
            return True
            
        except Exception as e:
            session.rollback()
            print(f"[DB] Error saving temperature data: {e}")
            return False
        finally:
            session.close()
    
    def save_humidity_data(self, data_dict):
        """Save humidity sensor data"""
        session = self.get_session()
        try:
            timestamp = datetime.fromtimestamp(data_dict.get('ts', 0) / 1000)
            
            hum_data = HumidityData(
                device_id=data_dict.get('deviceId', ''),
                room_id=data_dict.get('roomId'),
                humidity_percent=data_dict.get('value'),
                timestamp=timestamp,
                raw_data=json.dumps(data_dict)
            )
            
            session.add(hum_data)
            session.commit()
            print(f"[DB] Saved humidity data: {hum_data.humidity_percent}% from {hum_data.device_id}")
            return True
            
        except Exception as e:
            session.rollback()
            print(f"[DB] Error saving humidity data: {e}")
            return False
        finally:
            session.close()
    
    def save_co2_data(self, data_dict):
        """Save CO2 sensor data"""
        session = self.get_session()
        try:
            timestamp = datetime.fromtimestamp(data_dict.get('ts', 0) / 1000)
            
            co2_data = CO2Data(
                device_id=data_dict.get('deviceId', ''),
                room_id=data_dict.get('roomId'),
                co2_ppm=int(data_dict.get('value', 0)),
                timestamp=timestamp,
                raw_data=json.dumps(data_dict)
            )
            
            session.add(co2_data)
            session.commit()
            print(f"[DB] Saved CO2 data: {co2_data.co2_ppm}ppm from {co2_data.device_id}")
            return True
            
        except Exception as e:
            session.rollback()
            print(f"[DB] Error saving CO2 data: {e}")
            return False
        finally:
            session.close()
    
    def save_light_data(self, data_dict):
        """Save light sensor data"""
        session = self.get_session()
        try:
            timestamp = datetime.fromtimestamp(data_dict.get('ts', 0) / 1000)
            
            light_data = LightData(
                device_id=data_dict.get('deviceId', ''),
                room_id=data_dict.get('roomId'),
                is_on=data_dict.get('on', False),
                power_watts=data_dict.get('powerW'),
                timestamp=timestamp,
                raw_data=json.dumps(data_dict)
            )
            
            session.add(light_data)
            session.commit()
            print(f"[DB] Saved light data: {'ON' if light_data.is_on else 'OFF'} ({light_data.power_watts}W) from {light_data.device_id}")
            return True
            
        except Exception as e:
            session.rollback()
            print(f"[DB] Error saving light data: {e}")
            return False
        finally:
            session.close()
    
    def save_solar_data(self, data_dict):
        """Save solar sensor data"""
        session = self.get_session()
        try:
            timestamp = datetime.fromtimestamp(data_dict.get('ts', 0) / 1000)
            
            solar_data = SolarData(
                device_id=data_dict.get('deviceId', ''),
                power_watts=data_dict.get('powerW'),
                voltage_volts=data_dict.get('voltage'),
                current_amps=data_dict.get('current'),
                timestamp=timestamp,
                raw_data=json.dumps(data_dict)
            )
            
            session.add(solar_data)
            session.commit()
            print(f"[DB] Saved solar data: {solar_data.power_watts}W, {solar_data.voltage_volts}V, {solar_data.current_amps}A from {solar_data.device_id}")
            return True
            
        except Exception as e:
            session.rollback()
            print(f"[DB] Error saving solar data: {e}")
            return False
        finally:
            session.close()
    
    def save_sensor_data(self, data_dict):
        """Save sensor data to appropriate table based on sensor type"""
        kind = data_dict.get('kind', '').lower()
        
        if kind == 'temperature':
            return self.save_temperature_data(data_dict)
        elif kind == 'humidity':
            return self.save_humidity_data(data_dict)
        elif kind == 'co2':
            return self.save_co2_data(data_dict)
        elif kind == 'light':
            return self.save_light_data(data_dict)
        elif kind == 'solar':
            return self.save_solar_data(data_dict)
        else:
            print(f"[DB] Unknown sensor type: {kind}")
            return False
    
    def get_temperature_data(self, room_id=None, limit=100):
        """Get temperature data"""
        session = self.get_session()
        try:
            query = session.query(TemperatureData)
            if room_id:
                query = query.filter(TemperatureData.room_id == room_id)
            return query.order_by(TemperatureData.timestamp.desc()).limit(limit).all()
        except Exception as e:
            print(f"[DB] Error retrieving temperature data: {e}")
            return []
        finally:
            session.close()
    
    def get_humidity_data(self, room_id=None, limit=100):
        """Get humidity data"""
        session = self.get_session()
        try:
            query = session.query(HumidityData)
            if room_id:
                query = query.filter(HumidityData.room_id == room_id)
            return query.order_by(HumidityData.timestamp.desc()).limit(limit).all()
        except Exception as e:
            print(f"[DB] Error retrieving humidity data: {e}")
            return []
        finally:
            session.close()
    
    def get_co2_data(self, room_id=None, limit=100):
        """Get CO2 data"""
        session = self.get_session()
        try:
            query = session.query(CO2Data)
            if room_id:
                query = query.filter(CO2Data.room_id == room_id)
            return query.order_by(CO2Data.timestamp.desc()).limit(limit).all()
        except Exception as e:
            print(f"[DB] Error retrieving CO2 data: {e}")
            return []
        finally:
            session.close()
    
    def get_light_data(self, room_id=None, limit=100):
        """Get light data"""
        session = self.get_session()
        try:
            query = session.query(LightData)
            if room_id:
                query = query.filter(LightData.room_id == room_id)
            return query.order_by(LightData.timestamp.desc()).limit(limit).all()
        except Exception as e:
            print(f"[DB] Error retrieving light data: {e}")
            return []
        finally:
            session.close()
    
    def get_solar_data(self, limit=100):
        """Get solar data"""
        session = self.get_session()
        try:
            return session.query(SolarData).order_by(SolarData.timestamp.desc()).limit(limit).all()
        except Exception as e:
            print(f"[DB] Error retrieving solar data: {e}")
            return []
        finally:
            session.close()
    
    def get_room_summary(self, room_id):
        """Get summary of all sensor data for a room"""
        session = self.get_session()
        try:
            # Get latest data from each sensor type
            latest_temp = session.query(TemperatureData).filter(
                TemperatureData.room_id == room_id
            ).order_by(TemperatureData.timestamp.desc()).first()
            
            latest_humidity = session.query(HumidityData).filter(
                HumidityData.room_id == room_id
            ).order_by(HumidityData.timestamp.desc()).first()
            
            latest_co2 = session.query(CO2Data).filter(
                CO2Data.room_id == room_id
            ).order_by(CO2Data.timestamp.desc()).first()
            
            latest_light = session.query(LightData).filter(
                LightData.room_id == room_id
            ).order_by(LightData.timestamp.desc()).first()
            
            return {
                'room_id': room_id,
                'temperature': latest_temp,
                'humidity': latest_humidity,
                'co2': latest_co2,
                'light': latest_light
            }
        except Exception as e:
            print(f"[DB] Error retrieving room summary: {e}")
            return None
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
separate_db_manager = SeparateTablesDatabaseManager()

if __name__ == "__main__":
    # Test the separate tables database
    db = SeparateTablesDatabaseManager()
    if db.test_connection():
        print("Separate tables database setup completed successfully!")
        
        # Test saving sample data
        print("\nTesting sample data insertion...")
        
        # Sample temperature data
        temp_data = {
            "deviceId": "temp-1",
            "kind": "temperature",
            "roomId": "room1",
            "ts": int(datetime.now().timestamp() * 1000),
            "value": 23.5,
            "unit": "C"
        }
        db.save_sensor_data(temp_data)
        
        # Sample humidity data
        hum_data = {
            "deviceId": "hum-1",
            "kind": "humidity",
            "roomId": "room1",
            "ts": int(datetime.now().timestamp() * 1000),
            "value": 45.2,
            "unit": "%"
        }
        db.save_sensor_data(hum_data)
        
        # Sample CO2 data
        co2_data = {
            "deviceId": "co2-1",
            "kind": "co2",
            "roomId": "room1",
            "ts": int(datetime.now().timestamp() * 1000),
            "value": 520,
            "unit": "ppm"
        }
        db.save_sensor_data(co2_data)
        
        # Sample light data
        light_data = {
            "deviceId": "light-1",
            "kind": "light",
            "roomId": "room1",
            "ts": int(datetime.now().timestamp() * 1000),
            "on": True,
            "powerW": 18.5
        }
        db.save_sensor_data(light_data)
        
        # Sample solar data
        solar_data = {
            "deviceId": "solar-plant",
            "kind": "solar",
            "ts": int(datetime.now().timestamp() * 1000),
            "powerW": 850.5,
            "voltage": 48.2,
            "current": 17.6
        }
        db.save_sensor_data(solar_data)
        
        print("\nSample data insertion completed!")
    else:
        print("Separate tables database setup failed!")
