<<<<<<< Updated upstream
# راهنمای یکپارچگی فرانت‌اند و بک‌اند

## 🔗 **Endpoint های جدید برای فرانت‌اند**

### **1. Proxy Endpoint**
```
GET /api/proxy/data
```
- **هدف**: هماهنگی با فرانت‌اند
- **پاسخ**: داده‌های سنسورها با فرمت سازگار
- **استفاده**: فرانت‌اند می‌تواند از این endpoint استفاده کند

### **2. Health Check**
```
GET /api/health
```
- **هدف**: بررسی وضعیت سیستم
- **پاسخ**: وضعیت پایگاه داده، شبیه‌ساز و دستگاه‌ها

### **3. لیست دستگاه‌ها**
```
GET /api/devices
```
- **هدف**: دریافت لیست تمام دستگاه‌ها
- **پاسخ**: اطلاعات کلی تمام سنسورها

### **4. جزئیات دستگاه**
```
GET /api/devices/<device_id>
```
- **هدف**: دریافت اطلاعات جزئی یک دستگاه
- **پاسخ**: داده‌های کامل یک سنسور

### **5. تاریخچه سنسور**
```
GET /api/history/<sensor_type>/<device_id>?hours=24
```
- **هدف**: دریافت تاریخچه داده‌های یک سنسور
- **پاسخ**: داده‌های تاریخی از پایگاه داده

## 🔧 **تغییرات اعمال شده**

### **1. CORS Configuration**
```python
from flask_cors import CORS
CORS(app, origins=['*'], methods=['GET', 'POST', 'OPTIONS'], allow_headers=['Content-Type'])
```

### **2. Dependencies**
```
Flask-CORS==4.0.0
```

### **3. فرمت داده‌های سازگار**
=======
# DigitalTwin SensorPlus - Frontend Integration Guide

## Overview
This guide provides comprehensive information about the DigitalTwin SensorPlus backend API endpoints for frontend integration.

## Base URL
- **Production**: `https://digitaltwin-sensorplus-1.onrender.com`
- **Local Development**: `http://localhost:5000`

## API Endpoints

### 1. Real-time Data
#### GET `/api/data`
Get current sensor data for all devices.

**Response:**
>>>>>>> Stashed changes
```json
{
  "success": true,
  "devices": {
    "temp-1": {
      "device_id": "temp-1",
      "kind": "temperature",
<<<<<<< Updated upstream
      "value": 22.3,
      "unit": "°C",
      "room_id": "room1",
      "timestamp": "2024-01-15T10:30:00"
    }
  },
  "total_devices": 21,
  "timestamp": "2024-01-15T10:30:00",
=======
      "room_id": "room1",
      "temperature_c": 22.5,
      "timestamp": "2025-01-09T12:00:00"
    }
  },
  "timestamp": "2025-01-09T12:00:00",
  "uptime": 3600,
  "simulator_running": true
}
```

#### GET `/api/proxy/data`
Enhanced endpoint for frontend with additional metadata.

**Response:**
```json
{
  "success": true,
  "devices": { /* same as /api/data */ },
  "total_devices": 21,
  "timestamp": "2025-01-09T12:00:00",
>>>>>>> Stashed changes
  "uptime": 3600,
  "simulator_running": true,
  "db_saves": 150,
  "db_fails": 0
}
```

<<<<<<< Updated upstream
## 🚀 **نحوه استفاده در فرانت‌اند**

### **1. اتصال به API**
```javascript
// استفاده از proxy endpoint
const response = await fetch('https://digitaltwin-sensorplus-1.onrender.com/api/proxy/data');
const data = await response.json();

if (data.success) {
  console.log(`Received data for ${data.total_devices} devices`);
  // پردازش داده‌ها
}
```

### **2. دریافت تاریخچه**
```javascript
// دریافت تاریخچه 24 ساعته
const historyResponse = await fetch('https://digitaltwin-sensorplus-1.onrender.com/api/history/temperature/temp-1?hours=24');
const historyData = await historyResponse.json();

if (historyData.success) {
  console.log(`Retrieved ${historyData.count} historical records`);
  // نمایش نمودار یا تحلیل داده‌ها
}
```

