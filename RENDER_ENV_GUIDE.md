# Render.com Environment Variables Guide

## 🔧 Environment Variables for Render.com

### 📋 **Required Variables (Must be set)**

```bash
# Server Configuration
PORT=10000
PYTHONUNBUFFERED=1
FLASK_ENV=production
FLASK_DEBUG=False

# Security
SECRET_KEY=digitaltwin-sensor-render-secret-key-2024
```

### ⚙️ **Optional Variables (Can be customized)**

```bash
# Simulator Configuration
SIMULATOR_INTERVAL=5
SIMULATOR_ENABLED=true
SIMULATOR_DEVICES=21

# Dashboard Configuration
DASHBOARD_TITLE=DigitalTwin Sensor Dashboard
DASHBOARD_REFRESH_INTERVAL=10000
DASHBOARD_AUTO_REFRESH=true

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Performance Configuration
SOCKETIO_ASYNC_MODE=eventlet
SOCKETIO_CORS_ALLOWED_ORIGINS=*
```

## 🚀 **How to Set Environment Variables in Render.com**

### Method 1: Render Dashboard
1. **Go to your service** in Render dashboard
2. **Click "Environment"** tab
3. **Add each variable** with key-value pairs
4. **Click "Save Changes"**
5. **Redeploy** your service

### Method 2: render.yaml (Blueprint)
```yaml
services:
  - type: web
    name: digitaltwin-sensor-dashboard
    env: python
    plan: free
    buildCommand: pip install -r render_requirements.txt
    startCommand: python render_dashboard_env.py
    envVars:
      - key: PORT
        value: 10000
      - key: SECRET_KEY
        generateValue: true
      - key: SIMULATOR_INTERVAL
        value: 5
      - key: SIMULATOR_DEVICES
        value: 21
      - key: DASHBOARD_TITLE
        value: "DigitalTwin Sensor Dashboard"
      - key: DASHBOARD_AUTO_REFRESH
        value: true
      - key: FLASK_ENV
        value: production
      - key: FLASK_DEBUG
        value: false
```

## 📊 **Variable Descriptions**

### **Server Configuration**
| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `5000` | Port number for the web service |
| `PYTHONUNBUFFERED` | `1` | Python output buffering |
| `FLASK_ENV` | `production` | Flask environment mode |
| `FLASK_DEBUG` | `False` | Flask debug mode |

### **Simulator Configuration**
| Variable | Default | Description |
|----------|---------|-------------|
| `SIMULATOR_INTERVAL` | `5` | Seconds between data updates |
| `SIMULATOR_ENABLED` | `true` | Enable/disable simulator |
| `SIMULATOR_DEVICES` | `21` | Number of virtual devices |

### **Dashboard Configuration**
| Variable | Default | Description |
|----------|---------|-------------|
| `DASHBOARD_TITLE` | `DigitalTwin Sensor Dashboard` | Dashboard title |
| `DASHBOARD_REFRESH_INTERVAL` | `10000` | Auto-refresh interval (ms) |
| `DASHBOARD_AUTO_REFRESH` | `true` | Enable auto-refresh |

### **Logging Configuration**
| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FORMAT` | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` | Log format |

### **Performance Configuration**
| Variable | Default | Description |
|----------|---------|-------------|
| `SOCKETIO_ASYNC_MODE` | `eventlet` | SocketIO async mode |
| `SOCKETIO_CORS_ALLOWED_ORIGINS` | `*` | CORS allowed origins |

## 🎯 **Recommended Configurations**

### **For Development/Testing**
```bash
FLASK_ENV=development
FLASK_DEBUG=true
LOG_LEVEL=DEBUG
SIMULATOR_INTERVAL=2
SIMULATOR_DEVICES=10
DASHBOARD_AUTO_REFRESH=true
```

### **For Production**
```bash
FLASK_ENV=production
FLASK_DEBUG=false
LOG_LEVEL=INFO
SIMULATOR_INTERVAL=5
SIMULATOR_DEVICES=21
DASHBOARD_AUTO_REFRESH=true
```

### **For High Performance**
```bash
FLASK_ENV=production
FLASK_DEBUG=false
LOG_LEVEL=WARNING
SIMULATOR_INTERVAL=10
SIMULATOR_DEVICES=50
DASHBOARD_AUTO_REFRESH=false
SOCKETIO_ASYNC_MODE=threading
```

## 🔍 **Testing Environment Variables**

### **Local Testing**
```bash
# Set environment variables
export PORT=5000
export SIMULATOR_INTERVAL=3
export SIMULATOR_DEVICES=15
export DASHBOARD_TITLE="My Custom Dashboard"

# Run the application
python render_dashboard_env.py
```

### **Check Configuration via API**
```bash
# Get current configuration
curl http://localhost:5000/api/config

# Response example:
{
  "success": true,
  "config": {
    "PORT": 5000,
    "SIMULATOR_INTERVAL": 3,
    "SIMULATOR_DEVICES": 15,
    "DASHBOARD_TITLE": "My Custom Dashboard",
    ...
  }
}
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Simulator not starting**
   - Check `SIMULATOR_ENABLED=true`
   - Verify `SIMULATOR_INTERVAL` is a positive number

2. **Dashboard not updating**
   - Check `DASHBOARD_AUTO_REFRESH=true`
   - Verify `DASHBOARD_REFRESH_INTERVAL` is reasonable

3. **Performance issues**
   - Reduce `SIMULATOR_DEVICES`
   - Increase `SIMULATOR_INTERVAL`
   - Set `LOG_LEVEL=WARNING`

4. **WebSocket connection issues**
   - Check `SOCKETIO_CORS_ALLOWED_ORIGINS`
   - Verify `SOCKETIO_ASYNC_MODE=eventlet`

### **Debug Mode**
```bash
# Enable debug mode
FLASK_DEBUG=true
LOG_LEVEL=DEBUG

# Check logs in Render dashboard
# Or run locally with debug output
```

## 📈 **Performance Tuning**

### **Memory Usage**
- Reduce `SIMULATOR_DEVICES` for lower memory usage
- Increase `SIMULATOR_INTERVAL` for less frequent updates

### **CPU Usage**
- Use `SOCKETIO_ASYNC_MODE=threading` for better CPU utilization
- Set `LOG_LEVEL=WARNING` to reduce logging overhead

### **Network Usage**
- Increase `SIMULATOR_INTERVAL` to reduce network traffic
- Set `DASHBOARD_AUTO_REFRESH=false` to reduce client requests

## 🔐 **Security Considerations**

### **Production Settings**
```bash
# Always use in production
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-strong-secret-key-here

# Restrict CORS if needed
SOCKETIO_CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### **Secret Key Generation**
```bash
# Generate a strong secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

## 📝 **Environment Files**

### **render_env_vars.txt**
Contains all environment variables with descriptions and examples.

### **render_dashboard_env.py**
Enhanced dashboard with environment variable support.

### **render.yaml**
Blueprint configuration with environment variables.

---

**🎉 Your Render.com deployment is now fully configurable via environment variables!**
