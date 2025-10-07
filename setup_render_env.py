#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to help setup Render.com environment variables
This script provides the exact commands and values needed for Render.com
"""

def print_render_setup_guide():
    """Print Render.com setup guide"""
    print("=" * 80)
    print("🚀 RENDER.COM DATABASE SETUP GUIDE")
    print("=" * 80)
    
    print("\n📋 STEP 1: Go to Render Dashboard")
    print("   https://dashboard.render.com")
    print("   Select your project: digitaltwin-sensorplus-1")
    
    print("\n📋 STEP 2: Add Environment Variables")
    print("   Click on 'Environment' tab")
    print("   Click 'Add Environment Variable' for each variable below:")
    
    print("\n🗄️ DATABASE CONFIGURATION:")
    env_vars = [
        ("DB_HOST", "kbz.rew.mybluehost.me"),
        ("DB_NAME", "kbzrewmy_sensor"),
        ("DB_USER", "kbzrewmy_mo_kerma"),
        ("DB_PASSWORD", "Mehrafarid.5435"),
        ("DB_PORT", "3306"),
        ("DB_CHARSET", "utf8mb4")
    ]
    
    for var, value in env_vars:
        print(f"   Key: {var}")
        print(f"   Value: {value}")
        print()
    
    print("⚙️ APPLICATION CONFIGURATION:")
    app_vars = [
        ("PORT", "10000"),
        ("PYTHONUNBUFFERED", "1"),
        ("FLASK_ENV", "production"),
        ("FLASK_DEBUG", "False"),
        ("SECRET_KEY", "digitaltwin-sensor-api-secret-key-2024")
    ]
    
    for var, value in app_vars:
        print(f"   Key: {var}")
        print(f"   Value: {value}")
        print()
    
    print("🔄 SIMULATOR CONFIGURATION:")
    sim_vars = [
        ("SIMULATOR_INTERVAL", "5"),
        ("SIMULATOR_DEVICES", "21"),
        ("DASHBOARD_TITLE", "DigitalTwin Sensor Dashboard"),
        ("LOG_LEVEL", "INFO")
    ]
    
    for var, value in sim_vars:
        print(f"   Key: {var}")
        print(f"   Value: {value}")
        print()
    
    print("📋 STEP 3: Deploy")
    print("   1. Click 'Save Changes'")
    print("   2. Click 'Manual Deploy'")
    print("   3. Select 'Deploy latest commit'")
    print("   4. Wait for deployment to complete")
    
    print("\n✅ STEP 4: Verify")
    print("   After deployment, check your dashboard:")
    print("   - Database: Connected (green)")
    print("   - DB Saves: > 0 (increasing every minute)")
    print("   - DB Errors: 0")
    
    print("\n🔍 TROUBLESHOOTING:")
    print("   If Database still shows 'Not Available':")
    print("   1. Check Render.com Logs for errors")
    print("   2. Verify all environment variables are set")
    print("   3. Test database connection manually")
    print("   4. Try manual deploy again")
    
    print("\n" + "=" * 80)
    print("🎯 TOTAL ENVIRONMENT VARIABLES TO ADD: 15")
    print("⏰ ESTIMATED SETUP TIME: 5-10 minutes")
    print("🚀 EXPECTED RESULT: Database connected and saving data every minute")
    print("=" * 80)

def generate_env_file():
    """Generate environment variables file for reference"""
    env_content = """# Environment Variables for Render.com
# Copy these values to Render Dashboard > Environment Variables

# Database Configuration
DB_HOST=kbz.rew.mybluehost.me
DB_NAME=kbzrewmy_sensor
DB_USER=kbzrewmy_mo_kerma
DB_PASSWORD=Mehrafarid.5435
DB_PORT=3306
DB_CHARSET=utf8mb4

# Application Configuration
PORT=10000
PYTHONUNBUFFERED=1
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=digitaltwin-sensor-api-secret-key-2024

# Simulator Configuration
SIMULATOR_INTERVAL=5
SIMULATOR_DEVICES=21
DASHBOARD_TITLE=DigitalTwin Sensor Dashboard
LOG_LEVEL=INFO
"""
    
    with open('render_env_vars_complete.txt', 'w') as f:
        f.write(env_content)
    
    print(f"\n📄 Environment variables file created: render_env_vars_complete.txt")
    print("   You can use this file as reference when setting up Render.com")

if __name__ == '__main__':
    print_render_setup_guide()
    generate_env_file()
