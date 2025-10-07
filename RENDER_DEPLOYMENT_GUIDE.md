# Render.com Deployment Guide

## 🚀 Quick Deploy to Render.com

### Method 1: Using Render Dashboard (Recommended)

1. **Go to [Render.com](https://render.com)**
2. **Sign up/Login** with GitHub
3. **Click "New +"** → **"Web Service"**
4. **Connect your GitHub repository**
5. **Configure the service:**
   - **Name**: `digitaltwin-sensor-dashboard`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r render_requirements.txt`
   - **Start Command**: `python render_dashboard.py`
   - **Plan**: `Free`

6. **Click "Create Web Service"**

### Method 2: Using render.yaml (Blue-Green Deploy)

1. **Push the code to GitHub** (already done)
2. **Go to Render Dashboard**
3. **Click "New +"** → **"Blueprint"**
4. **Select your repository**
5. **Render will automatically detect `render.yaml`**
6. **Click "Apply"**

## 📁 Required Files for Render.com

### Core Files:
- `render_dashboard.py` - Main application
- `render_requirements.txt` - Python dependencies
- `render.yaml` - Render configuration
- `Procfile` - Process definition

### Features:
- ✅ **Built-in MQTT Simulator** (no external broker needed)
- ✅ **Real-time Dashboard** with WebSocket
- ✅ **21 Virtual Devices** (5 rooms × 4 sensors + 1 solar)
- ✅ **Auto-scaling** on Render.com
- ✅ **HTTPS** automatically enabled
- ✅ **Custom Domain** support

## 🔧 Configuration

### Environment Variables:
```bash
SECRET_KEY=your_secret_key_here
PORT=10000
```

### Dependencies:
```
Flask==2.3.3
Flask-SocketIO==5.3.6
python-socketio==5.9.0
eventlet==0.33.3
python-engineio==4.7.1
```

## 📊 Dashboard Features

### Real-time Sensors:
- **Temperature** (5 devices) - 18-28°C
- **Humidity** (5 devices) - 30-70%
- **CO2** (5 devices) - 350-600 ppm
- **Light** (5 devices) - 200-1200 lux
- **Solar Panel** (1 device) - 80-150W

### Dashboard Controls:
- **Refresh Data** - Reload dashboard
- **Clear Display** - Clear all data
- **Toggle Simulator** - Start/Stop data generation

### Status Bar:
- **Connection Status** - WebSocket connection
- **Device Count** - Number of active devices
- **Message Count** - Total messages received
- **Uptime** - Service uptime

## 🌐 Access Your Dashboard

After deployment, your dashboard will be available at:
```
https://your-app-name.onrender.com
```

## 🔍 Testing

### Local Testing:
```bash
python render_dashboard.py
```
Then visit: `http://localhost:5000`

### API Endpoints:
- `GET /` - Dashboard
- `GET /api/data` - JSON data
- `POST /api/toggle-simulator` - Control simulator

## 🚨 Troubleshooting

### Common Issues:

1. **Build Fails**:
   - Check `render_requirements.txt` syntax
   - Ensure all dependencies are listed

2. **App Crashes**:
   - Check logs in Render dashboard
   - Verify `render_dashboard.py` runs locally

3. **No Data Display**:
   - Simulator starts automatically
   - Check WebSocket connection in browser console

4. **Port Issues**:
   - Render sets `PORT` environment variable
   - App uses `os.getenv('PORT', 5000)`

### Logs:
```bash
# View logs in Render dashboard
# Or check local logs:
python render_dashboard.py
```

## 📈 Scaling

### Free Plan:
- 750 hours/month
- Sleeps after 15 minutes of inactivity
- Cold start ~30 seconds

### Paid Plans:
- Always-on
- Custom domains
- More resources

## 🔄 Updates

To update your deployment:
1. **Push changes to GitHub**
2. **Render auto-deploys** (if enabled)
3. **Or manually redeploy** from dashboard

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Flask-SocketIO**: https://flask-socketio.readthedocs.io/
- **Project Issues**: GitHub Issues

---

**🎉 Your DigitalTwin Sensor Dashboard is now live on Render.com!**
