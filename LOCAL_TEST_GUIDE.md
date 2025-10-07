# راهنمای تست محلی - Local Testing Guide

## 🚀 شروع سریع (3 دقیقه)

### 1. نصب Dependencies
```bash
pip install flask-socketio paho-mqtt flask-cors
```

### 2. اجرای سیستم

#### Terminal 1: Dashboard
```bash
python simple_dashboard.py
```

#### Terminal 2: MQTT Simulator (اختیاری)
```bash
python simple_mqtt_simulator.py
```

### 3. تست سیستم
```bash
python test_complete_system.py
```

## 🎯 نتیجه

- ✅ **Dashboard**: http://localhost:5000
- ✅ **API**: http://localhost:5000/api/data
- ✅ **MQTT**: test.mosquitto.org:1883

## 🧪 تست‌های موجود

### 1. تست MQTT
```bash
python test_simple_mqtt.py
```

### 2. تست کامل سیستم
```bash
python test_complete_system.py
```

### 3. تست MQTT Subscriber
```bash
python simple_mqtt_subscriber.py
```

## 📊 بررسی نتایج

### Dashboard API:
```bash
curl http://localhost:5000/api/data
```

**پاسخ موفق:**
```json
{
  "count": 3,
  "devices": {
    "temp-1": {
      "kind": "temperature",
      "value": 25.5,
      "unit": "°C",
      "timestamp": "2024-01-15T10:30:00"
    }
  },
  "success": true
}
```

## 🔧 عیب‌یابی

### مشکل: Dashboard باز نمی‌شود
```bash
# بررسی پورت
netstat -an | findstr :5000

# تغییر پورت در simple_dashboard.py
socketio.run(app, host='0.0.0.0', port=5001)  # تغییر از 5000 به 5001
```

### مشکل: داده نمایش نمی‌شود
```bash
# تست MQTT
python test_simple_mqtt.py

# تست کامل
python test_complete_system.py
```

### مشکل: MQTT متصل نمی‌شود
```bash
# بررسی اینترنت
ping test.mosquitto.org

# استفاده از broker محلی (اگر Docker دارید)
# docker run -d -p 1883:1883 eclipse-mosquitto:2
```

## 📱 ویژگی‌های Dashboard

- 🌡️ نمایش Real-time داده‌ها
- 📊 آمار دستگاه‌ها
- 🔄 بروزرسانی خودکار
- 🎨 UI فارسی و مدرن
- 📱 Responsive design

## 🔄 جریان داده

```
MQTT Simulator → test.mosquitto.org → Dashboard → Browser
```

## 📋 فایل‌های تست

- `test_simple_mqtt.py` - تست اتصال MQTT
- `test_complete_system.py` - تست کامل سیستم
- `simple_mqtt_simulator.py` - شبیه‌ساز سنسورها
- `simple_mqtt_subscriber.py` - دریافت‌کننده MQTT
- `simple_dashboard.py` - داشبورد ساده

## 🎯 مراحل تست

1. **اجرای Dashboard**: `python simple_dashboard.py`
2. **تست API**: `curl http://localhost:5000/api/data`
3. **ارسال داده**: `python test_complete_system.py`
4. **بررسی Dashboard**: باز کردن http://localhost:5000
5. **تست Real-time**: اجرای `python simple_mqtt_simulator.py`

## 🚨 نکات مهم

- **MQTT Broker**: از test.mosquitto.org استفاده می‌شود
- **Topic Pattern**: `building/demo/{kind}/{device_id}`
- **Data Format**: JSON با فیلدهای deviceId, kind, value, unit, roomId, ts
- **Port**: Dashboard روی پورت 5000 اجرا می‌شود

## 🎉 موفقیت

اگر همه تست‌ها موفق باشند:
- Dashboard باز می‌شود
- داده‌ها Real-time نمایش داده می‌شوند
- API پاسخ می‌دهد
- WebSocket کار می‌کند

---

**💡 نکته:** این سیستم ساده برای تست و توسعه است. برای production از سیستم ترکیبی استفاده کنید.
