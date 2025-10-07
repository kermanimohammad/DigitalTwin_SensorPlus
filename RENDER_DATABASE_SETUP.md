# Render.com Database Setup Guide

## 🔧 Environment Variables Configuration

برای اتصال نسخه آنلاین به database، باید environment variables زیر را در Render.com تنظیم کنید:

### 📋 **مراحل تنظیم:**

1. **وارد Render Dashboard شوید:**
   - به https://dashboard.render.com بروید
   - پروژه `digitaltwin-sensorplus-1` را انتخاب کنید

2. **Environment Variables را اضافه کنید:**
   - روی **"Environment"** کلیک کنید
   - **"Add Environment Variable"** را کلیک کنید
   - متغیرهای زیر را یکی یکی اضافه کنید:

### 🗄️ **Database Configuration:**

```bash
DB_HOST=kbz.rew.mybluehost.me
DB_NAME=kbzrewmy_sensor
DB_USER=kbzrewmy_mo_kerma
DB_PASSWORD=Mehrafarid.5435
DB_PORT=3306
DB_CHARSET=utf8mb4
```

### ⚙️ **Application Configuration:**

```bash
PORT=10000
PYTHONUNBUFFERED=1
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=digitaltwin-sensor-api-secret-key-2024
```

### 🔄 **Simulator Configuration:**

```bash
SIMULATOR_INTERVAL=5
SIMULATOR_DEVICES=21
DASHBOARD_TITLE=DigitalTwin Sensor Dashboard
LOG_LEVEL=INFO
```

## 🚀 **Deploy Steps:**

1. **Environment Variables را اضافه کنید** (همه متغیرهای بالا)
2. **"Save Changes"** کلیک کنید
3. **"Manual Deploy"** کلیک کنید
4. **"Deploy latest commit"** انتخاب کنید

## ✅ **Verification:**

پس از deploy، dashboard باید نشان دهد:
- **Database: Connected** (سبز)
- **DB Saves: > 0** (شمارنده افزایش می‌یابد)
- **DB Errors: 0**

## 🔍 **Troubleshooting:**

### اگر Database هنوز "Not Available" است:

1. **Environment Variables را بررسی کنید:**
   - همه متغیرهای بالا اضافه شده‌اند؟
   - مقادیر درست هستند؟

2. **Logs را بررسی کنید:**
   - Render Dashboard > Logs
   - خطاهای database connection را جستجو کنید

3. **Database Connection را تست کنید:**
   - دکمه "Test Database" را کلیک کنید
   - پیام خطا را بررسی کنید

## 📊 **Expected Behavior:**

پس از تنظیم صحیح:
- ✅ Database scheduler هر 1 دقیقه اجرا می‌شود
- ✅ تمام 21 دستگاه در جداول مخصوص ذخیره می‌شوند
- ✅ Dashboard وضعیت "Database: Connected" نشان می‌دهد
- ✅ شمارنده "DB Saves" هر دقیقه افزایش می‌یابد

## 🆘 **Support:**

اگر مشکل ادامه داشت:
1. Logs را در Render Dashboard بررسی کنید
2. Environment variables را دوباره بررسی کنید
3. Manual deploy انجام دهید
