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
```json
{
  "success": true,
  "devices": {
    "temp-1": {
      "device_id": "temp-1",
      "kind": "temperature",
      "value": 22.3,
      "unit": "°C",
      "room_id": "room1",
      "timestamp": "2024-01-15T10:30:00"
    }
  },
  "total_devices": 21,
  "timestamp": "2024-01-15T10:30:00",
  "uptime": 3600,
  "simulator_running": true,
  "db_saves": 150,
  "db_fails": 0
}
```

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
