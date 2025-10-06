#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script for Enhanced Lighting Scenarios
This script demonstrates the realistic lighting behavior with:
- Seasonal variations
- Holiday and weekend patterns
- Random occupancy variations
- Different room types with specific patterns
"""

import os
import time
from datetime import datetime
from mqtt_simulator_enhanced import MQTTSimEnhanced

def run_demo():
    """Run a demonstration of the enhanced lighting simulator"""
    
    print("=" * 80)
    print("Enhanced Lighting Scenarios Demo")
    print("=" * 80)
    print()
    print("This demo shows realistic lighting behavior with:")
    print("- Seasonal variations (sunrise/sunset times)")
    print("- Holiday and weekend patterns")
    print("- Random occupancy variations")
    print("- Different room types with specific patterns")
    print()
    print("Room Types:")
    print("- Bedroom: Early morning and evening, off during work hours")
    print("- Living Room: Most active room, longer usage periods")
    print("- Kitchen: Early morning and evening, lunch time activity")
    print("- Office: Work hours only, less activity on weekends")
    print("- Bathroom: Short usage periods throughout the day")
    print()
    
    # Configuration
    broker = os.getenv("BROKER", "test.mosquitto.org")
    port = int(os.getenv("PORT", "1883"))
    prefix = os.getenv("PREFIX", "building/demo")
    qos = int(os.getenv("QOS", "0"))
    interval = float(os.getenv("INTERVAL", "10"))
    
    print(f"Configuration:")
    print(f"- Broker: {broker}:{port}")
    print(f"- Topic Prefix: {prefix}")
    print(f"- Update Interval: {interval} seconds")
    print(f"- QoS Level: {qos}")
    print()
    
    # Create and run the enhanced simulator
    sim = MQTTSimEnhanced(broker, port, prefix, qos, interval)
    
    print("Starting enhanced MQTT simulator...")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        # Run for 5 minutes by default, or use DURATION env var
        duration = os.getenv("DURATION", "300")  # 5 minutes default
        duration = int(duration) if duration else None
        
        sim.run(duration)
        
    except KeyboardInterrupt:
        print("\nDemo stopped by user")
    except Exception as e:
        print(f"\nError: {e}")

def show_lighting_patterns():
    """Show the lighting patterns for different scenarios"""
    
    print("=" * 80)
    print("Lighting Patterns Overview")
    print("=" * 80)
    print()
    
    from mqtt_simulator_enhanced import LightingController, RoomType
    
    controller = LightingController()
    
    # Show current season info
    season = controller.get_current_season()
    print(f"Current Season: {season}")
    
    seasonal_info = {
        "spring": "Normal sunrise/sunset times",
        "summer": "Early sunrise, late sunset (longer days)",
        "autumn": "Later sunrise, earlier sunset",
        "winter": "Late sunrise, early sunset (shorter days)"
    }
    print(f"Seasonal Effect: {seasonal_info[season]}")
    print()
    
    # Show room patterns
    print("Room Lighting Patterns:")
    print("-" * 50)
    
    patterns = {
        RoomType.BEDROOM: {
            "morning": "6:30-8:00 AM",
            "evening": "7:00-11:00 PM",
            "weekend_delay": "1 hour later",
            "usage": "Sleep and relaxation"
        },
        RoomType.LIVING_ROOM: {
            "morning": "6:00-9:00 AM",
            "evening": "5:00 PM-12:00 AM",
            "weekend_delay": "30 minutes later",
            "usage": "Most active room, family time"
        },
        RoomType.KITCHEN: {
            "morning": "5:30-8:30 AM",
            "evening": "6:00-9:00 PM",
            "weekend_delay": "1.5 hours later",
            "usage": "Cooking and dining"
        },
        RoomType.OFFICE: {
            "morning": "7:00 AM-6:00 PM",
            "evening": "7:00-10:00 PM",
            "weekend_delay": "2 hours later",
            "usage": "Work hours, less weekend activity"
        },
        RoomType.BATHROOM: {
            "morning": "6:00-8:00 AM",
            "evening": "7:00-11:00 PM",
            "weekend_delay": "1 hour later",
            "usage": "Short usage periods throughout day"
        }
    }
    
    for room_type, info in patterns.items():
        print(f"{room_type.upper()}:")
        print(f"  Morning: {info['morning']}")
        print(f"  Evening: {info['evening']}")
        print(f"  Weekend Delay: {info['weekend_delay']}")
        print(f"  Usage: {info['usage']}")
        print()
    
    # Show random factors
    print("Random Factors:")
    print("-" * 20)
    print("- ±30-60 minutes random variation in timing")
    print("- 10-30% chance of unexpected usage")
    print("- Different occupancy levels (0.0-1.0)")
    print("- Seasonal adjustments to sunrise/sunset")
    print("- Holiday and weekend behavior changes")
    print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "patterns":
        show_lighting_patterns()
    else:
        show_lighting_patterns()
        print()
        input("Press Enter to start the demo...")
        run_demo()
