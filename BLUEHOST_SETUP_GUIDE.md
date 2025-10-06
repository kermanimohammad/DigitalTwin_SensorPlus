# راهنمای تنظیم دیتابیس Bluehost

## مشکل فعلی
خطای `Access denied for user 'mo_kerma'@'your-ip'` نشان می‌دهد که IP شما در Bluehost مجاز نیست.

## راه‌حل‌های ممکن:

### 1. اضافه کردن IP به Remote MySQL (توصیه شده)

1. وارد cPanel Bluehost شوید
2. بخش "Remote MySQL" را پیدا کنید
3. IP فعلی خود را اضافه کنید:
   - IP فعلی شما: `bras-base-mtrlpq4718w-grc-16-142-115-175-25.dsl.bell.ca`
   - یا از `%` استفاده کنید (برای همه IP ها - کمتر امن)

### 2. استفاده از Localhost (اگر روی همان سرور اجرا می‌کنید)

اگر کد شما روی همان سرور Bluehost اجرا می‌شود:
```python
config = {
    'host': 'localhost',  # به جای kbz.rew.mybluehost.me
    'database': 'kbzrewmy_sensor',
    'user': 'mo_kerma',
    'password': 'Mehrafarid.5435',
    'port': 3306
}
```

### 3. استفاده از SSH Tunnel

اگر SSH دسترسی دارید:
```bash
ssh -L 3306:localhost:3306 username@kbz.rew.mybluehost.me
```

### 4. تنظیمات امنیتی Bluehost

در cPanel:
- Database Users → mo_kerma → Manage → Remote Access
- IP Address: `%` (برای همه) یا IP خاص شما

## تست اتصال

پس از تنظیمات، این کد را اجرا کنید:
```bash
python test_bluehost_connection.py
```

## استفاده از متغیرهای محیطی

برای امنیت بیشتر، اطلاعات دیتابیس را در متغیرهای محیطی قرار دهید:

```bash
export DB_HOST=kbz.rew.mybluehost.me
export DB_NAME=kbzrewmy_sensor
export DB_USER=mo_kerma
export DB_PASSWORD=Mehrafarid.5435
export DB_PORT=3306
```

## نکات مهم:

1. **امنیت**: هرگز رمز عبور را در کد قرار ندهید
2. **IP Whitelist**: فقط IP های مورد نیاز را اضافه کنید
3. **Backup**: قبل از تغییرات، از دیتابیس پشتیبان تهیه کنید
4. **Testing**: همیشه ابتدا اتصال را تست کنید

## اگر مشکل ادامه داشت:

1. با پشتیبانی Bluehost تماس بگیرید
2. از phpMyAdmin در cPanel استفاده کنید
3. از MySQL Workbench برای تست اتصال استفاده کنید
