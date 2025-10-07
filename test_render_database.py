#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Render.com database connection
This script tests if the database connection works with environment variables
"""

import os
import sys
from datetime import datetime

def test_database_connection():
    """Test database connection with environment variables"""
    print("=" * 60)
    print("🧪 Testing Render.com Database Connection")
    print("=" * 60)
    
    # Check environment variables
    print("📋 Checking Environment Variables:")
    env_vars = [
        'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_PORT'
    ]
    
    missing_vars = []
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Hide password for security
            display_value = "***" if var == 'DB_PASSWORD' else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n💥 Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in Render.com Environment Variables")
        return False
    
    # Test database import
    print(f"\n🔄 Testing Database Import:")
    try:
        from database import DatabaseManager
        print("✅ Database module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import database module: {e}")
        return False
    
    # Test database connection
    print(f"\n🔗 Testing Database Connection:")
    try:
        db_manager = DatabaseManager()
        print("✅ Database manager initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize database manager: {e}")
        return False
    
    # Test database operations
    print(f"\n📊 Testing Database Operations:")
    try:
        # Test saving a sample record
        test_data = {
            'deviceId': 'test-device',
            'kind': 'temperature',
            'roomId': 'test-room',
            'value': 25.5,
            'unit': '°C',
            'ts': int(datetime.now().timestamp() * 1000),
            'raw_data': '{"test": "data"}'
        }
        
        success = db_manager.save_sensor_data(test_data)
        if success:
            print("✅ Test data saved successfully")
        else:
            print("❌ Failed to save test data")
            return False
        
        # Test getting statistics
        stats = db_manager.get_table_statistics()
        print("✅ Database statistics retrieved successfully")
        print(f"📈 Table Statistics:")
        for table_name, table_stats in stats.items():
            print(f"  • {table_name}: {table_stats['count']} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operation failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Starting Render.com Database Connection Test")
    print(f"⏰ Test started at: {datetime.now().isoformat()}")
    
    success = test_database_connection()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 Database connection test PASSED!")
        print("✅ Render.com should be able to connect to database")
        print("✅ Environment variables are correctly set")
        print("✅ Database operations are working")
    else:
        print("💥 Database connection test FAILED!")
        print("❌ Check environment variables in Render.com")
        print("❌ Verify database credentials")
        print("❌ Check network connectivity")
    
    print(f"⏰ Test completed at: {datetime.now().isoformat()}")
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
