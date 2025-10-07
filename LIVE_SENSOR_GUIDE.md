# راهنمای Live Sensor Dashboard و API

این راهنما نحوه استفاده از سیستم نمایش داده‌های مستقیم از سنسورها (بدون وابستگی به دیتابیس) را توضیح می‌دهد.

## 🎯 ویژگی‌ها

- ✅ **داده‌های Real-time**: نمایش مستقیم از MQTT بدون ذخیره در دیتابیس
- ✅ **WebSocket**: بروزرسانی خودکار داشبورد
- ✅ **API کامل**: دسترسی به داده‌های live از طریق REST API
- ✅ **آمار زنده**: شمارش دستگاه‌ها و انواع سنسورها
- ✅ **تاریخچه**: نگهداری آخرین 1000 رکورد هر دستگاه در حافظه
- ✅ **UI زیبا**: داشبورد فارسی با طراحی مدرن

## 🚀 نصب و راه‌اندازی

### 1. نصب Dependencies

```bash
pip install -r requirements_live.txt
```

### 2. راه‌اندازی MQTT Broker

```bash
# با Docker
docker-compose up -d broker

# یا اجرای دستی Mosquitto
mosquitto -c mosquitto/mosquitto.conf
```

### 3. اجرای Live Dashboard

```bash
python realtime_dashboard.py
```

**دسترسی:**
- داشبورد: http://localhost:5000
- WebSocket: ws://localhost:5000/socket.io/

### 4. اجرای Live API

```bash
python live_sensor_api.py
```

**دسترسی:**
- API: http://localhost:5001
- مستندات: http://localhost:5001/

## 📊 Live Dashboard

### ویژگی‌های داشبورد:

- **نمایش Real-time**: داده‌ها به محض دریافت از MQTT نمایش داده می‌شوند
- **وضعیت اتصال**: نشانگر آنلاین/آفلاین دستگاه‌ها
- **شمارش دستگاه‌ها**: تعداد دستگاه‌های متصل
- **تاریخچه**: آخرین بروزرسانی هر دستگاه
- **کنترل‌ها**: پاک کردن داده‌ها و توقف/شروع بروزرسانی

### نحوه استفاده:

1. داشبورد را باز کنید: http://localhost:5000
2. سنسورها را راه‌اندازی کنید (mqtt_simulator.py)
3. داده‌ها به صورت خودکار نمایش داده می‌شوند

## 🔌 Live API

### Endpoints موجود:

#### 1. آمار کلی
```http
GET /api/live/stats
```

**پاسخ:**
```json
{
  "success": true,
  "stats": {
    "total_devices": 5,
    "active_devices": 4,
    "sensor_type_counts": {
      "temperature": 2,
      "humidity": 1,
      "light": 1
    },
    "room_counts": {
      "room1": 3,
      "room2": 1
    },
    "device_list": ["temp-1", "temp-2", "hum-1"],
    "timestamp": "2024-01-15T10:30:00",
    "data_source": "live_mqtt"
  }
}
```

#### 2. لیست دستگاه‌ها
```http
GET /api/live/devices
```

#### 3. داده دستگاه خاص
```http
GET /api/live/device/{device_id}
```

#### 4. تاریخچه دستگاه
```http
GET /api/live/device/{device_id}/history?limit=50
```

#### 5. داده اتاق
```http
GET /api/live/room/{room_id}
```

#### 6. داده نوع سنسور
```http
GET /api/live/sensors/{sensor_type}
```

#### 7. وضعیت سیستم
```http
GET /api/live/health
```

## 🧪 تست سیستم

### 1. اجرای شبیه‌ساز سنسورها

```bash
python mqtt_simulator.py
```

### 2. تست API با curl

```bash
# آمار کلی
curl http://localhost:5001/api/live/stats

# دستگاه‌های متصل
curl http://localhost:5001/api/live/devices

# داده دستگاه خاص
curl http://localhost:5001/api/live/device/temp-1
```

### 3. تست WebSocket

```javascript
// در مرورگر (Console)
const socket = io('http://localhost:5000');
socket.on('sensor_data', (data) => {
    console.log('New sensor data:', data);
});
```

## 🔧 تنظیمات

### تغییر MQTT Broker

در فایل‌های `realtime_dashboard.py` و `live_sensor_api.py`:

```python
mqtt_subscriber = LiveMQTTSubscriber(
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

## 📈 مقایسه با سیستم دیتابیس

| ویژگی | Live System | Database System |
|--------|-------------|-----------------|
| **سرعت** | ⚡ فوری | 🐌 تاخیر ذخیره/خواندن |
| **حافظه** | 💾 محدود (1000 رکورد) | 💾 نامحدود |
| **پایداری** | ⚠️ موقت | ✅ دائمی |
| **تحلیل** | 📊 ساده | 📊 پیشرفته |
| **Backup** | ❌ ندارد | ✅ دارد |

## 🚨 نکات مهم

1. **حافظه**: داده‌ها فقط در حافظه نگهداری می‌شوند
2. **پایداری**: با restart سرور، داده‌ها از بین می‌روند
3. **مقیاس‌پذیری**: برای تعداد محدود دستگاه مناسب است
4. **امنیت**: فعلاً authentication ندارد

## 🔄 ترکیب با سیستم دیتابیس

می‌توانید هر دو سیستم را همزمان اجرا کنید:

```bash
# Terminal 1: Live Dashboard
python realtime_dashboard.py

# Terminal 2: Live API  
python live_sensor_api.py

# Terminal 3: Database System
python web_dashboard.py

# Terminal 4: MQTT Subscriber (برای دیتابیس)
python mqtt_subscriber.py
```

## 🐛 عیب‌یابی

### مشکل: داده‌ای نمایش داده نمی‌شود

1. MQTT Broker در حال اجرا است؟
2. سنسورها داده ارسال می‌کنند؟
3. موضوعات MQTT درست تنظیم شده؟

### مشکل: WebSocket متصل نمی‌شود

1. پورت 5000 آزاد است؟
2. Firewall مسدود نکرده؟
3. Browser از WebSocket پشتیبانی می‌کند؟

### مشکل: API پاسخ نمی‌دهد

1. پورت 5001 آزاد است؟
2. MQTT Subscriber متصل است؟
3. لاگ‌های خطا را بررسی کنید

## 📞 پشتیبانی

برای سوالات و مشکلات:
- بررسی لاگ‌های console
- تست اتصال MQTT با `mqtt-test.html`
- بررسی وضعیت با `/api/live/health`
