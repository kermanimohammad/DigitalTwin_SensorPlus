#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script for Advanced Sensor Simulations
Demonstrates realistic sensor patterns with weather, seasonal, and occupancy effects
"""

import os
import time
from datetime import datetime
from mqtt_simulator_advanced import MQTTSimAdvanced

def show_sensor_patterns():
    """Show detailed sensor patterns and behaviors"""
    
    print("=" * 80)
    print("Advanced Sensor Simulation Patterns")
    print("=" * 80)
    print()
    
    print("SOLAR PANEL SIMULATION:")
    print("-" * 30)
    print("• Day/Night Cycle: 0W at night, gradual increase from sunrise")
    print("• Peak Production: Maximum at noon (12:00)")
    print("• Seasonal Variations:")
    print("  - Spring: 80% efficiency")
    print("  - Summer: 120% efficiency (longer days)")
    print("  - Autumn: 70% efficiency")
    print("  - Winter: 50% efficiency (shorter days)")
    print("• Weather Effects:")
    print("  - Sunny: 100% production")
    print("  - Cloudy: 30% production")
    print("  - Rainy: 10% production")
    print("  - Stormy: 5% production")
    print()
    
    print("TEMPERATURE SIMULATION:")
    print("-" * 30)
    print("• Room-Specific Base Temperatures:")
    print("  - Bedroom: 20°C (cooler for sleep)")
    print("  - Living Room: 22°C (comfortable)")
    print("  - Kitchen: 24°C (warmer due to cooking)")
    print("  - Office: 21°C (optimal for work)")
    print("  - Bathroom: 23°C (warm for comfort)")
    print("• Seasonal Adjustments:")
    print("  - Spring: +0°C")
    print("  - Summer: +8°C")
    print("  - Autumn: -2°C")
    print("  - Winter: -8°C")
    print("• Occupancy Effects: +0.5-2.0°C per person")
    print("• Weather Effects: ±2°C based on conditions")
    print()
    
    print("HUMIDITY SIMULATION:")
    print("-" * 30)
    print("• Room-Specific Base Humidity:")
    print("  - Bedroom: 45% (comfortable for sleep)")
    print("  - Living Room: 50% (balanced)")
    print("  - Kitchen: 60% (higher due to cooking)")
    print("  - Office: 40% (optimal for work)")
    print("  - Bathroom: 70% (highest due to showers)")
    print("• Seasonal Adjustments:")
    print("  - Spring: +0%")
    print("  - Summer: +15%")
    print("  - Autumn: +10%")
    print("  - Winter: -10%")
    print("• Weather Effects:")
    print("  - Sunny: -5% humidity")
    print("  - Rainy: +15% humidity")
    print("  - Stormy: +20% humidity")
    print()
    
    print("CO2 SIMULATION:")
    print("-" * 30)
    print("• Base CO2 Levels:")
    print("  - Bedroom: 400 ppm")
    print("  - Living Room: 450 ppm")
    print("  - Kitchen: 500 ppm")
    print("  - Office: 420 ppm")
    print("  - Bathroom: 480 ppm")
    print("• Occupancy Effects: +200 ppm per person")
    print("• Ventilation Rates:")
    print("  - Bedroom: 30% (low)")
    print("  - Living Room: 50% (medium)")
    print("  - Kitchen: 80% (high)")
    print("  - Office: 70% (good)")
    print("  - Bathroom: 90% (highest)")
    print("• Time-Based Ventilation:")
    print("  - Work Hours (8-18): +30% ventilation")
    print("  - Night (22-6): -20% ventilation")
    print()
    
    print("WEATHER SIMULATION:")
    print("-" * 30)
    print("• Dynamic Weather Changes:")
    print("  - Changes every 30-120 minutes")
    print("  - Seasonal probability adjustments")
    print("• Weather Conditions:")
    print("  - Sunny: Clear skies, maximum solar")
    print("  - Cloudy: Reduced solar, stable conditions")
    print("  - Rainy: Low solar, increased humidity")
    print("  - Stormy: Minimal solar, high humidity")
    print("• Seasonal Weather Patterns:")
    print("  - Spring: 30% rain, 40% clouds")
    print("  - Summer: 20% rain, 30% clouds")
    print("  - Autumn: 40% rain, 50% clouds")
    print("  - Winter: 30% rain, 60% clouds")
    print()

def show_mqtt_topics():
    """Show MQTT topic structure and data format"""
    
    print("=" * 80)
    print("MQTT Topics and Data Format")
    print("=" * 80)
    print()
    
    print("ROOM SENSOR TOPICS:")
    print("-" * 30)
    print("• {prefix}/{room_id}/temperature")
    print("• {prefix}/{room_id}/humidity")
    print("• {prefix}/{room_id}/co2")
    print("• {prefix}/{room_id}/light")
    print("• {prefix}/{room_id}/occupancy")
    print()
    
    print("SYSTEM TOPICS:")
    print("-" * 30)
    print("• {prefix}/solar")
    print("• {prefix}/weather")
    print()
    
    print("ENHANCED DATA FORMAT:")
    print("-" * 30)
    print("Temperature Example:")
    print('{')
    print('  "deviceId": "temp-1",')
    print('  "kind": "temperature",')
    print('  "roomId": "room1",')
    print('  "roomType": "bedroom",')
    print('  "ts": 1696608000000,')
    print('  "value": 22.4,')
    print('  "unit": "C",')
    print('  "occupancy": 0.75')
    print('}')
    print()
    
    print("Solar Example:")
    print('{')
    print('  "deviceId": "solar-plant",')
    print('  "kind": "solar",')
    print('  "ts": 1696608000000,')
    print('  "powerW": 755.6,')
    print('  "voltage": 48.2,')
    print('  "current": 15.7,')
    print('  "efficiency": 0.756,')
    print('  "season": "autumn",')
    print('  "weather": "cloudy"')
    print('}')
    print()
    
    print("Weather Example:")
    print('{')
    print('  "deviceId": "weather-station",')
    print('  "kind": "weather",')
    print('  "ts": 1696608000000,')
    print('  "condition": "cloudy",')
    print('  "season": "autumn",')
    print('  "solarImpact": 0.3')
    print('}')
    print()

def run_demo():
    """Run the advanced sensor simulation demo"""
    
    print("=" * 80)
    print("Advanced Sensor Simulation Demo")
    print("=" * 80)
    print()
    print("This demo shows realistic sensor behavior with:")
    print("- Dynamic weather conditions")
    print("- Seasonal variations")
    print("- Room-specific patterns")
    print("- Occupancy effects")
    print("- Time-based behaviors")
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
    
    # Create and run the advanced simulator
    sim = MQTTSimAdvanced(broker, port, prefix, qos, interval)
    
    print("Starting advanced MQTT simulator...")
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

def show_usage_examples():
    """Show usage examples and configuration options"""
    
    print("=" * 80)
    print("Usage Examples and Configuration")
    print("=" * 80)
    print()
    
    print("BASIC USAGE:")
    print("-" * 20)
    print("python mqtt_simulator_advanced.py")
    print()
    
    print("WITH ENVIRONMENT VARIABLES:")
    print("-" * 30)
    print("export BROKER='test.mosquitto.org'")
    print("export PORT='1883'")
    print("export PREFIX='building/demo'")
    print("export INTERVAL='5'")
    print("export DURATION='600'")
    print("python mqtt_simulator_advanced.py")
    print()
    
    print("DOCKER USAGE:")
    print("-" * 20)
    print("docker compose up --build -d")
    print("docker compose logs -f mqtt-sim")
    print()
    
    print("TESTING:")
    print("-" * 20)
    print("python test_advanced_sensors.py")
    print()
    
    print("CUSTOMIZATION:")
    print("-" * 20)
    print("• Modify room patterns in room_sensor_patterns")
    print("• Adjust seasonal effects in seasonal_adjustments")
    print("• Change weather probabilities in weather_effects")
    print("• Add new room types or sensor types")
    print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "patterns":
            show_sensor_patterns()
        elif sys.argv[1] == "topics":
            show_mqtt_topics()
        elif sys.argv[1] == "usage":
            show_usage_examples()
        else:
            print("Usage: python demo_advanced_sensors.py [patterns|topics|usage]")
    else:
        show_sensor_patterns()
        print()
        show_mqtt_topics()
        print()
        show_usage_examples()
        print()
        input("Press Enter to start the demo...")
        run_demo()
