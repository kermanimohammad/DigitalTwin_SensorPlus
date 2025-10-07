# راهنمای سیستم ترکیبی سنسورها - Hybrid Sensor System

این راهنما نحوه استفاده از سیستم ترکیبی سنسورها را توضیح می‌دهد که **هم Real-time** و **هم دیتابیس** را ترکیب می‌کند.

## 🎯 ویژگی‌های سیستم ترکیبی

- ✅ **Real-time Display**: نمایش فوری داده‌ها از MQTT
- ✅ **Database Storage**: ذخیره‌سازی در دیتابیس برای تاریخچه
- ✅ **Hybrid API**: API ترکیبی برای دسترسی به هر دو منبع
- ✅ **Analytics**: تحلیل داده‌های ترکیبی
- ✅ **Export**: صادرات داده‌های تاریخی
- ✅ **WebSocket**: بروزرسانی خودکار داشبورد

## 🏗️ معماری سیستم

```
Sensors (MQTT) → Hybrid Subscriber → Database + Live Memory
                                    ↓
                            Dashboard + API
```

### جریان داده:
1. **سنسورها** داده را از طریق MQTT ارسال می‌کنند
2. **Hybrid Subscriber** داده را دریافت می‌کند
3. **همزمان** داده در دیتابیس ذخیره می‌شود (برای تاریخچه)
4. **و** در حافظه نگهداری می‌شود (برای Real-time)
5. **Dashboard** و **API** از هر دو منبع استفاده می‌کنند

## 🚀 نصب و راه‌اندازی

### 1. نصب Dependencies

```bash
pip install -r requirements.txt
```

### 2. راه‌اندازی MQTT Broker

```bash
# با Docker
docker-compose up -d broker

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

## 📊 دسترسی‌ها

- **Hybrid Dashboard**: http://localhost:5000
- **Hybrid API**: http://localhost:5001
- **MQTT Broker**: localhost:1883

## 🔌 Hybrid API Endpoints

### 1. آمار ترکیبی
```http
GET /api/hybrid/stats
```

**پاسخ:**
```json
{
  "success": true,
  "stats": {
    "live": {
      "total_devices": 5,
      "active_devices": 4,
      "sensor_type_counts": {"temperature": 2, "humidity": 1},
      "global_stats": {"total_messages": 150, "db_success_rate": 98.5}
    },
    "database": {
      "total_records": 1000,
      "unique_devices": 5,
      "unique_rooms": 3
    },
    "combined": {
      "data_source": "hybrid_live_database",
      "mqtt_status": "connected",
      "database_status": "connected"
    }
  }
}
```

### 2. دستگاه‌های Live
```http
GET /api/hybrid/live/devices
```

### 3. داده Live دستگاه خاص
```http
GET /api/hybrid/live/device/{device_id}
```

### 4. تاریخچه دستگاه از دیتابیس
```http
GET /api/hybrid/history/device/{device_id}?limit=50
```

### 5. داده اتاق (Live + History)
```http
GET /api/hybrid/room/{room_id}
```

### 6. داده نوع سنسور
```http
GET /api/hybrid/sensors/{sensor_type}
```

### 7. Analytics ترکیبی
```http
GET /api/hybrid/analytics
```

### 8. Export داده‌ها
```http
GET /api/hybrid/export?device=temp-1&limit=1000
```

### 9. وضعیت سیستم
```http
GET /api/hybrid/health
```

## 🎨 داشبورد ترکیبی

### تب‌های داشبورد:

#### 1. **Live Data** 📡
- نمایش Real-time داده‌ها
- وضعیت اتصال دستگاه‌ها
- نرخ موفقیت ذخیره در دیتابیس
- بروزرسانی خودکار

#### 2. **History** 📊
- تاریخچه داده‌ها از دیتابیس
- جدول کامل رکوردها
- قابلیت صادرات

#### 3. **Analytics** 📈
- نمودارهای آماری
- توزیع انواع سنسور
- فعالیت دستگاه‌ها

### ویژگی‌های داشبورد:

- **Status Bar**: نمایش آمار کلی
- **Real-time Updates**: بروزرسانی خودکار
- **Database Status**: وضعیت ذخیره‌سازی
- **Export**: صادرات داده‌ها
- **Responsive**: طراحی واکنش‌گرا

## 🧪 تست سیستم

### تست کامل:
```bash
python test_hybrid_system.py
```

### تست‌های جداگانه:

#### 1. تست MQTT
```bash
python mqtt-test.html
```

#### 2. تست دیتابیس
```bash
python test_database.py
```

#### 3. تست API
```bash
curl http://localhost:5001/api/hybrid/health
```

## 📈 مقایسه سیستم‌ها

| ویژگی | Live Only | Database Only | **Hybrid** |
|--------|-----------|---------------|------------|
| **Real-time** | ✅ | ❌ | ✅ |
| **History** | ❌ | ✅ | ✅ |
| **Analytics** | ⚠️ محدود | ✅ | ✅ |
| **Export** | ❌ | ✅ | ✅ |
| **Persistence** | ❌ | ✅ | ✅ |
| **Performance** | ⚡ بالا | 🐌 متوسط | ⚡ بالا |

## 🔧 تنظیمات

### تغییر MQTT Broker

در فایل‌های `mqtt_subscriber_hybrid.py`:

```python
hybrid_subscriber = HybridMQTTSubscriber(
    broker="your-broker-ip",  # تغییر IP
    port=1883,                # تغییر پورت
    topics=["your/topic/#"]   # تغییر موضوعات
)
```

### تغییر پورت‌ها

```python
# Dashboard
socketio.run(app, host='0.0.0.0', port=5000)