### **3. بررسی وضعیت سیستم**
```javascript
// بررسی وضعیت سیستم
const healthResponse = await fetch('https://digitaltwin-sensorplus-1.onrender.com/api/health');
const healthData = await healthResponse.json();

console.log(`System status: ${healthData.status}`);
console.log(`Database: ${healthData.database}`);
console.log(`Total devices: ${healthData.total_devices}`);
```

## 📊 **نقشه دستگاه‌ها**

### **دستگاه‌های موجود:**
- **temp-1 تا temp-5**: سنسورهای دما (5 دستگاه)
- **hum-1 تا hum-5**: سنسورهای رطوبت (5 دستگاه)
- **co2-1 تا co2-5**: سنسورهای CO2 (5 دستگاه)
- **light-1 تا light-5**: سنسورهای نور (5 دستگاه)
- **solar-plant**: پنل خورشیدی (1 دستگاه)

**مجموع: 21 دستگاه**

### **اتاق‌ها:**
- **room1 تا room5**: هر اتاق دارای 4 سنسور
- **solar-farm**: مزرعه خورشیدی

## 🔄 **جریان داده**

```
شبیه‌ساز → latest_data → API Endpoints → فرانت‌اند
    ↓
پایگاه داده (هر 5 دقیقه)
```

## 🛠️ **تست و عیب‌یابی**

### **1. تست اتصال**
```bash
curl https://digitaltwin-sensorplus-1.onrender.com/api/health
```

### **2. تست داده‌ها**
```bash
curl https://digitaltwin-sensorplus-1.onrender.com/api/proxy/data
```

### **3. تست تاریخچه**
```bash
curl https://digitaltwin-sensorplus-1.onrender.com/api/history/temperature/temp-1?hours=24
```

## 📈 **بهینه‌سازی‌ها**

### **1. Caching**
- داده‌ها هر 5 ثانیه به‌روزرسانی می‌شوند
- پایگاه داده هر 5 دقیقه ذخیره می‌شود

### **2. Error Handling**
- مدیریت خطاهای پایگاه داده
- Fallback به حالت شبیه‌سازی
- پیام‌های خطای واضح

### **3. Performance**
- پاسخ سریع API (کمتر از 200ms)
- بهینه‌سازی کوئری‌های پایگاه داده
- مدیریت حافظه

## 🔒 **امنیت**

### **1. CORS**
- پیکربندی CORS برای تمام origins
- پشتیبانی از methods مورد نیاز

### **2. Validation**
- اعتبارسنجی ورودی‌ها
- محدودیت تعداد نتایج

### **3. Error Messages**
- پیام‌های خطای امن
- عدم افشای اطلاعات حساس

## 📝 **نکات مهم**

1. **فرانت‌اند** می‌تواند مستقیماً از `https://digitaltwin-sensorplus-1.onrender.com/api/proxy/data` استفاده کند
2. **تاریخچه داده‌ها** از پایگاه داده MySQL دریافت می‌شود
3. **CORS** برای تمام origins فعال است
4. **21 دستگاه** به طور مداوم داده تولید می‌کنند
5. **پایگاه داده** هر 5 دقیقه به‌روزرسانی می‌شود

## 🚀 **Deployment**

### **فایل‌های به‌روزرسانی شده:**
- `render_dashboard_no_socketio.py` - سرور اصلی
- `render_requirements_ultra_simple.txt` - وابستگی‌ها
- `Dockerfile.no_socketio` - Docker configuration

### **متغیرهای محیطی:**
```bash
PORT=10000
SECRET_KEY=your-secret-key
DB_HOST=kbz.rew.mybluehost.me
DB_NAME=kbzrewmy_sensor
DB_USER=kbzrewmy_mo_kerma
DB_PASSWORD=Mehrafarid.5435
DB_PORT=3306
```

---

**آخرین به‌روزرسانی**: ژانویه 2025  
**نسخه**: 1.0 - یکپارچگی کامل فرانت‌اند و بک‌اند  
**وضعیت**: ✅ آماده برای استفاده
=======
### 2. Health & Status
#### GET `/api/health`
Health check endpoint for frontend monitoring.

