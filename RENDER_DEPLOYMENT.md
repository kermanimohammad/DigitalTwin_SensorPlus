# 🚀 Render.com Deployment Guide

## فایل‌های مورد نیاز برای Deploy

### 1. فایل‌های اصلی:
- `render_api.py` - API اصلی Flask
- `render_requirements.txt` - وابستگی‌های Python
- `Procfile` - دستور اجرای سرور

### 2. تنظیمات Render.com:

#### Build Command:
```bash
pip install -r render_requirements.txt
```

#### Start Command:
```bash
gunicorn render_api:app
```

#### Environment Variables:
```
PORT=10000
```

## 📊 API Endpoints

### صفحه اصلی:
```
https://digitaltwin-sensorplus.onrender.com/
```

### API Endpoints:
```
GET /api/stats          - آمار کلی سنسورها
GET /api/temperature    - داده‌های دما
GET /api/humidity       - داده‌های رطوبت
GET /api/co2           - داده‌های CO2
GET /api/light         - داده‌های نور
GET /api/solar         - داده‌های خورشیدی
GET /api/room/room1    - داده‌های اتاق
GET /api/health        - وضعیت سیستم
```

### مثال استفاده:
```
https://digitaltwin-sensorplus.onrender.com/api/stats
https://digitaltwin-sensorplus.onrender.com/api/temperature?limit=5
```

## 🔧 مراحل Deploy:

1. **آپلود فایل‌ها** به Render.com
2. **تنظیم Build Command**: `pip install -r render_requirements.txt`
3. **تنظیم Start Command**: `gunicorn render_api:app`
4. **Deploy** کردن پروژه

## ✅ تست محلی:

```bash
python render_api.py
```

سپس به آدرس `http://localhost:5000` بروید.

## 📱 ویژگی‌ها:

- ✅ صفحه اصلی زیبا با لینک‌های مستقیم
- ✅ API endpoints برای تمام سنسورها
- ✅ اتصال به دیتابیس Bluehost
- ✅ نمایش آمار کلی
- ✅ فیلتر بر اساس تعداد رکوردها
- ✅ وضعیت سلامت سیستم
- ✅ JSON response برای تمام endpoints

## 🎯 نتیجه:

پس از deploy، می‌توانید از طریق مرورگر به آدرس‌های زیر دسترسی پیدا کنید:

- **صفحه اصلی**: `https://digitaltwin-sensorplus.onrender.com/`
- **آمار**: `https://digitaltwin-sensorplus.onrender.com/api/stats`
- **دما**: `https://digitaltwin-sensorplus.onrender.com/api/temperature`