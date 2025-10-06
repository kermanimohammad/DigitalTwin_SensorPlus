#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت تست سناریوهای روشنایی هوشمند
این اسکریپت سناریوهای مختلف روشنایی را در زمان‌های مختلف شبیه‌سازی می‌کند
"""

import sys
import os
from datetime import datetime, timedelta
import json

# اضافه کردن مسیر فعلی برای import کردن کلاس‌ها
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mqtt_simulator_enhanced import LightingController, RoomType, Season

def test_lighting_scenarios():
    """تست سناریوهای مختلف روشنایی"""
    
    controller = LightingController()
    
    print("=" * 80)
    print("تست سناریوهای روشنایی هوشمند")
    print("=" * 80)
    
    # تست در زمان‌های مختلف روز
    test_times = [
        datetime.now().replace(hour=5, minute=30, second=0),   # صبح زود
        datetime.now().replace(hour=7, minute=0, second=0),    # صبح
        datetime.now().replace(hour=9, minute=0, second=0),    # صبح دیر
        datetime.now().replace(hour=12, minute=0, second=0),   # ظهر
        datetime.now().replace(hour=15, minute=0, second=0),   # بعدازظهر
        datetime.now().replace(hour=18, minute=0, second=0),   # غروب
        datetime.now().replace(hour=20, minute=0, second=0),   # شب
        datetime.now().replace(hour=23, minute=0, second=0),   # شب دیر
        datetime.now().replace(hour=1, minute=0, second=0),    # نیمه شب
    ]
    
    room_types = [
        (RoomType.BEDROOM, "اتاق خواب"),
        (RoomType.LIVING_ROOM, "اتاق نشیمن"),
        (RoomType.KITCHEN, "آشپزخانه"),
        (RoomType.OFFICE, "دفتر کار"),
        (RoomType.BATHROOM, "حمام")
    ]
    
    print(f"فصل فعلی: {controller.get_current_season()}")
    print(f"تاریخ فعلی: {datetime.now().strftime('%Y-%m-%d %A')}")
    print(f"آخر هفته: {'بله' if controller.is_weekend(datetime.now()) else 'خیر'}")
    print(f"تعطیل: {'بله' if controller.is_holiday(datetime.now()) else 'خیر'}")
    print()
    
    for test_time in test_times:
        print(f"⏰ زمان: {test_time.strftime('%H:%M')}")
        print("-" * 50)
        
        for room_type, persian_name in room_types:
            # تست چندین بار برای دیدن تغییرات تصادفی
            results = []
            for i in range(3):
                light_on, occupancy = controller.should_light_be_on(
                    room_type, test_time, f"room{i+1}", 0.0
                )
                results.append((light_on, occupancy))
            
            # نمایش نتایج
            light_status = "🔆 روشن" if any(r[0] for r in results) else "🌙 خاموش"
            avg_occupancy = sum(r[1] for r in results) / len(results)
            
            print(f"  {persian_name:12} | {light_status:8} | حضور: {avg_occupancy:.2f}")
        
        print()

def test_seasonal_variations():
    """تست تغییرات فصلی"""
    
    print("=" * 80)
    print("تست تغییرات فصلی")
    print("=" * 80)
    
    controller = LightingController()
    
    # شبیه‌سازی فصول مختلف
    seasons = [
        (Season.SPRING, "بهار"),
        (Season.SUMMER, "تابستان"),
        (Season.AUTUMN, "پاییز"),
        (Season.WINTER, "زمستان")
    ]
    
    test_time = datetime.now().replace(hour=18, minute=0, second=0)  # غروب
    
    for season, persian_name in seasons:
        print(f"🌍 فصل: {persian_name}")
        print("-" * 30)
        
        # تغییر فصول در کنترلر (برای تست)
        original_season = controller.get_current_season()
        controller._current_season = season  # تغییر موقت برای تست
        
        for room_type, persian_room in [
            (RoomType.BEDROOM, "اتاق خواب"),
            (RoomType.LIVING_ROOM, "اتاق نشیمن"),
            (RoomType.KITCHEN, "آشپزخانه")
        ]:
            light_on, occupancy = controller.should_light_be_on(
                room_type, test_time, "test_room", 0.0
            )
            status = "🔆 روشن" if light_on else "🌙 خاموش"
            print(f"  {persian_room:12} | {status}")
        
        print()

def test_holiday_scenarios():
    """تست سناریوهای تعطیلات"""
    
    print("=" * 80)
    print("تست سناریوهای تعطیلات")
    print("=" * 80)
    
    controller = LightingController()
    
    # تست روزهای مختلف
    test_dates = [
        datetime.now().replace(month=1, day=1),    # روز سال نو
        datetime.now().replace(month=12, day=25),  # کریسمس
        datetime.now() + timedelta(days=1),        # فردا (ممکن است آخر هفته باشد)
    ]
    
    test_time = datetime.now().replace(hour=10, minute=0, second=0)  # صبح
    
    for test_date in test_dates:
        print(f"📅 تاریخ: {test_date.strftime('%Y-%m-%d %A')}")
        print(f"تعطیل: {'بله' if controller.is_holiday(test_date) else 'خیر'}")
        print(f"آخر هفته: {'بله' if controller.is_weekend(test_date) else 'خیر'}")
        print("-" * 40)
        
        for room_type, persian_name in [
            (RoomType.BEDROOM, "اتاق خواب"),
            (RoomType.OFFICE, "دفتر کار"),
            (RoomType.LIVING_ROOM, "اتاق نشیمن")
        ]:
            light_on, occupancy = controller.should_light_be_on(
                room_type, test_time, "test_room", 0.0
            )
            status = "🔆 روشن" if light_on else "🌙 خاموش"
            print(f"  {persian_name:12} | {status:8} | حضور: {occupancy:.2f}")
        
        print()

def test_room_specific_patterns():
    """تست الگوهای خاص هر اتاق"""
    
    print("=" * 80)
    print("تست الگوهای خاص هر اتاق")
    print("=" * 80)
    
    controller = LightingController()
    
    # تست در ساعات مختلف برای اتاق‌های مختلف
    hours_to_test = [6, 8, 12, 18, 22]
    
    for hour in hours_to_test:
        test_time = datetime.now().replace(hour=hour, minute=0, second=0)
        print(f"⏰ ساعت {hour:02d}:00")
        print("-" * 30)
        
        for room_type, persian_name in [
            (RoomType.BEDROOM, "اتاق خواب"),
            (RoomType.KITCHEN, "آشپزخانه"),
            (RoomType.OFFICE, "دفتر کار"),
            (RoomType.BATHROOM, "حمام"),
            (RoomType.LIVING_ROOM, "اتاق نشیمن")
        ]:
            # تست چندین بار برای دیدن الگو
            light_results = []
            for i in range(5):
                light_on, occupancy = controller.should_light_be_on(
                    room_type, test_time, f"room{i}", 0.0
                )
                light_results.append(light_on)
            
            light_probability = sum(light_results) / len(light_results)
            status = "🔆" if light_probability > 0.5 else "🌙"
            
            print(f"  {persian_name:12} | {status} احتمال: {light_probability:.2f}")
        
        print()

def generate_lighting_report():
    """تولید گزارش کامل روشنایی برای 24 ساعت"""
    
    print("=" * 80)
    print("گزارش 24 ساعته روشنایی")
    print("=" * 80)
    
    controller = LightingController()
    
    # تولید گزارش برای هر ساعت
    report_data = {}
    
    for hour in range(24):
        test_time = datetime.now().replace(hour=hour, minute=0, second=0)
        hour_data = {}
        
        for room_type in [RoomType.BEDROOM, RoomType.LIVING_ROOM, RoomType.KITCHEN, 
                         RoomType.OFFICE, RoomType.BATHROOM]:
            light_on, occupancy = controller.should_light_be_on(
                room_type, test_time, "report_room", 0.0
            )
            hour_data[room_type] = {
                "light_on": light_on,
                "occupancy": occupancy
            }
        
        report_data[hour] = hour_data
    
    # نمایش گزارش
    print("ساعت | اتاق خواب | نشیمن | آشپزخانه | دفتر | حمام")
    print("-" * 60)
    
    for hour in range(24):
        hour_data = report_data[hour]
        line = f"{hour:02d}:00 |"
        
        for room_type in [RoomType.BEDROOM, RoomType.LIVING_ROOM, RoomType.KITCHEN, 
                         RoomType.OFFICE, RoomType.BATHROOM]:
            status = "🔆" if hour_data[room_type]["light_on"] else "🌙"
            line += f"    {status}    |"
        
        print(line)

if __name__ == "__main__":
    print("🚀 شروع تست سناریوهای روشنایی هوشمند")
    print()
    
    try:
        test_lighting_scenarios()
        test_seasonal_variations()
        test_holiday_scenarios()
        test_room_specific_patterns()
        generate_lighting_report()
        
        print("=" * 80)
        print("✅ تمام تست‌ها با موفقیت انجام شد!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ خطا در اجرای تست‌ها: {e}")
        import traceback
        traceback.print_exc()
