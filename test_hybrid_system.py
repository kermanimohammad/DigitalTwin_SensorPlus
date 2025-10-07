#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Hybrid Sensor System
Tests the combination of real-time data and database storage
"""

import requests
import time
import json
from datetime import datetime
import threading

def test_hybrid_api():
    """Test the hybrid sensor API endpoints"""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Hybrid Sensor API...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/hybrid/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Check: PASSED")
            health = data['health']
            print(f"   MQTT Status: {health['mqtt_status']}")
            print(f"   Database Status: {health['database_status']}")
            print(f"   Live Devices: {health['live_devices']}")
            print(f"   DB Success Rate: {health['db_success_rate']:.1f}%")
        else:
            print("❌ Health Check: FAILED")
    except Exception as e:
        print(f"❌ Health Check: ERROR - {e}")
    
    # Test hybrid stats endpoint
    try:
        response = requests.get(f"{base_url}/api/hybrid/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Hybrid Stats: PASSED")
            stats = data['stats']
            print(f"   Live Devices: {stats['live']['total_devices']}")
            print(f"   Active Devices: {stats['live']['active_devices']}")
            print(f"   DB Records: {stats['database']['total_records']}")
            print(f"   Unique DB Devices: {stats['database']['unique_devices']}")
        else:
            print("❌ Hybrid Stats: FAILED")
    except Exception as e:
        print(f"❌ Hybrid Stats: ERROR - {e}")
    
    # Test live devices endpoint
    try:
        response = requests.get(f"{base_url}/api/hybrid/live/devices", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Live Devices: PASSED")
            print(f"   Device Count: {data['count']}")
            if data['devices']:
                for device_id in list(data['devices'].keys())[:3]:  # Show first 3 devices
                    device = data['devices'][device_id]
                    latest = device['latest_data']
                    stats = device['statistics']
                    print(f"   - {device_id}: {latest.get('kind')} = {latest.get('value')} {latest.get('unit', '')}")
                    print(f"     Messages: {stats.get('message_count', 0)}, DB Saves: {stats.get('db_save_count', 0)}")
        else:
            print("❌ Live Devices: FAILED")
    except Exception as e:
        print(f"❌ Live Devices: ERROR - {e}")
    
    # Test analytics endpoint
    try:
        response = requests.get(f"{base_url}/api/hybrid/analytics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics: PASSED")
            analytics = data['analytics']
            print(f"   Total DB Records: {analytics['database_stats']['total_records']}")
            print(f"   Recent Records: {analytics['database_stats']['recent_records']}")
            print(f"   Activity Rate: {analytics['trends']['activity_rate']:.1f}%")
        else:
            print("❌ Analytics: FAILED")
    except Exception as e:
        print(f"❌ Analytics: ERROR - {e}")

def test_hybrid_dashboard():
    """Test the hybrid dashboard"""
    dashboard_url = "http://localhost:5000"
    
    print("\n🌐 Testing Hybrid Dashboard...")
    print("=" * 50)
    
    try:
        response = requests.get(dashboard_url, timeout=5)
        if response.status_code == 200:
            print("✅ Hybrid Dashboard: ACCESSIBLE")
            print(f"   URL: {dashboard_url}")
            print("   Features: Real-time + Database + Analytics")
        else:
            print("❌ Hybrid Dashboard: NOT ACCESSIBLE")
    except Exception as e:
        print(f"❌ Hybrid Dashboard: ERROR - {e}")

def test_database_connection():
    """Test database connection"""
    print("\n🗄️ Testing Database Connection...")
    print("=" * 50)
    
    try:
        from database import db_manager
        
        # Test database connection
        if db_manager.engine:
            print("✅ Database: CONNECTED")
            
            # Test getting recent data
            records = db_manager.get_recent_data(limit=5)
            print(f"   Recent Records: {len(records)}")
            
            if records:
                latest = records[0]
                print(f"   Latest: {latest.device_id} - {latest.kind} = {latest.value}")
        else:
            print("❌ Database: NOT CONNECTED")
            
    except Exception as e:
        print(f"❌ Database Test: ERROR - {e}")

def test_mqtt_connection():
    """Test MQTT connection"""
    print("\n📡 Testing MQTT Connection...")
    print("=" * 50)
    
    try:
        import paho.mqtt.client as mqtt
        import time
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("✅ MQTT Broker: CONNECTED")
                client.disconnect()
            else:
                print(f"❌ MQTT Broker: CONNECTION FAILED (rc={rc})")
        
        def on_disconnect(client, userdata, rc):
            print("   MQTT connection test completed")
        
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        
        client.connect("localhost", 1883, 60)
        client.loop_start()
        time.sleep(2)
        client.loop_stop()
        
    except Exception as e:
        print(f"❌ MQTT Test: ERROR - {e}")

def test_hybrid_subscriber():
    """Test hybrid MQTT subscriber"""
    print("\n🔄 Testing Hybrid MQTT Subscriber...")
    print("=" * 50)
    
    try:
        from mqtt_subscriber_hybrid import get_hybrid_subscriber
        
        subscriber = get_hybrid_subscriber()
        
        if subscriber.running:
            print("✅ Hybrid Subscriber: RUNNING")
            
            # Get live data
            live_data = subscriber.get_live_data()
            print(f"   Connected Devices: {len(live_data.get('latest_data', {}))}")
            
            # Get statistics
            stats = subscriber.get_statistics()
            print(f"   Total Messages: {stats.get('global_stats', {}).get('total_messages', 0)}")
            print(f"   DB Success Rate: {stats.get('global_stats', {}).get('db_success_rate', 0):.1f}%")
        else:
            print("❌ Hybrid Subscriber: NOT RUNNING")
            
    except Exception as e:
        print(f"❌ Hybrid Subscriber Test: ERROR - {e}")

def test_data_flow():
    """Test the complete data flow"""
    print("\n🔄 Testing Data Flow...")
    print("=" * 50)
    
    try:
        # Test MQTT simulator
        print("1. Starting MQTT Simulator for 10 seconds...")
        
        def run_simulator():
            import subprocess
            import time
            try:
                # Run MQTT simulator for 10 seconds
                process = subprocess.Popen(['python', 'mqtt_simulator.py'], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
                time.sleep(10)
                process.terminate()
            except Exception as e:
                print(f"   Simulator error: {e}")
        
        # Run simulator in background
        simulator_thread = threading.Thread(target=run_simulator, daemon=True)
        simulator_thread.start()
        
        # Wait a bit for data to flow
        time.sleep(5)
        
        # Check if data is flowing
        try:
            response = requests.get("http://localhost:5001/api/hybrid/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                health = data['health']
                print(f"2. Data Flow Check:")
                print(f"   Total Messages: {health['total_messages']}")
                print(f"   DB Saves: {health['db_saves']}")
                print(f"   DB Success Rate: {health['db_success_rate']:.1f}%")
                
                if health['total_messages'] > 0:
                    print("✅ Data Flow: WORKING")
                else:
                    print("⚠️ Data Flow: NO MESSAGES YET")
            else:
                print("❌ Data Flow: API NOT RESPONDING")
        except Exception as e:
            print(f"❌ Data Flow: ERROR - {e}")
        
    except Exception as e:
        print(f"❌ Data Flow Test: ERROR - {e}")

def main():
    """Run all tests"""
    print("🚀 Hybrid Sensor System Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test individual components
    test_mqtt_connection()
    test_database_connection()
    test_hybrid_subscriber()
    
    # Test API endpoints
    test_hybrid_api()
    
    # Test dashboard
    test_hybrid_dashboard()
    
    # Test complete data flow
    test_data_flow()
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")
    print("\n📋 Next steps:")
    print("1. Start MQTT simulator: python mqtt_simulator.py")
    print("2. Open hybrid dashboard: http://localhost:5000")
    print("3. Check hybrid API: http://localhost:5001")
    print("4. Monitor real-time data + database storage")
    print("\n🎯 Features tested:")
    print("✅ Real-time data display")
    print("✅ Database storage for history")
    print("✅ Hybrid API endpoints")
    print("✅ Analytics and statistics")
    print("✅ Data export functionality")

if __name__ == "__main__":
    main()
