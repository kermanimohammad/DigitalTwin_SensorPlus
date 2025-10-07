#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Realistic Sensor Simulator with Gradual Temperature Changes
- Normal fluctuations: 0-1°C every 5 seconds
- Major changes: 5-8°C over 5 minutes, 2 times per hour (except 9 PM - 6 AM)
- Time zone: Eastern Canada (UTC-5/UTC-4)
- Room-specific changes, independent of each other
- Seasonal logic: summer (increase), winter (decrease)
"""

import os
import time
import random
import threading
from datetime import datetime, timedelta
import pytz

class RealisticSensorSimulator:
    """Realistic sensor simulator with gradual temperature changes"""
    
    def __init__(self):
        self.running = False
        self.interval = 5  # 5 seconds
        self.room_count = 5
        self.devices_per_room = 4  # temp, humidity, co2, light
        self.solar_devices = 1
        
        # Eastern Canada timezone
        self.timezone = pytz.timezone('America/Toronto')
        
        # Temperature base values for each room
        self.room_base_temps = {
            1: 22.0, 2: 21.5, 3: 23.0, 4: 22.5, 5: 21.0
        }
        
        # Current temperature values
        self.current_temps = self.room_base_temps.copy()
        
        # Major change tracking
        self.major_change_active = {i: False for i in range(1, 6)}
        self.major_change_start_time = {i: None for i in range(1, 6)}
        self.major_change_target = {i: 0 for i in range(1, 6)}
        self.major_change_duration = 300  # 5 minutes = 300 seconds
        
        # Last major change time for each room
        self.last_major_change = {i: datetime.now(self.timezone) for i in range(1, 6)}
        
        print(f"[Realistic Simulator] Initialized with {self.room_count} rooms")
        print(f"[Realistic Simulator] Timezone: {self.timezone}")
        print(f"[Realistic Simulator] Base temperatures: {self.room_base_temps}")
        
    def get_current_season(self):
        """Determine current season based on month"""
        now = datetime.now(self.timezone)
        month = now.month
        
        if month in [12, 1, 2]:  # Winter
            return 'winter'
        elif month in [3, 4, 5]:  # Spring
            return 'spring'
        elif month in [6, 7, 8]:  # Summer
            return 'summer'
        else:  # Fall
            return 'fall'
    
    def is_major_change_time(self):
        """Check if it's time for major changes (not between 9 PM - 6 AM)"""
        now = datetime.now(self.timezone)
        hour = now.hour
        
        # No major changes between 9 PM (21:00) and 6 AM (06:00)
        if 21 <= hour or hour < 6:
            return False
        return True
    
    def should_trigger_major_change(self, room_id):
        """Check if a major change should be triggered for this room"""
        if not self.is_major_change_time():
            return False
            
        if self.major_change_active[room_id]:
            return False
            
        # Check if enough time has passed since last major change (30 minutes)
        time_since_last = datetime.now(self.timezone) - self.last_major_change[room_id]
        if time_since_last.total_seconds() < 1800:  # 30 minutes
            return False
            
        # 2 times per hour = 50% chance every 30 minutes
        return random.random() < 0.5
    
    def calculate_major_change(self, room_id):
        """Calculate major temperature change based on season"""
        season = self.get_current_season()
        current_temp = self.current_temps[room_id]
        
        # Major change: 5-8 degrees
        change_magnitude = random.uniform(5.0, 8.0)
        
        if season in ['summer', 'spring']:
            # Warmer seasons: opening window increases temperature
            change_direction = random.choice([1, 1, 1, -1])  # 75% increase, 25% decrease
        else:  # winter, fall
            # Colder seasons: opening window decreases temperature
            change_direction = random.choice([-1, -1, -1, 1])  # 75% decrease, 25% increase
        
        target_temp = current_temp + (change_magnitude * change_direction)
        
        # Keep temperature within reasonable bounds (15-30°C)
        target_temp = max(15.0, min(30.0, target_temp))
        
        return target_temp
    
    def update_temperature_gradually(self, room_id):
        """Update temperature gradually during major change"""
        if not self.major_change_active[room_id]:
            return
            
        elapsed = time.time() - self.major_change_start_time[room_id]
        progress = min(elapsed / self.major_change_duration, 1.0)
        
        # Smooth transition using easing function
        eased_progress = progress * progress * (3.0 - 2.0 * progress)  # Smooth step
        
        start_temp = self.room_base_temps[room_id]
        target_temp = self.major_change_target[room_id]
        
        self.current_temps[room_id] = start_temp + (target_temp - start_temp) * eased_progress
        
        # Check if major change is complete
        if progress >= 1.0:
            self.major_change_active[room_id] = False
            self.room_base_temps[room_id] = target_temp
            self.last_major_change[room_id] = datetime.now(self.timezone)
            print(f"[Major Change] Room {room_id} completed: {target_temp:.1f}°C")
    
    def update_temperature_normal(self, room_id):
        """Update temperature with normal fluctuations"""
        if self.major_change_active[room_id]:
            return
            
        # Normal fluctuation: 0-1°C
        fluctuation = random.uniform(-1.0, 1.0)
        new_temp = self.current_temps[room_id] + fluctuation
        
        # Keep within reasonable bounds
        new_temp = max(15.0, min(30.0, new_temp))
        self.current_temps[room_id] = new_temp
    
    def run(self):
        """Run the realistic simulator"""
        self.running = True
        print(f"[Realistic Simulator] Started with realistic temperature changes")
        
        while self.running:
            current_time = datetime.now(self.timezone)
            
            # Generate sensor data for all rooms
            for room_id in range(1, self.room_count + 1):
                room_name = f'room{room_id}'
                
                # Check for major change trigger
                if self.should_trigger_major_change(room_id):
                    target_temp = self.calculate_major_change(room_id)
                    self.major_change_active[room_id] = True
                    self.major_change_start_time[room_id] = time.time()
                    self.major_change_target[room_id] = target_temp
                    
                    season = self.get_current_season()
                    change_type = "increase" if target_temp > self.current_temps[room_id] else "decrease"
                    print(f"[Major Change] Room {room_id} started {change_type} to {target_temp:.1f}°C ({season})")
                
                # Update temperature
                if self.major_change_active[room_id]:
                    self.update_temperature_gradually(room_id)
                else:
                    self.update_temperature_normal(room_id)
                
                # Generate other sensor data with realistic variations
                temp = round(self.current_temps[room_id], 1)
                
                # Humidity: realistic indoor room humidity (30-60%)
                base_humidity = 45 - (temp - 22) * 1.5  # Base humidity around 45%
                humidity = round(base_humidity + random.uniform(-0.6, 0.6), 1)
                humidity = max(30, min(60, humidity))
                
                # CO2: slightly higher when temperature is higher (more activity)
                base_co2 = 400 + (temp - 20) * 10
                co2 = round(base_co2 + random.uniform(-20, 20), 0)
                co2 = max(350, min(600, co2))
                
                # Light: random but realistic
                light = round(800 + random.uniform(-200, 200), 0)
                light = max(100, min(1200, light))
                
                # Store data (this would be sent to your dashboard)
                sensor_data = {
                    f'temp-{room_id}': {
                        'device_id': f'temp-{room_id}',
                        'kind': 'temperature',
                        'value': temp,
                        'unit': '°C',
                        'room_id': room_name,
                        'timestamp': current_time.isoformat(),
                        'major_change': self.major_change_active[room_id]
                    },
                    f'hum-{room_id}': {
                        'device_id': f'hum-{room_id}',
                        'kind': 'humidity',
                        'value': humidity,
                        'unit': '%',
                        'room_id': room_name,
                        'timestamp': current_time.isoformat()
                    },
                    f'co2-{room_id}': {
                        'device_id': f'co2-{room_id}',
                        'kind': 'co2',
                        'value': co2,
                        'unit': 'ppm',
                        'room_id': room_name,
                        'timestamp': current_time.isoformat()
                    },
                    f'light-{room_id}': {
                        'device_id': f'light-{room_id}',
                        'kind': 'light',
                        'value': light,
                        'unit': 'lux',
                        'room_id': room_name,
                        'timestamp': current_time.isoformat()
                    }
                }
                
                # Print temperature changes for monitoring
                if self.major_change_active[room_id]:
                    elapsed = time.time() - self.major_change_start_time[room_id]
                    remaining = self.major_change_duration - elapsed
                    print(f"[Room {room_id}] Major change: {temp:.1f}°C (remaining: {remaining:.0f}s)")
            
            # Solar Panel (independent)
            solar_power = round(120 + random.uniform(-20, 20), 1)
            solar_data = {
                'solar-plant': {
                    'device_id': 'solar-plant',
                    'kind': 'solar',
                    'value': solar_power,
                    'unit': 'W',
                    'room_id': 'solar-farm',
                    'timestamp': current_time.isoformat()
                }
            }
            
            total_devices = self.room_count * self.devices_per_room + self.solar_devices
            active_major_changes = sum(1 for active in self.major_change_active.values() if active)
            
            if active_major_changes > 0:
                print(f"[Simulator] Updated {total_devices} devices, {active_major_changes} major changes active")
            else:
                print(f"[Simulator] Updated {total_devices} devices (normal mode)")
            
            time.sleep(self.interval)
    
    def stop(self):
        self.running = False
        print("[Realistic Simulator] Stopped")

def main():
    """Test the realistic simulator"""
    print("=" * 60)
    print("🧪 Testing Realistic Sensor Simulator")
    print("=" * 60)
    
    simulator = RealisticSensorSimulator()
    
    try:
        simulator.run()
    except KeyboardInterrupt:
        print("\n🛑 Stopping simulator...")
        simulator.stop()

if __name__ == '__main__':
    main()
