#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System startup script to run all components
"""

import subprocess
import time
import sys
import os
import signal
import threading
from datetime import datetime

class SystemManager:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_mqtt_broker(self):
        """Start MQTT broker"""
        print("🔧 Starting MQTT Broker...")
        try:
            # Try to start mosquitto broker
            cmd = ["mosquitto", "-v", "-c", "mosquitto/mosquitto.conf"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(("MQTT Broker", process))
            print("✅ MQTT Broker started")
            time.sleep(2)  # Give it time to start
            return True
        except FileNotFoundError:
            print("❌ Mosquitto not found. Please install mosquitto or use Docker.")
            return False
        except Exception as e:
            print(f"❌ Error starting MQTT Broker: {e}")
            return False
    
    def start_mqtt_simulator(self):
        """Start MQTT simulator"""
        print("📡 Starting MQTT Simulator...")
        try:
            cmd = [sys.executable, "mqtt_simulator.py"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(("MQTT Simulator", process))
            print("✅ MQTT Simulator started")
            time.sleep(2)  # Give it time to start
            return True
        except Exception as e:
            print(f"❌ Error starting MQTT Simulator: {e}")
            return False
    
    def start_dashboard(self):
        """Start Dashboard"""
        print("🌐 Starting Dashboard...")
        try:
            cmd = [sys.executable, "final_working_dashboard.py"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(("Dashboard", process))
            print("✅ Dashboard started")
            time.sleep(3)  # Give it time to start
            return True
        except Exception as e:
            print(f"❌ Error starting Dashboard: {e}")
            return False
    
    def check_ports(self):
        """Check if required ports are open"""
        print("\n🔍 Checking system status...")
        
        # Check MQTT broker (port 1883)
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 1883))
            sock.close()
            if result == 0:
                print("✅ MQTT Broker (port 1883) is running")
            else:
                print("❌ MQTT Broker (port 1883) is not running")
        except Exception as e:
            print(f"❌ Error checking MQTT Broker: {e}")
        
        # Check Dashboard (port 5000)
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 5000))
            sock.close()
            if result == 0:
                print("✅ Dashboard (port 5000) is running")
                print("🌐 Dashboard URL: http://localhost:5000")
            else:
                print("❌ Dashboard (port 5000) is not running")
        except Exception as e:
            print(f"❌ Error checking Dashboard: {e}")
    
    def monitor_processes(self):
        """Monitor running processes"""
        while self.running:
            for name, process in self.processes:
                if process.poll() is not None:
                    print(f"⚠️  {name} has stopped unexpectedly")
            time.sleep(5)
    
    def stop_all(self):
        """Stop all processes"""
        print("\n🛑 Stopping all processes...")
        self.running = False
        
        for name, process in self.processes:
            try:
                print(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                print(f"⚠️  Force killing {name}...")
                process.kill()
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
    
    def start_system(self):
        """Start the complete system"""
        print("=" * 60)
        print("🚀 Starting Digital Twin Sensor System")
        print("=" * 60)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Start components
        success = True
        success &= self.start_mqtt_broker()
        success &= self.start_mqtt_simulator()
        success &= self.start_dashboard()
        
        if not success:
            print("\n❌ Some components failed to start!")
            self.stop_all()
            return False
        
        # Check system status
        self.check_ports()
        
        # Start monitoring
        monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        monitor_thread.start()
        
        print("\n" + "=" * 60)
        print("✅ System started successfully!")
        print("🌐 Dashboard: http://localhost:5000")
        print("📡 MQTT Broker: localhost:1883")
        print("=" * 60)
        print("\nPress Ctrl+C to stop all services...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
            self.stop_all()
            print("✅ System stopped successfully!")
        
        return True

def main():
    """Main function"""
    system = SystemManager()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Shutdown signal received...")
        system.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start the system
    system.start_system()

if __name__ == "__main__":
    main()