**Response:**
```json
{
  "status": "ok",
  "database": "connected",
  "timestamp": "2025-01-09T12:00:00",
  "uptime": 3600,
  "simulator_running": true,
  "total_devices": 21
}
```

#### GET `/health`
Basic health check endpoint.

#### GET `/api/database-status`
Get detailed database status and statistics.

**Response:**
```json
{
  "success": true,
  "database_available": true,
  "db_manager": "Available",
  "scheduler_running": true,
  "total_saves": 150,
  "total_errors": 0,
  "table_statistics": {
    "temperature_data": {"count": 50},
    "humidity_data": {"count": 50}
  }
}
```

### 3. Device Management
#### GET `/api/devices`
Get list of all available devices.

**Response:**
```json
{
  "success": true,
  "devices": [
    {
      "device_id": "temp-1",
      "kind": "temperature",
      "room_id": "room1",
      "last_seen": "2025-01-09T12:00:00"
    }
  ],
  "total_count": 21,
  "timestamp": "2025-01-09T12:00:00"
}
```

#### GET `/api/devices/<device_id>`
Get detailed information for a specific device.

**Example:** `/api/devices/temp-1`

**Response:**
```json
{
  "success": true,
  "device": {
    "device_id": "temp-1",
    "kind": "temperature",
    "room_id": "room1",
    "temperature_c": 22.5,
    "timestamp": "2025-01-09T12:00:00"
  },
  "timestamp": "2025-01-09T12:00:00"
}
```

### 4. Historical Data
#### GET `/api/history/<sensor_type>/<device_id>`
Get historical data for a specific sensor.

**Parameters:**
- `sensor_type`: temperature, humidity, co2, light, solar
- `device_id`: temp-1, hum-1, co2-1, light-1, solar-plant
- `hours` (query param): Number of hours to retrieve (default: 24)

**Example:** `/api/history/temperature/temp-1?hours=48`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2025-01-09T11:00:00",
      "value": 22.3,
      "device_id": "temp-1",
      "room_id": "room1"
    }
  ],
  "count": 100,
  "sensor_type": "temperature",
  "device_id": "temp-1",
  "hours": 48
}
```

### 5. Control Endpoints
#### POST `/api/toggle-simulator`
Toggle simulator on/off.

**Response:**
```json
{
  "success": true,
  "running": true
}
```

#### GET `/api/debug-database`
Get detailed database debug information.

## Device Types & IDs

### Temperature Sensors
- `temp-1` to `temp-5` (rooms 1-5)

### Humidity Sensors  
- `hum-1` to `hum-5` (rooms 1-5)

### CO2 Sensors
- `co2-1` to `co2-5` (rooms 1-5)

### Light Sensors
- `light-1` to `light-5` (rooms 1-5)

### Solar Farm
- `solar-plant` (solar farm)

## CORS Configuration
The backend is configured with CORS to allow requests from any origin:
- **Origins**: `*` (all origins)
- **Methods**: `GET`, `POST`, `OPTIONS`
- **Headers**: `Content-Type`

## Error Handling
All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error description"
}
```

Common HTTP status codes:
- `200`: Success
- `404`: Device not found
- `503`: Database not available
- `500`: Internal server error

## Usage Examples

### Frontend Integration
```javascript
// Fetch real-time data
const response = await fetch('https://digitaltwin-sensorplus-1.onrender.com/api/proxy/data');
const data = await response.json();

// Get device list
const devices = await fetch('https://digitaltwin-sensorplus-1.onrender.com/api/devices');

// Get historical data
const history = await fetch('https://digitaltwin-sensorplus-1.onrender.com/api/history/temperature/temp-1?hours=24');
```

### Health Monitoring
```javascript
// Check system health
const health = await fetch('https://digitaltwin-sensorplus-1.onrender.com/api/health');
const status = await health.json();
console.log('Database:', status.database);
console.log('Devices:', status.total_devices);
```

## Notes
- All timestamps are in ISO 8601 format
- Data is updated every 5 seconds
- Database saves occur every 5 minutes
- The system supports both real-time and historical data access
- All endpoints are CORS-enabled for frontend integration
>>>>>>> Stashed changes
