# 🚀 راهنمای سریع Live Sensor System

## ⚡ شروع سریع (5 دقیقه)

### 1. نصب Dependencies
```bash
pip install -r requirements_live.txt
```

### 2. راه‌اندازی MQTT Broker
```bash
# با Docker
docker-compose -f docker-compose-live.yml up -d broker

# یا دستی
mosquitto -c mosquitto/mosquitto.conf
```

### 3. اجرای Live Dashboard
```bash
python realtime_dashboard.py
```
**باز کردن:** http://localhost:5000

### 4. اجرای Live API
```bash
python live_sensor_api.py
```
**باز کردن:** http://localhost:5001

### 5. ارسال داده تست
```bash
python mqtt_simulator.py
```

## 🎯 نتیجه

- ✅ داشبورد Real-time: http://localhost:5000
- ✅ API Live: http://localhost:5001
- ✅ داده‌های مستقیم از سنسورها (بدون دیتابیس)

## 🐳 با Docker (یک دستور)

```bash
docker-compose -f docker-compose-live.yml up --build
```

**دسترسی:**
- Dashboard: http://localhost:5000
- API: http://localhost:5001
- MQTT: localhost:1883

## 🧪 تست سیستم

```bash
python test_live_system.py
```

## 📊 مقایسه با سیستم قبلی

| سیستم | پورت | ویژگی |
|--------|------|--------|
| **Live Dashboard** | 5000 | Real-time, WebSocket |
| **Live API** | 5001 | REST API, بدون دیتابیس |
| **Database Dashboard** | 5000 | از دیتابیس می‌خواند |
| **Database API** | 5000 | از دیتابیس می‌خواند |

## 🔄 اجرای همزمان هر دو سیستم

```bash
# Terminal 1: Live System
python realtime_dashboard.py
python live_sensor_api.py

# Terminal 2: Database System  
python web_dashboard.py
python sensor_api.py
```

## 🆘 عیب‌یابی سریع

### مشکل: داده نمایش نمی‌شود
```bash
# بررسی MQTT
python mqtt_simulator.py

# بررسی اتصال
python test_live_system.py
```

### مشکل: پورت اشغال
```bash
# تغییر پورت در فایل‌ها
# realtime_dashboard.py: port=5000
# live_sensor_api.py: port=5001
```

## 📱 API Endpoints کلیدی

```bash
# آمار زنده
curl http://localhost:5001/api/live/stats

# دستگاه‌های متصل
curl http://localhost:5001/api/live/devices

# وضعیت سیستم
curl http://localhost:5001/api/live/health
```

## 🎨 ویژگی‌های داشبورد

- 🌡️ نمایش Real-time داده‌ها
- 📊 آمار زنده دستگاه‌ها
- 🔄 بروزرسانی خودکار
- 🎨 UI فارسی و مدرن
- 📱 Responsive design

---

**💡 نکته:** این سیستم برای نمایش فوری داده‌ها طراحی شده. برای ذخیره‌سازی دائمی از سیستم دیتابیس استفاده کنید.
