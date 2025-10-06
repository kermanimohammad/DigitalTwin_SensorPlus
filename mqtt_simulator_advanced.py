#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, argparse, json, math, random, signal, time
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from enum import Enum

def now_ms(): return int(time.time()*1000)
def clamp(v, lo, hi): return max(lo, min(hi, v))

class RoomType:
    """انواع مختلف اتاق با الگوهای سنسور متفاوت"""
    BEDROOM = "bedroom"      # اتاق خواب - دمای پایین‌تر، رطوبت متوسط
    LIVING_ROOM = "living"   # اتاق نشیمن - بیشترین فعالیت
    KITCHEN = "kitchen"      # آشپزخانه - دمای بالاتر، رطوبت متغیر
    OFFICE = "office"        # دفتر کار - دمای ثابت، تهویه بهتر
    BATHROOM = "bathroom"    # حمام - رطوبت بالا، دمای متغیر

class Season:
    """فصل‌های سال با تغییرات آب و هوا"""
    SPRING = "spring"
    SUMMER = "summer" 
    AUTUMN = "autumn"
    WINTER = "winter"

class WeatherCondition:
    """شرایط آب و هوایی"""
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    STORMY = "stormy"

class AdvancedSensorController:
    """کنترلر پیشرفته سنسورها با در نظر گیری عوامل مختلف"""
    
    def __init__(self):
        # تعطیلات ثابت
        self.holidays = [
            (1, 1),   # روز سال نو
            (12, 25), # کریسمس
            (12, 26), # روز بعد کریسمس
        ]
        
        # الگوهای سنسور برای انواع اتاق
        self.room_sensor_patterns = {
            RoomType.BEDROOM: {
                "base_temp": 20.0,      # دمای پایه
                "temp_variation": 2.0,  # تغییرات دما
                "base_humidity": 45.0,  # رطوبت پایه
                "humidity_variation": 10.0,
                "base_co2": 400,        # CO2 پایه
                "co2_variation": 50,
                "ventilation_rate": 0.3, # نرخ تهویه
                "heat_generation": 0.5   # تولید گرما
            },
            RoomType.LIVING_ROOM: {
                "base_temp": 22.0,
                "temp_variation": 3.0,
                "base_humidity": 50.0,
                "humidity_variation": 15.0,
                "base_co2": 450,
                "co2_variation": 100,
                "ventilation_rate": 0.5,
                "heat_generation": 1.0
            },
            RoomType.KITCHEN: {
                "base_temp": 24.0,
                "temp_variation": 4.0,
                "base_humidity": 60.0,
                "humidity_variation": 20.0,
                "base_co2": 500,
                "co2_variation": 150,
                "ventilation_rate": 0.8,
                "heat_generation": 2.0
            },
            RoomType.OFFICE: {
                "base_temp": 21.0,
                "temp_variation": 1.5,
                "base_humidity": 40.0,
                "humidity_variation": 8.0,
                "base_co2": 420,
                "co2_variation": 80,
                "ventilation_rate": 0.7,
                "heat_generation": 0.8
            },
            RoomType.BATHROOM: {
                "base_temp": 23.0,
                "temp_variation": 3.0,
                "base_humidity": 70.0,
                "humidity_variation": 25.0,
                "base_co2": 480,
                "co2_variation": 120,
                "ventilation_rate": 0.9,
                "heat_generation": 0.3
            }
        }
        
        # تنظیمات فصلی
        self.seasonal_adjustments = {
            Season.SPRING: {
                "temp_offset": 0, "humidity_offset": 0, "solar_multiplier": 0.8,
                "rain_probability": 0.3, "cloud_probability": 0.4
            },
            Season.SUMMER: {
                "temp_offset": 8, "humidity_offset": 15, "solar_multiplier": 1.2,
                "rain_probability": 0.2, "cloud_probability": 0.3
            },
            Season.AUTUMN: {
                "temp_offset": -2, "humidity_offset": 10, "solar_multiplier": 0.7,
                "rain_probability": 0.4, "cloud_probability": 0.5
            },
            Season.WINTER: {
                "temp_offset": -8, "humidity_offset": -10, "solar_multiplier": 0.5,
                "rain_probability": 0.3, "cloud_probability": 0.6
            }
        }
        
        # تنظیمات آب و هوا
        self.weather_effects = {
            WeatherCondition.SUNNY: {
                "solar_multiplier": 1.0, "temp_boost": 2.0, "humidity_reduction": -5.0
            },
            WeatherCondition.CLOUDY: {
                "solar_multiplier": 0.3, "temp_boost": 0.0, "humidity_reduction": 0.0
            },
            WeatherCondition.RAINY: {
                "solar_multiplier": 0.1, "temp_boost": -1.0, "humidity_reduction": 15.0
            },
            WeatherCondition.STORMY: {
                "solar_multiplier": 0.05, "temp_boost": -2.0, "humidity_reduction": 20.0
            }
        }
        
        # وضعیت آب و هوای فعلی
        self.current_weather = WeatherCondition.SUNNY
        self.weather_change_timer = 0
        self.weather_change_interval = random.uniform(1800, 7200)  # 30-120 minutes
    
    def get_current_season(self) -> str:
        """تعیین فصل فعلی بر اساس تاریخ"""
        now = datetime.now()
        month = now.month
        
        if month in [12, 1, 2]:
            return Season.WINTER
        elif month in [3, 4, 5]:
            return Season.SPRING
        elif month in [6, 7, 8]:
            return Season.SUMMER
        else:
            return Season.AUTUMN
    
    def is_holiday(self, date: datetime) -> bool:
        """بررسی تعطیل بودن روز"""
        if (date.month, date.day) in self.holidays:
            return True
        return date.weekday() >= 5  # آخر هفته
    
    def is_weekend(self, date: datetime) -> bool:
        """بررسی آخر هفته بودن"""
        return date.weekday() >= 5
    
    def update_weather(self, dt: float):
        """به‌روزرسانی وضعیت آب و هوا"""
        self.weather_change_timer += dt
        
        if self.weather_change_timer >= self.weather_change_interval:
            self.weather_change_timer = 0
            self.weather_change_interval = random.uniform(1800, 7200)
            
            # احتمال تغییر آب و هوا بر اساس فصل
            season = self.get_current_season()
            seasonal_adj = self.seasonal_adjustments[season]
            
            # محاسبه احتمال آب و هوای مختلف
            weather_probs = {
                WeatherCondition.SUNNY: 1.0 - seasonal_adj["cloud_probability"] - seasonal_adj["rain_probability"],
                WeatherCondition.CLOUDY: seasonal_adj["cloud_probability"],
                WeatherCondition.RAINY: seasonal_adj["rain_probability"] * 0.8,
                WeatherCondition.STORMY: seasonal_adj["rain_probability"] * 0.2
            }
            
            # انتخاب آب و هوای جدید
            rand = random.random()
            cumulative = 0
            for weather, prob in weather_probs.items():
                cumulative += prob
                if rand <= cumulative:
                    self.current_weather = weather
                    break
    
    def calculate_solar_power(self, current_time: datetime) -> float:
        """محاسبه قدرت خورشیدی با در نظر گیری عوامل مختلف"""
        hour = current_time.hour + current_time.minute / 60.0
        season = self.get_current_season()
        seasonal_adj = self.seasonal_adjustments[season]
        weather_effect = self.weather_effects[self.current_weather]
        
        # الگوی روزانه خورشیدی
        if 6 <= hour <= 18:  # روز
            # منحنی سینوسی برای تولید خورشیدی
            day_progress = (hour - 6) / 12  # 0 تا 1
            solar_factor = math.sin(day_progress * math.pi)
            
            # حداکثر قدرت در ظهر
            if 11 <= hour <= 13:
                solar_factor *= 1.1  # افزایش 10% در ظهر
            
            base_power = solar_factor * 1000
        else:  # شب
            base_power = 0
        
        # اعمال تنظیمات فصلی
        seasonal_multiplier = seasonal_adj["solar_multiplier"]
        
        # اعمال اثرات آب و هوا
        weather_multiplier = weather_effect["solar_multiplier"]
        
        # تغییرات تصادفی
        random_variation = random.uniform(0.9, 1.1)
        
        # محاسبه نهایی
        final_power = base_power * seasonal_multiplier * weather_multiplier * random_variation
        
        return clamp(final_power, 0, 1200)
    
    def calculate_temperature(self, room_type: str, current_time: datetime, 
                            occupancy: float, base_temp: float, dt: float) -> float:
        """محاسبه دمای اتاق با در نظر گیری عوامل مختلف"""
        pattern = self.room_sensor_patterns[room_type]
        season = self.get_current_season()
        seasonal_adj = self.seasonal_adjustments[season]
        weather_effect = self.weather_effects[self.current_weather]
        
        # دمای هدف بر اساس فصل
        target_temp = pattern["base_temp"] + seasonal_adj["temp_offset"]
        
        # اثرات آب و هوا
        weather_temp_effect = weather_effect["temp_boost"]
        
        # اثرات حضور
        occupancy_heat = occupancy * pattern["heat_generation"]
        
        # اثرات زمان روز
        hour = current_time.hour
        time_effect = 0
        if 6 <= hour <= 8:  # صبح - گرمایش
            time_effect = 1.0
        elif 14 <= hour <= 16:  # بعدازظهر - گرم‌ترین زمان
            time_effect = 2.0
        elif 22 <= hour <= 24 or 0 <= hour <= 2:  # شب - خنک‌ترین زمان
            time_effect = -1.0
        
        # محاسبه تغییر دما
        temp_change = (target_temp - base_temp) * 0.01 * dt
        temp_change += occupancy_heat * dt
        temp_change += weather_temp_effect * 0.1 * dt
        temp_change += time_effect * 0.05 * dt
        temp_change += random.uniform(-0.02, 0.02) * dt
        
        new_temp = base_temp + temp_change
        return clamp(new_temp, 15, 35)
    
    def calculate_humidity(self, room_type: str, current_time: datetime,
                          occupancy: float, base_humidity: float, dt: float) -> float:
        """محاسبه رطوبت اتاق با در نظر گیری عوامل مختلف"""
        pattern = self.room_sensor_patterns[room_type]
        season = self.get_current_season()
        seasonal_adj = self.seasonal_adjustments[season]
        weather_effect = self.weather_effects[self.current_weather]
        
        # رطوبت هدف بر اساس فصل
        target_humidity = pattern["base_humidity"] + seasonal_adj["humidity_offset"]
        
        # اثرات آب و هوا
        weather_humidity_effect = weather_effect["humidity_reduction"]
        
        # اثرات حضور (تنفس و تعریق)
        occupancy_humidity = occupancy * 5.0
        
        # اثرات زمان روز
        hour = current_time.hour
        time_effect = 0
        if 6 <= hour <= 8:  # صبح - رطوبت بالاتر
            time_effect = 5.0
        elif 14 <= hour <= 16:  # بعدازظهر - رطوبت پایین‌تر
            time_effect = -3.0
        
        # محاسبه تغییر رطوبت
        humidity_change = (target_humidity - base_humidity) * 0.02 * dt
        humidity_change += occupancy_humidity * 0.1 * dt
        humidity_change += weather_humidity_effect * 0.05 * dt
        humidity_change += time_effect * 0.1 * dt
        humidity_change += random.uniform(-0.1, 0.1) * dt
        
        new_humidity = base_humidity + humidity_change
        return clamp(new_humidity, 20, 90)
    
    def calculate_co2(self, room_type: str, current_time: datetime,
                     occupancy: float, base_co2: float, dt: float) -> float:
        """محاسبه CO2 اتاق با در نظر گیری عوامل مختلف"""
        pattern = self.room_sensor_patterns[room_type]
        
        # CO2 پایه
        target_co2 = pattern["base_co2"]
        
        # اثرات حضور (تنفس)
        occupancy_co2 = occupancy * 200.0  # هر نفر حدود 200 ppm اضافه می‌کند
        
        # نرخ تهویه
        ventilation_rate = pattern["ventilation_rate"]
        
        # اثرات زمان روز (تهویه طبیعی)
        hour = current_time.hour
        ventilation_boost = 0
        if 8 <= hour <= 18:  # ساعات کاری - تهویه بیشتر
            ventilation_boost = 0.3
        elif 22 <= hour <= 24 or 0 <= hour <= 6:  # شب - تهویه کمتر
            ventilation_boost = -0.2
        
        # محاسبه تغییر CO2
        co2_change = (target_co2 - base_co2) * 0.02 * dt
        co2_change += occupancy_co2 * dt
        co2_change -= (ventilation_rate + ventilation_boost) * (base_co2 - 400) * 0.01 * dt
        co2_change += random.uniform(-2, 2) * dt
        
        new_co2 = base_co2 + co2_change
        return clamp(new_co2, 350, 2000)

