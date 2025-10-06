# سیستم ذخیره‌سازی داده‌های سنسور - Sensor Data Storage System

این سیستم برای ذخیره‌سازی داده‌های سنسورهای MQTT در پایگاه داده MySQL طراحی شده است.

## ویژگی‌ها

- ✅ دریافت داده‌های MQTT از سنسورها
- ✅ ذخیره‌سازی خودکار در پایگاه داده MySQL
- ✅ داشبورد وب برای مشاهده داده‌ها
- ✅ API برای دسترسی به داده‌ها
- ✅ پشتیبانی از انواع مختلف سنسور (دما، رطوبت، CO2، نور، خورشیدی)

## ساختار پروژه

```
├── mqtt_simulator.py      # شبیه‌ساز سنسورها (ارسال داده)
├── mqtt_subscriber.py     # دریافت‌کننده MQTT (ذخیره در دیتابیس)
├── database.py           # مدیریت پایگاه داده
├── web_dashboard.py      # داشبورد وب
├── test_database.py      # تست پایگاه داده
└── docker-compose.yml    # تنظیمات Docker
```

## نصب و راه‌اندازی

### 1. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### 2. تست اتصال به پایگاه داده

```bash
python test_database.py
```

### 3. راه‌اندازی با Docker

```bash
# ساخت و اجرای تمام سرویس‌ها
docker compose up --build -d

# مشاهده لاگ‌ها
docker compose logs -f mqtt-subscriber
docker compose logs -f web-dashboard
```

### 4. دسترسی به سرویس‌ها

- **داشبورد وب**: http://localhost:5000
- **MQTT Broker**: localhost:1883
- **API**: http://localhost:5000/api/data

## استفاده

### اجرای دستی

#### 1. اجرای شبیه‌ساز سنسورها
```bash
python mqtt_simulator.py
```

#### 2. اجرای دریافت‌کننده MQTT
```bash
python mqtt_subscriber.py
```

#### 3. اجرای داشبورد وب
```bash
python web_dashboard.py
```

### اجرای با Docker

```bash
# اجرای تمام سرویس‌ها
docker compose up -d

# مشاهده وضعیت
docker compose ps

# توقف سرویس‌ها
docker compose down
```

## ساختار پایگاه داده

جدول `sensor_data` شامل فیلدهای زیر است:

| فیلد | نوع | توضیح |
|------|-----|-------|
| id | INT | شناسه یکتا |
| device_id | VARCHAR(50) | شناسه دستگاه |
| kind | VARCHAR(20) | نوع سنسور (temperature, humidity, co2, light, solar) |
| room_id | VARCHAR(20) | شناسه اتاق |
| value | FLOAT | مقدار سنسور |
| unit | VARCHAR(10) | واحد اندازه‌گیری |
| power_w | FLOAT | توان (وات) |
| voltage | FLOAT | ولتاژ |
| current | FLOAT | جریان |
| on_status | BOOLEAN | وضعیت روشن/خاموش |
| timestamp | DATETIME | زمان ثبت |
| raw_data | TEXT | داده‌های خام JSON |

## API Endpoints

### دریافت داده‌های اخیر
```http
GET /api/data
```

### دریافت داده‌های اتاق خاص
```http
GET /api/room/{room_id}
```

### دریافت داده‌های دستگاه خاص
```http
GET /api/device/{device_id}
```

## نمونه داده‌های MQTT

### داده‌های دما
```json
{
  "deviceId": "temp-1",
  "kind": "temperature",
  "roomId": "room1",
  "ts": 1703123456789,
  "value": 23.5,
  "unit": "C"
}
```

### داده‌های رطوبت
```json
{
  "deviceId": "hum-1",
  "kind": "humidity",
  "roomId": "room1",
  "ts": 1703123456789,
  "value": 45.2,
  "unit": "%"
}
```

### داده‌های CO2
```json
{
  "deviceId": "co2-1",
  "kind": "co2",
  "roomId": "room1",
  "ts": 1703123456789,
  "value": 520,
  "unit": "ppm"
}
```

### داده‌های خورشیدی
```json
{
  "deviceId": "solar-plant",
  "kind": "solar",
  "ts": 1703123456789,
  "powerW": 850.5,
  "voltage": 48.2,
  "current": 17.6
}
```

## تنظیمات محیطی

### متغیرهای محیطی MQTT
```bash
BROKER=test.mosquitto.org
PORT=1883
TOPICS=building/demo/#
QOS=0
MQTT_USER=username
MQTT_PASS=password
```

### تنظیمات پایگاه داده
اطلاعات پایگاه داده در فایل `database.py` تنظیم شده است:

```python
DB_CONFIG = {
    'host': 'kbz.rew.mybluehost.me',
    'database': 'kbzrewmy_sensor',
    'user': 'mo_kerma',
    'password': 'Mehrafarid.5435',
    'port': 3306
}
```

## عیب‌یابی

### بررسی اتصال پایگاه داده
```bash
python -c "from database import db_manager; print('DB OK' if db_manager.test_connection() else 'DB Error')"
```

### بررسی لاگ‌های MQTT
```bash
docker compose logs -f mqtt-subscriber
```

### بررسی لاگ‌های وب
```bash
docker compose logs -f web-dashboard
```

## نکات مهم

1. **امنیت**: رمز عبور پایگاه داده در کد قرار دارد. برای محیط تولید، از متغیرهای محیطی استفاده کنید.

2. **عملکرد**: برای حجم بالای داده، از connection pooling استفاده کنید.

3. **پشتیبان‌گیری**: برنامه‌ریزی منظم برای پشتیبان‌گیری از پایگاه داده انجام دهید.

4. **مانیتورینگ**: لاگ‌ها را به طور منظم بررسی کنید.

## پشتیبانی

در صورت بروز مشکل، لاگ‌های سیستم را بررسی کنید:

```bash
# لاگ‌های تمام سرویس‌ها
docker compose logs

# لاگ‌های سرویس خاص
docker compose logs mqtt-subscriber
docker compose logs web-dashboard
```
