# راهنمای استقرار روی Render.com

## 📋 مراحل استقرار

### 1. آماده‌سازی Repository
```bash
# اطمینان از وجود فایل‌های زیر:
- render.yaml
- Dockerfile.render
- mqtt_simulator.py (به‌روزرسانی شده)
- mqtt-test.html (به‌روزرسانی شده)
- requirements.txt
```

### 2. ایجاد حساب Render.com
1. به [render.com](https://render.com) بروید
2. حساب کاربری ایجاد کنید
3. اتصال GitHub repository

### 3. استقرار سرویس
1. در داشبورد Render، "New +" کلیک کنید
2. "Web Service" انتخاب کنید
3. Repository خود را انتخاب کنید
4. تنظیمات:
   - **Name**: mqtt-simulator
   - **Environment**: Docker
   - **Dockerfile Path**: `./Dockerfile.render`
   - **Plan**: Free

### 4. متغیرهای محیطی (اختیاری)
در صورت نیاز به تغییر تنظیمات:
- `BROKER`: آدرس MQTT broker
- `PORT`: پورت MQTT (8883 برای SSL)
- `PREFIX`: پیشوند topic ها
- `INTERVAL`: فاصله ارسال داده (ثانیه)

## 🔧 تنظیمات پیشنهادی

### MQTT Broker های رایگان:
1. **HiveMQ** (پیشنهادی):
   - Host: `broker.hivemq.com`
   - Port: `8883` (SSL) یا `1883` (غیر SSL)
   - WebSocket: `wss://broker.hivemq.com:8884`

2. **Eclipse Mosquitto**:
   - Host: `test.mosquitto.org`
   - Port: `8883` (SSL)

3. **MQTT.fx**:
   - Host: `broker.mqtt-dashboard.com`
   - Port: `1883`

## 🌐 دسترسی به سرویس

پس از استقرار موفق:
- **URL اصلی**: `https://your-app-name.onrender.com`
- **صفحه تست MQTT**: `https://your-app-name.onrender.com/`
- **Health Check**: `https://your-app-name.onrender.com/health`

## 📊 مانیتورینگ

### لاگ‌ها:
```bash
# در داشبورد Render
Logs > View Logs
```

### تست اتصال:
1. صفحه وب را باز کنید
2. تنظیمات MQTT broker را وارد کنید
3. "Connection" کلیک کنید
4. پیام‌های دریافتی را مشاهده کنید

## ⚠️ محدودیت‌های Render Free Plan

- **Sleep Mode**: سرویس بعد از 15 دقیقه عدم استفاده خواب می‌رود
- **Bandwidth**: محدودیت ترافیک ماهانه
- **Build Time**: محدودیت زمان ساخت
- **Memory**: محدودیت حافظه

## 🔄 به‌روزرسانی

برای به‌روزرسانی:
1. تغییرات را در GitHub push کنید
2. Render به‌طور خودکار rebuild می‌کند
3. یا در داشبورد "Manual Deploy" کلیک کنید

## 🆘 عیب‌یابی

### مشکلات رایج:
1. **Build Failed**: بررسی Dockerfile.render
2. **Connection Failed**: بررسی تنظیمات MQTT broker
3. **Sleep Mode**: سرویس را wake up کنید
4. **Memory Limit**: به پلن پولی ارتقا دهید

### لاگ‌های مفید:
```bash
# بررسی اتصال MQTT
docker compose logs -f mqtt-sim

# تست محلی
python mqtt_simulator.py --broker broker.hivemq.com --port 8883
```