# API
app.run(host='0.0.0.0', port=5001)
```

### تنظیم حافظه

```python
# در mqtt_subscriber_hybrid.py
self.live_sensor_data = defaultdict(lambda: deque(maxlen=1000))  # تغییر تعداد
```

## 🐳 Docker Setup

### فایل docker-compose-hybrid.yml:

```yaml
version: "3.9"

services:
  broker:
    image: eclipse-mosquitto:2
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf

  hybrid-subscriber:
    build: .
    command: python mqtt_subscriber_hybrid.py
    depends_on:
      - broker

  hybrid-dashboard:
    build: .
    ports:
      - "5000:5000"
    command: python hybrid_dashboard.py
    depends_on:
      - hybrid-subscriber

  hybrid-api:
    build: .
    ports:
      - "5001:5001"
    command: python hybrid_sensor_api.py
    depends_on:
      - hybrid-subscriber

  mqtt-sim:
    build: .
    command: python mqtt_simulator.py
    depends_on:
      - broker
```

### اجرا:
```bash
docker-compose -f docker-compose-hybrid.yml up --build
```

## 🚨 نکات مهم

### 1. **Thread Safety**
- تمام عملیات حافظه thread-safe هستند
- استفاده از locks برای امنیت

### 2. **Memory Management**
- حداکثر 1000 رکورد در حافظه
- حافظه خودکار پاک می‌شود

### 3. **Database Performance**
- استفاده از connection pooling
- Batch operations برای کارایی بهتر

### 4. **Error Handling**
- مدیریت خطاهای MQTT
- مدیریت خطاهای دیتابیس
- Fallback mechanisms

## 🔄 Migration از سیستم‌های قبلی

### از Live System:
```bash
# متوقف کردن live system
# اجرای hybrid system
python mqtt_subscriber_hybrid.py
python hybrid_dashboard.py
python hybrid_sensor_api.py
```

### از Database System:
```bash
# متوقف کردن database system
# اجرای hybrid system
python mqtt_subscriber_hybrid.py
python hybrid_dashboard.py
python hybrid_sensor_api.py
```

## 📊 Monitoring

### لاگ‌های مهم:

```bash
# MQTT Subscriber
tail -f logs/mqtt_subscriber.log

# Dashboard
tail -f logs/dashboard.log

# API
tail -f logs/api.log
```

### Metrics:

- **MQTT Messages/sec**: تعداد پیام‌های دریافتی
- **DB Success Rate**: نرخ موفقیت ذخیره‌سازی
- **Active Devices**: تعداد دستگاه‌های فعال
- **Memory Usage**: استفاده از حافظه

## 🆘 عیب‌یابی

### مشکل: داده در دیتابیس ذخیره نمی‌شود

1. بررسی اتصال دیتابیس:
```bash
python test_database.py
```

2. بررسی لاگ‌های MQTT Subscriber:
```bash
python mqtt_subscriber_hybrid.py
```

### مشکل: داده Real-time نمایش نمی‌شود

1. بررسی MQTT Broker:
```bash
python mqtt-test.html
```

2. بررسی WebSocket:
```javascript
// در browser console
const socket = io('http://localhost:5000');
socket.on('connect', () => console.log('Connected'));
```

### مشکل: API پاسخ نمی‌دهد

1. بررسی پورت‌ها:
```bash
netstat -an | grep :5001
```

2. بررسی health endpoint:
```bash
curl http://localhost:5001/api/hybrid/health
```

## 📞 پشتیبانی

برای سوالات و مشکلات:
- بررسی لاگ‌های console
- تست با `test_hybrid_system.py`
- بررسی health endpoints
- تست جداگانه هر component

---

**💡 نکته:** این سیستم بهترین ترکیب از Real-time و Database storage را ارائه می‌دهد. برای پروژه‌های production توصیه می‌شود.
