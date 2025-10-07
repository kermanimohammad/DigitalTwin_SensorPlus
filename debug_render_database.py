#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to check Render.com database connection issues
"""

import os
import sys
from datetime import datetime

def debug_environment():
    """Debug environment variables"""
    print("=" * 60)
    print("🔍 DEBUGGING RENDER.COM DATABASE CONNECTION")
    print("=" * 60)
    
    print("\n📋 Environment Variables Check:")
    env_vars = [
        'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_PORT', 'DB_CHARSET',
        'PORT', 'PYTHONUNBUFFERED', 'FLASK_ENV', 'SECRET_KEY'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            display_value = "***" if 'PASSWORD' in var else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NOT SET")
    
    print(f"\n🌍 Environment Info:")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current Directory: {os.getcwd()}")
    
    # Check if we're in Render.com environment
    render_indicators = [
        'RENDER', 'PORT', 'PYTHONUNBUFFERED'
    ]
    
    render_env = any(os.getenv(var) for var in render_indicators)
    print(f"Render.com Environment: {'Yes' if render_env else 'No'}")

def debug_database_import():
    """Debug database import"""
    print(f"\n🔄 Database Import Test:")
    try:
        from database import DatabaseManager, DB_CONFIG
        print("✅ Database module imported successfully")
        print(f"📊 DB_CONFIG: {DB_CONFIG}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import database module: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing database: {e}")
        return False

def debug_database_connection():
    """Debug database connection"""
    print(f"\n🔗 Database Connection Test:")
    try:
        from database import DatabaseManager
        
        print("🔄 Initializing DatabaseManager...")
        db_manager = DatabaseManager()
        print("✅ DatabaseManager initialized successfully")
        
        print("🔄 Testing database connection...")
        # Try to get a session
        session = db_manager.get_session()
        print("✅ Database session created successfully")
        session.close()
        
        print("🔄 Testing table statistics...")
        stats = db_manager.get_table_statistics()
        print("✅ Table statistics retrieved successfully")
        print(f"📊 Statistics: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

def debug_dashboard_code():
    """Debug dashboard code logic"""
    print(f"\n🎯 Dashboard Code Logic Test:")
    
    # Simulate the dashboard logic
    DATABASE_AVAILABLE = False
    db_manager = None
    
    try:
        from database import DatabaseManager
        DATABASE_AVAILABLE = True
        print("✅ Database module imported successfully")
    except ImportError as e:
        print(f"❌ Database module not available: {e}")
        print("❌ Running in simulation mode only")
        return False
    
    if DATABASE_AVAILABLE:
        try:
            db_manager = DatabaseManager()
            print("✅ Database manager initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize database manager: {e}")
            DATABASE_AVAILABLE = False
    
    print(f"📊 Final Status:")
    print(f"  DATABASE_AVAILABLE: {DATABASE_AVAILABLE}")
    print(f"  db_manager: {'Available' if db_manager else 'None'}")
    
    return DATABASE_AVAILABLE and db_manager is not None

def main():
    """Main debug function"""
    print("🚀 Starting Render.com Database Debug")
    print(f"⏰ Debug started at: {datetime.now().isoformat()}")
    
    # Run all debug tests
    debug_environment()
    import_success = debug_database_import()
    connection_success = debug_database_connection() if import_success else False
    dashboard_success = debug_dashboard_code()
    
    print(f"\n{'='*60}")
    print("📊 DEBUG SUMMARY:")
    print(f"✅ Environment Variables: {'OK' if any(os.getenv('DB_HOST')) else 'MISSING'}")
    print(f"✅ Database Import: {'OK' if import_success else 'FAILED'}")
    print(f"✅ Database Connection: {'OK' if connection_success else 'FAILED'}")
    print(f"✅ Dashboard Logic: {'OK' if dashboard_success else 'FAILED'}")
    
    if dashboard_success:
        print("\n🎉 All tests passed! Database should work in Render.com")
    else:
        print("\n💥 Some tests failed! Check the errors above")
        
        if not any(os.getenv('DB_HOST')):
            print("\n🔧 SOLUTION: Set environment variables in Render.com")
        elif not import_success:
            print("\n🔧 SOLUTION: Check database.py file")
        elif not connection_success:
            print("\n🔧 SOLUTION: Check database credentials and network")
    
    print(f"⏰ Debug completed at: {datetime.now().isoformat()}")
    return dashboard_success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
