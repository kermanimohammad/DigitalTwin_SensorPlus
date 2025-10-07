# 🚀 راهنمای سریع سیستم ترکیبی - Hybrid System

## ⚡ شروع سریع (5 دقیقه)

### 1. نصب Dependencies
```bash
pip install -r requirements.txt
```

### 2. راه‌اندازی MQTT Broker
```bash
# با Docker
docker-compose -f docker-compose-hybrid.yml up -d broker

# یا دستی
mosquitto -c mosquitto/mosquitto.conf
```

### 3. اجرای سیستم ترکیبی

#### Terminal 1: Hybrid MQTT Subscriber
```bash
python mqtt_subscriber_hybrid.py
```

#### Terminal 2: Hybrid Dashboard
```bash
python hybrid_dashboard.py
```

#### Terminal 3: Hybrid API
```bash
python hybrid_sensor_api.py
```

#### Terminal 4: MQTT Simulator (تست)
```bash
python mqtt_simulator.py
```

## 🎯 نتیجه

- ✅ **Hybrid Dashboard**: http://localhost:5000 (Real-time + Database)
- ✅ **Hybrid API**: http://localhost:5001 (Real-time + Database)
- ✅ **Data Storage**: هم در دیتابیس + هم Real-time

## 🐳 با Docker (یک دستور)

```bash
docker-compose -f docker-compose-hybrid.yml up --build
```

**دسترسی:**
- Dashboard: http://localhost:5000
- API: http://localhost:5001
- MQTT: localhost:1883

## 🧪 تست سیستم

```bash
python test_hybrid_system.py
```

## 📊 مقایسه سیستم‌ها

| سیستم | پورت | ویژگی |
|--------|------|--------|
| **Live Only** | 5000/5001 | فقط Real-time |
| **Database Only** | 5000 | فقط دیتابیس |
| **Hybrid** | 5000/5001 | **Real-time + Database** |

## 🔄 اجرای همزمان با سیستم‌های قبلی

```bash
# Terminal 1: Hybrid System (جدید)
python mqtt_subscriber_hybrid.py
python hybrid_dashboard.py
python hybrid_sensor_api.py

# Terminal 2: Database System (قدیمی)
python mqtt_subscriber.py
python web_dashboard.py
python sensor_api.py
```

## 🆘 عیب‌یابی سریع

### مشکل: داده نمایش نمی‌شود
```bash
# بررسی MQTT
python mqtt_simulator.py

# بررسی سیستم
python test_hybrid_system.py
```

### مشکل: دیتابیس کار نمی‌کند
```bash
# بررسی دیتابیس
python test_database.py

# بررسی hybrid subscriber
python mqtt_subscriber_hybrid.py
```

### مشکل: پورت اشغال
```bash
# تغییر پورت در فایل‌ها
# hybrid_dashboard.py: port=5000
# hybrid_sensor_api.py: port=5001
```

## 📱 API Endpoints کلیدی

```bash
# آمار ترکیبی
curl http://localhost:5001/api/hybrid/stats

# دستگاه‌های Live
curl http://localhost:5001/api/hybrid/live/devices

# تاریخچه دیتابیس
curl http://localhost:5001/api/hybrid/history/device/temp-1

# وضعیت سیستم
curl http://localhost:5001/api/hybrid/health
```

## 🎨 ویژگی‌های داشبورد

### تب Live Data:
- 🌡️ نمایش Real-time داده‌ها
- 📊 آمار زنده دستگاه‌ها
- 🔄 بروزرسانی خودکار
- 💾 وضعیت ذخیره در دیتابیس

### تب History:
- 📚 تاریخچه کامل از دیتابیس
- 📋 جدول رکوردها
- 💾 قابلیت صادرات

### تب Analytics:
- 📈 نمودارهای آماری
- 🥧 توزیع انواع سنسور
- 📊 فعالیت دستگاه‌ها

## 🔧 تنظیمات سریع

### تغییر MQTT Broker:
```python
# در mqtt_subscriber_hybrid.py
hybrid_subscriber = HybridMQTTSubscriber(
    broker="your-broker-ip",
    port=1883,
    topics=["your/topic/#"]
)
```

### تغییر حافظه:
```python
# در mqtt_subscriber_hybrid.py
self.live_sensor_data = defaultdict(lambda: deque(maxlen=2000))  # تغییر از 1000 به 2000
```

## 📈 مزایای سیستم ترکیبی

1. **Real-time**: داده‌ها فوراً نمایش داده می‌شوند
2. **History**: تمام داده‌ها در دیتابیس ذخیره می‌شوند
3. **Analytics**: تحلیل کامل داده‌ها
4. **Export**: صادرات داده‌های تاریخی
5. **Reliability**: پایداری بالا با fallback

## 🎯 استفاده‌های مختلف

### برای Monitoring:
- استفاده از تب Live Data
- WebSocket برای بروزرسانی خودکار

### برای Analysis:
- استفاده از تب History
- Export داده‌ها برای تحلیل

### برای Development:
- استفاده از API endpoints
- تست با test_hybrid_system.py

---

**💡 نکته:** این سیستم بهترین ترکیب از Real-time و Database storage را ارائه می‌دهد. برای پروژه‌های production ایده‌آل است! 🎉
