#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, argparse, json, math, random, signal, time
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

def now_ms(): return int(time.time()*1000)
def clamp(v, lo, hi): return max(lo, min(hi, v))

class RoomType:
    """انواع مختلف اتاق با الگوهای روشنایی متفاوت"""
    BEDROOM = "bedroom"      # اتاق خواب - زود خاموش، دیر روشن
    LIVING_ROOM = "living"   # اتاق نشیمن - بیشترین استفاده
    KITCHEN = "kitchen"      # آشپزخانه - صبح زود و عصر
    OFFICE = "office"        # دفتر کار - ساعات کاری
    BATHROOM = "bathroom"    # حمام - کوتاه مدت

class Season:
    """فصل‌های سال با تغییرات ساعات روشنایی"""
    SPRING = "spring"
    SUMMER = "summer" 
    AUTUMN = "autumn"
    WINTER = "winter"

class LightingController:
    """کنترلر هوشمند روشنایی با در نظر گیری عوامل مختلف"""
    
    def __init__(self):
        # تعطیلات ثابت
        self.holidays = [
            (1, 1),   # روز سال نو
            (12, 25), # کریسمس
            (12, 26), # روز بعد کریسمس
        ]
        
        # الگوهای روشنایی برای انواع اتاق
        self.room_patterns = {
            RoomType.BEDROOM: {
                "morning_start": 6.5,    # 6:30 صبح
                "morning_end": 8.0,      # 8:00 صبح
                "evening_start": 19.0,   # 7:00 عصر
                "evening_end": 23.0,     # 11:00 شب
                "weekend_delay": 1.0,    # تعطیلات 1 ساعت دیرتر
                "random_variation": 0.5, # تغییر تصادفی ±30 دقیقه
                "occupancy_probability": 0.7  # احتمال استفاده
            },
            RoomType.LIVING_ROOM: {
                "morning_start": 6.0,
                "morning_end": 9.0,
                "evening_start": 17.0,
                "evening_end": 24.0,
                "weekend_delay": 0.5,
                "random_variation": 0.8,
                "occupancy_probability": 0.9
            },
            RoomType.KITCHEN: {
                "morning_start": 5.5,
                "morning_end": 8.5,
                "evening_start": 18.0,
                "evening_end": 21.0,
                "weekend_delay": 1.5,
                "random_variation": 0.3,
                "occupancy_probability": 0.8
            },
            RoomType.OFFICE: {
                "morning_start": 7.0,
                "morning_end": 18.0,
                "evening_start": 19.0,
                "evening_end": 22.0,
                "weekend_delay": 2.0,
                "random_variation": 0.2,
                "occupancy_probability": 0.3  # کمتر در تعطیلات
            },
            RoomType.BATHROOM: {
                "morning_start": 6.0,
                "morning_end": 8.0,
                "evening_start": 19.0,
                "evening_end": 23.0,
                "weekend_delay": 1.0,
                "random_variation": 1.0,
                "occupancy_probability": 0.6
            }
        }
        
        # تنظیمات فصلی
        self.seasonal_adjustments = {
            Season.SPRING: {"sunrise_offset": 0, "sunset_offset": 0},
            Season.SUMMER: {"sunrise_offset": -1.5, "sunset_offset": 2.0},  # زودتر طلوع، دیرتر غروب
            Season.AUTUMN: {"sunrise_offset": 1.0, "sunset_offset": -1.0},
            Season.WINTER: {"sunrise_offset": 2.0, "sunset_offset": -2.5}   # دیرتر طلوع، زودتر غروب
        }
    
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
        # تعطیلات ثابت
        if (date.month, date.day) in self.holidays:
            return True
        
        # تعطیلات آخر هفته
        if date.weekday() >= 5:  # شنبه و یکشنبه
            return True
            
        return False
    
    def is_weekend(self, date: datetime) -> bool:
        """بررسی آخر هفته بودن"""
        return date.weekday() >= 5
    
    def should_light_be_on(self, room_type: str, current_time: datetime, 
                          room_id: str, base_occupancy: float = 0.0) -> Tuple[bool, float]:
        """
        تعیین وضعیت روشنایی بر اساس عوامل مختلف
        Returns: (should_be_on, occupancy_level)
        """
        pattern = self.room_patterns[room_type]
        season = self.get_current_season()
        seasonal_adj = self.seasonal_adjustments[season]
        is_holiday = self.is_holiday(current_time)
        is_weekend = self.is_weekend(current_time)
        
        # محاسبه ساعت فعلی
        current_hour = current_time.hour + current_time.minute / 60.0
        
        # اعمال تنظیمات فصلی
        morning_start = pattern["morning_start"] + seasonal_adj["sunrise_offset"]
        morning_end = pattern["morning_end"] + seasonal_adj["sunrise_offset"]
        evening_start = pattern["evening_start"] + seasonal_adj["sunset_offset"]
        evening_end = pattern["evening_end"] + seasonal_adj["sunset_offset"]
        
        # اعمال تاخیر تعطیلات
        if is_holiday or is_weekend:
            morning_start += pattern["weekend_delay"]
            morning_end += pattern["weekend_delay"]
            evening_start += pattern["weekend_delay"]
            evening_end += pattern["weekend_delay"]
        
        # تغییرات تصادفی
        random_offset = random.uniform(-pattern["random_variation"], 
                                     pattern["random_variation"])
        morning_start += random_offset
        evening_start += random_offset
        
        # احتمال استفاده از اتاق
        occupancy_prob = pattern["occupancy_probability"]
        if is_holiday or is_weekend:
            if room_type == RoomType.OFFICE:
                occupancy_prob *= 0.3  # دفتر کمتر استفاده می‌شود
            else:
                occupancy_prob *= 1.2  # سایر اتاق‌ها بیشتر
        
        # شبیه‌سازی حضور تصادفی
        room_hash = hash(room_id + str(current_time.date()))
        random.seed(room_hash)
        is_occupied = random.random() < occupancy_prob
        
        # تعیین وضعیت روشنایی
        light_on = False
        occupancy_level = 0.0
        
        if is_occupied:
            # دوره صبح
            if morning_start <= current_hour <= morning_end:
                light_on = True
                occupancy_level = 0.8 + random.uniform(-0.2, 0.2)
            
            # دوره عصر/شب
            elif evening_start <= current_hour <= evening_end:
                light_on = True
                occupancy_level = 0.9 + random.uniform(-0.1, 0.1)
            
            # حالت‌های خاص
            elif room_type == RoomType.BATHROOM:
                # حمام ممکن است در هر ساعتی استفاده شود
                if random.random() < 0.1:  # 10% احتمال
                    light_on = True
                    occupancy_level = 0.6
            
            elif room_type == RoomType.KITCHEN and 11 <= current_hour <= 14:
                # آشپزخانه در ناهار
                if random.random() < 0.3:
                    light_on = True
                    occupancy_level = 0.7
        
        # اضافه کردن حضور پایه (مثلاً برای سیستم‌های هوشمند)
        if base_occupancy > 0.1:
            light_on = True
            occupancy_level = max(occupancy_level, base_occupancy)
        
        return light_on, clamp(occupancy_level, 0.0, 1.0)

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
        self.lighting_controller = LightingController()