class RoomState:
    def __init__(self, room_id, room_type, temp, hum, co2):
        self.room_id = room_id
        self.room_type = room_type
        self.temp_c = temp
        self.humidity = hum
        self.co2 = co2
        self.light_on = False
        self.light_power_w = 0.0
        self.occupancy = 0
        self.sensor_controller = AdvancedSensorController()

class SolarState:
    def __init__(self): 
        self.power_w = 0.0
        self.voltage = 48.0
        self.current = 0.0
        self.efficiency = 0.0
        self.weather_condition = WeatherCondition.SUNNY

class MQTTSimAdvanced:
    def __init__(self, broker, port, prefix, qos, interval_s):
        self.broker = broker
        self.port = port
        self.prefix = prefix.rstrip("/")
        self.qos = qos
        self.interval_s = interval_s
        self.client = mqtt.Client()
        self.client.on_connect = lambda c, u, f, rc: print(f"[MQTT] Connected rc={rc}")
        self.client.on_disconnect = lambda c, u, rc: print(f"[MQTT] Disconnected rc={rc}")
        
        # ایجاد اتاق‌های مختلف با انواع مختلف
        room_configs = [
            ("room1", RoomType.BEDROOM),
            ("room2", RoomType.LIVING_ROOM),
            ("room3", RoomType.KITCHEN),
            ("room4", RoomType.OFFICE),
            ("room5", RoomType.BATHROOM)
        ]
        
        self.rooms = [
            RoomState(
                room_id, 
                room_type,
                random.uniform(20, 25), 
                random.uniform(35, 55), 
                random.uniform(400, 600)
            ) 
            for room_id, room_type in room_configs
        ]
        
        self.solar = SolarState()
        self.running = True
        self.sensor_controller = AdvancedSensorController()

    def step_room(self, r, dt):
        current_time = datetime.now()
        
        # به‌روزرسانی آب و هوا
        self.sensor_controller.update_weather(dt)
        
        # شبیه‌سازی حضور (ساده شده)
        r.occupancy = random.uniform(0.0, 1.0) if random.random() < 0.3 else 0.0
        
        # محاسبه سنسورها با الگوریتم‌های پیشرفته
        r.temp_c = self.sensor_controller.calculate_temperature(
            r.room_type, current_time, r.occupancy, r.temp_c, dt
        )
        
        r.humidity = self.sensor_controller.calculate_humidity(
            r.room_type, current_time, r.occupancy, r.humidity, dt
        )
        
        r.co2 = self.sensor_controller.calculate_co2(
            r.room_type, current_time, r.occupancy, r.co2, dt
        )
        
        # شبیه‌سازی روشنایی (ساده شده)
        hour = current_time.hour
        if 6 <= hour <= 22 and r.occupancy > 0.3:
            r.light_on = True
            r.light_power_w = 15 + random.uniform(-2, 2)
        else:
            r.light_on = False
            r.light_power_w = 0.0

    def step_solar(self, current_time):
        # محاسبه قدرت خورشیدی با الگوریتم پیشرفته
        self.solar.power_w = self.sensor_controller.calculate_solar_power(current_time)
        
        # محاسبه ولتاژ و جریان
        if self.solar.power_w > 0:
            self.solar.voltage = 48 + random.uniform(-1, 1)
            self.solar.current = self.solar.power_w / max(1, self.solar.voltage)
            self.solar.efficiency = min(1.0, self.solar.power_w / 1000)
        else:
            self.solar.voltage = 48 + random.uniform(-0.5, 0.5)
            self.solar.current = 0
            self.solar.efficiency = 0
        
        # به‌روزرسانی وضعیت آب و هوا
        self.solar.weather_condition = self.sensor_controller.current_weather

    def pub(self, topic, payload): 
        self.client.publish(topic, json.dumps(payload), qos=self.qos)
    
    def publish_room(self, r):
        ts = now_ms()
        base = f"{self.prefix}/{r.room_id}"
        i = r.room_id[-1]
        
        self.pub(f"{base}/temperature", {
            "deviceId": f"temp-{i}",
            "kind": "temperature",
            "roomId": r.room_id,
            "roomType": r.room_type,
            "ts": ts,
            "value": round(r.temp_c, 2),
            "unit": "C",
            "occupancy": round(r.occupancy, 2)
        })
        
        self.pub(f"{base}/humidity", {
            "deviceId": f"hum-{i}",
            "kind": "humidity",
            "roomId": r.room_id,
            "roomType": r.room_type,
            "ts": ts,
            "value": round(r.humidity, 1),
            "unit": "%",
            "occupancy": round(r.occupancy, 2)
        })
        
        self.pub(f"{base}/co2", {
            "deviceId": f"co2-{i}",
            "kind": "co2",
            "roomId": r.room_id,
            "roomType": r.room_type,
            "ts": ts,
            "value": int(r.co2),
            "unit": "ppm",
            "occupancy": round(r.occupancy, 2)
        })
        
        self.pub(f"{base}/light", {
            "deviceId": f"light-{i}",
            "kind": "light",
            "roomId": r.room_id,
            "roomType": r.room_type,
            "ts": ts,
            "on": r.light_on,
            "powerW": round(r.light_power_w, 1)
        })
        
        self.pub(f"{base}/occupancy", {
            "deviceId": f"occ-{i}",
            "kind": "occupancy",
            "roomId": r.room_id,
            "roomType": r.room_type,
            "ts": ts,
            "value": round(r.occupancy, 2),
            "unit": "ratio"
        })

    def publish_solar(self):
        ts = now_ms()
        season = self.sensor_controller.get_current_season()
        
        self.pub(f"{self.prefix}/solar", {
            "deviceId": "solar-plant",
            "kind": "solar",
            "ts": ts,
            "powerW": round(self.solar.power_w, 1),
            "voltage": round(self.solar.voltage, 2),
            "current": round(self.solar.current, 2),
            "efficiency": round(self.solar.efficiency, 3),
            "season": season,
            "weather": self.solar.weather_condition
        })
        
        # انتشار اطلاعات آب و هوا
        self.pub(f"{self.prefix}/weather", {
            "deviceId": "weather-station",
            "kind": "weather",
            "ts": ts,
            "condition": self.solar.weather_condition,
            "season": season,
            "solarImpact": round(self.sensor_controller.weather_effects[self.solar.weather_condition]["solar_multiplier"], 2)
        })

    def run(self, duration=None):
        # تنظیم احراز هویت فقط در صورت وجود
        mqtt_user = os.getenv("MQTT_USER", "")
        mqtt_pass = os.getenv("MQTT_PASS", "")
        if mqtt_user and mqtt_pass:
            self.client.username_pw_set(mqtt_user, mqtt_pass)
        
        # تنظیم SSL برای broker های خارجی
        if self.port == 8883:
            self.client.tls_set()
        
        self.client.connect(self.broker, self.port, keepalive=30)
        self.client.loop_start()
        t0 = time.time()
        last = t0
        
        print(f"[INFO] Starting advanced MQTT simulator with realistic sensor patterns")
        print(f"[INFO] Season: {self.sensor_controller.get_current_season()}")
        print(f"[INFO] Weather: {self.sensor_controller.current_weather}")
        print(f"[INFO] Room types: {[f'{r.room_id}({r.room_type})' for r in self.rooms]}")
        
        try:
            while True:
                now = time.time()
                dt = now - last
                last = now
                elapsed = now - t0
                current_time = datetime.now()
                
                for r in self.rooms:
                    self.step_room(r, dt)
                
                self.step_solar(current_time)
                
                for r in self.rooms:
                    self.publish_room(r)
                
                self.publish_solar()
                
                # نمایش وضعیت هر 60 ثانیه
                if int(elapsed) % 60 == 0 and int(elapsed) > 0:
                    print(f"[{current_time.strftime('%H:%M:%S')}] Status:")
                    print(f"  Weather: {self.sensor_controller.current_weather}")
                    print(f"  Solar: {self.solar.power_w:.1f}W (Efficiency: {self.solar.efficiency:.2f})")
                    for r in self.rooms:
                        print(f"  {r.room_id}({r.room_type}): T={r.temp_c:.1f}°C, H={r.humidity:.1f}%, CO2={r.co2:.0f}ppm, Occ={r.occupancy:.2f}")
                
                time.sleep(self.interval_s)
                if duration and (now - t0) >= duration:
                    break
                    
        finally:
            self.client.loop_stop()
            self.client.disconnect()

if __name__ == "__main__":
    # اولویت با ENV برای داکر؛ CLI هم پشتیبانی می‌شود
    broker = os.getenv("BROKER", "test.mosquitto.org")
    port = int(os.getenv("PORT", "1883"))
    prefix = os.getenv("PREFIX", "building/demo")
    qos = int(os.getenv("QOS", "0"))
    interval = float(os.getenv("INTERVAL", "10"))
    duration = os.getenv("DURATION", "")
    duration = int(duration) if duration else None
    
    sim = MQTTSimAdvanced(broker, port, prefix, qos, interval)
    sim.run(duration)