class SolarState:
    def __init__(self): 
        self.power_w = 0.0
        self.voltage = 48.0
        self.current = 0.0

class MQTTSimEnhanced:
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
                random.uniform(21, 24), 
                random.uniform(30, 45), 
                random.uniform(450, 650)
            ) 
            for room_id, room_type in room_configs
        ]
        
        self.solar = SolarState()
        self.running = True
        self.lighting_controller = LightingController()

    def step_room(self, r, dt):
        # محاسبه وضعیت روشنایی هوشمند
        current_time = datetime.now()
        light_should_be_on, occupancy_level = self.lighting_controller.should_light_be_on(
            r.room_type, current_time, r.room_id, r.occupancy
        )
        
        # به‌روزرسانی وضعیت روشنایی
        r.light_on = light_should_be_on
        r.occupancy = occupancy_level
        
        # محاسبه مصرف برق روشنایی
        if r.light_on:
            # مصرف برق متفاوت برای انواع مختلف اتاق
            base_power = {
                RoomType.BEDROOM: 15,
                RoomType.LIVING_ROOM: 25,
                RoomType.KITCHEN: 20,
                RoomType.OFFICE: 18,
                RoomType.BATHROOM: 12
            }
            r.light_power_w = base_power[r.room_type] + random.uniform(-2, 2)
        else:
            r.light_power_w = 0.0
        
        # شبیه‌سازی دما (تأثیر روشنایی و حضور)
        temp_influence = 0.0
        if r.light_on:
            temp_influence += 0.5  # روشنایی گرما تولید می‌کند
        if r.occupancy > 0.5:
            temp_influence += 0.3 * r.occupancy  # حضور انسان گرما تولید می‌کند
        
        r.temp_c += (22.0 - r.temp_c) * 0.01 * dt + temp_influence * dt + random.uniform(-0.02, 0.02)
        r.temp_c = clamp(r.temp_c, 16, 32)
        
        # شبیه‌سازی رطوبت
        target_h = 40 + min(15, 2 * r.occupancy)
        r.humidity += (target_h - r.humidity) * 0.02 * dt + random.uniform(-0.1, 0.1)
        r.humidity = clamp(r.humidity, 20, 80)
        
        # شبیه‌سازی CO2
        r.co2 += (420 - r.co2) * 0.02 * dt + r.occupancy * 8 * dt + random.uniform(-2, 2)
        r.co2 = clamp(r.co2, 350, 3000)

    def step_solar(self, t):
        # شبیه‌سازی خورشیدی با الگوی روزانه واقعی‌تر
        current_time = datetime.now()
        hour = current_time.hour + current_time.minute / 60.0
        
        # الگوی خورشیدی بر اساس ساعت روز
        if 6 <= hour <= 18:  # روز
            # منحنی سینوسی برای تولید خورشیدی
            day_progress = (hour - 6) / 12  # 0 تا 1
            solar_factor = math.sin(day_progress * math.pi)
            base_power = solar_factor * 1000
        else:  # شب
            base_power = 0
        
        # تغییرات فصلی
        season = self.lighting_controller.get_current_season()
        seasonal_multiplier = {
            Season.SPRING: 0.8,
            Season.SUMMER: 1.2,
            Season.AUTUMN: 0.7,
            Season.WINTER: 0.5
        }
        
        p = base_power * seasonal_multiplier[season] + random.uniform(-20, 20)
        self.solar.power_w = clamp(p, 0, 1100)
        self.solar.voltage = 48 + random.uniform(-0.5, 0.5)
        self.solar.current = self.solar.power_w / max(1, self.solar.voltage)

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
            "unit": "C"
        })
        
        self.pub(f"{base}/humidity", {
            "deviceId": f"hum-{i}",
            "kind": "humidity",
            "roomId": r.room_id,
            "roomType": r.room_type,
            "ts": ts,
            "value": round(r.humidity, 1),
            "unit": "%"
        })
        
        self.pub(f"{base}/co2", {
            "deviceId": f"co2-{i}",
            "kind": "co2",
            "roomId": r.room_id,
            "roomType": r.room_type,
            "ts": ts,
            "value": int(r.co2),
            "unit": "ppm"
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
        season = self.lighting_controller.get_current_season()
        
        self.pub(f"{self.prefix}/solar", {
            "deviceId": "solar-plant",
            "kind": "solar",
            "ts": ts,
            "powerW": round(self.solar.power_w, 1),
            "voltage": round(self.solar.voltage, 2),
            "current": round(self.solar.current, 2),
            "season": season
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
        
        print(f"[INFO] Starting enhanced MQTT simulator with realistic lighting scenarios")
        print(f"[INFO] Season: {self.lighting_controller.get_current_season()}")
        print(f"[INFO] Room types: {[f'{r.room_id}({r.room_type})' for r in self.rooms]}")
        
        try:
            while True:
                now = time.time()
                dt = now - last
                last = now
                elapsed = now - t0
                
                for r in self.rooms:
                    self.step_room(r, dt)
                
                self.step_solar(elapsed)
                
                for r in self.rooms:
                    self.publish_room(r)
                
                self.publish_solar()
                
                # نمایش وضعیت هر 60 ثانیه
                if int(elapsed) % 60 == 0 and int(elapsed) > 0:
                    current_time = datetime.now()
                    print(f"[{current_time.strftime('%H:%M:%S')}] Room status:")
                    for r in self.rooms:
                        status = "ON" if r.light_on else "OFF"
                        print(f"  {r.room_id}({r.room_type}): Light {status}, Occupancy: {r.occupancy:.2f}")
                
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
    
    sim = MQTTSimEnhanced(broker, port, prefix, qos, interval)
    sim.run(duration)
