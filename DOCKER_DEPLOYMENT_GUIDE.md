# Docker Deployment Guide for Render.com

## 🐳 Docker Files Overview

### **Available Dockerfiles:**

1. **`Dockerfile.render`** - Optimized for Render.com (Recommended)
2. **`Dockerfile.simple`** - Minimal configuration
3. **`Dockerfile.production`** - Multi-stage production build
4. **`docker-compose.render.yml`** - Local testing with Docker Compose

## 🚀 **Quick Start with Docker**

### **Method 1: Using Dockerfile.render (Recommended)**

```bash
# Build the image
docker build -f Dockerfile.render -t digitaltwin-dashboard .

# Run the container
docker run -p 10000:10000 \
  -e SIMULATOR_DEVICES=21 \
  -e SIMULATOR_INTERVAL=5 \
  -e DASHBOARD_TITLE="My Dashboard" \
  digitaltwin-dashboard
```

### **Method 2: Using Docker Compose**

```bash
# Start the service
docker-compose -f docker-compose.render.yml up -d

# View logs
docker-compose -f docker-compose.render.yml logs -f

# Stop the service
docker-compose -f docker-compose.render.yml down
```

## 📋 **Dockerfile.render Features**

### **Optimizations:**
- ✅ **Python 3.11-slim** base image
- ✅ **Non-root user** for security
- ✅ **Health check** endpoint
- ✅ **Environment variables** support
- ✅ **Optimized caching** layers
- ✅ **Security hardening**

### **Environment Variables:**
```dockerfile
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=10000
```

## 🔧 **Environment Variables in Docker**

### **Required Variables:**
```bash
PORT=10000
SECRET_KEY=your-secret-key
FLASK_ENV=production
FLASK_DEBUG=false
```

### **Optional Variables:**
```bash
SIMULATOR_INTERVAL=5
SIMULATOR_DEVICES=21
SIMULATOR_ENABLED=true
DASHBOARD_TITLE=DigitalTwin Sensor Dashboard
DASHBOARD_AUTO_REFRESH=true
LOG_LEVEL=INFO
```

## 🏗️ **Build Commands**

### **Build Dockerfile.render:**
```bash
docker build -f Dockerfile.render -t digitaltwin-dashboard:latest .
```

### **Build Dockerfile.simple:**
```bash
docker build -f Dockerfile.simple -t digitaltwin-dashboard:simple .
```

### **Build Dockerfile.production:**
```bash
docker build -f Dockerfile.production -t digitaltwin-dashboard:production .
```

## 🚀 **Run Commands**

### **Basic Run:**
```bash
docker run -p 10000:10000 digitaltwin-dashboard:latest
```

### **With Environment Variables:**
```bash
docker run -p 10000:10000 \
  -e SIMULATOR_DEVICES=15 \
  -e SIMULATOR_INTERVAL=3 \
  -e DASHBOARD_TITLE="Custom Dashboard" \
  -e LOG_LEVEL=DEBUG \
  digitaltwin-dashboard:latest
```

### **With Volume Mounting:**
```bash
docker run -p 10000:10000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config:/app/config \
  digitaltwin-dashboard:latest
```

## 🔍 **Health Check**

### **Built-in Health Check:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/api/data || exit 1
```

### **Manual Health Check:**
```bash
# Check container health
docker ps

# Check health status
docker inspect --format='{{.State.Health.Status}}' <container_id>

# View health logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' <container_id>
```

## 📊 **Docker Compose Configuration**

### **Basic Service:**
```yaml
services:
  digitaltwin-dashboard:
    build:
      context: .
      dockerfile: Dockerfile.render
    ports:
      - "10000:10000"
    environment:
      - PORT=10000
      - SIMULATOR_DEVICES=21
      - SIMULATOR_INTERVAL=5
    restart: unless-stopped
```

### **With Nginx (Production):**
```yaml
services:
  digitaltwin-dashboard:
    build:
      context: .
      dockerfile: Dockerfile.render
    environment:
      - PORT=10000
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - digitaltwin-dashboard
    profiles:
      - production
```

## 🔐 **Security Considerations**

### **Non-root User:**
```dockerfile
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app
```

### **Minimal Base Image:**
```dockerfile
FROM python:3.11-slim
```

### **No Cache in Production:**
```dockerfile
RUN pip install --no-cache-dir -r render_requirements.txt
```

## 📈 **Performance Optimization**

### **Multi-stage Build (Dockerfile.production):**
```dockerfile
# Build stage
FROM python:3.11-slim as builder
# ... build dependencies

# Production stage
FROM python:3.11-slim
# ... copy from builder
```

### **Layer Caching:**
```dockerfile
# Copy requirements first for better caching
COPY render_requirements.txt ./
RUN pip install -r render_requirements.txt

# Copy application files last
COPY render_dashboard_env.py ./
```

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **Port Already in Use:**
   ```bash
   # Check what's using the port
   netstat -tulpn | grep :10000
   
   # Use different port
   docker run -p 8080:10000 digitaltwin-dashboard:latest
   ```

2. **Permission Denied:**
   ```bash
   # Check file permissions
   ls -la render_dashboard_env.py
   
   # Fix permissions
   chmod +x render_dashboard_env.py
   ```

3. **Health Check Failing:**
   ```bash
   # Check if app is running
   docker exec -it <container_id> curl http://localhost:10000/api/data
   
   # Check logs
   docker logs <container_id>
   ```

4. **Environment Variables Not Working:**
   ```bash
   # Check environment variables
   docker exec -it <container_id> env | grep SIMULATOR
   
   # Verify in app
   curl http://localhost:10000/api/config
   ```

### **Debug Mode:**
```bash
# Run with debug environment
docker run -p 10000:10000 \
  -e FLASK_DEBUG=true \
  -e LOG_LEVEL=DEBUG \
  digitaltwin-dashboard:latest
```

## 📝 **Docker Commands Reference**

### **Build Commands:**
```bash
# Build with specific tag
docker build -t digitaltwin-dashboard:v1.0 .

# Build with no cache
docker build --no-cache -t digitaltwin-dashboard:latest .

# Build with build args
docker build --build-arg PYTHON_VERSION=3.11 -t digitaltwin-dashboard:latest .
```

### **Run Commands:**
```bash
# Run in background
docker run -d -p 10000:10000 digitaltwin-dashboard:latest

# Run with name
docker run --name my-dashboard -p 10000:10000 digitaltwin-dashboard:latest

# Run with restart policy
docker run --restart unless-stopped -p 10000:10000 digitaltwin-dashboard:latest
```

### **Management Commands:**
```bash
# List containers
docker ps -a

# View logs
docker logs <container_id>

# Execute commands
docker exec -it <container_id> /bin/bash

# Stop container
docker stop <container_id>

# Remove container
docker rm <container_id>

# Remove image
docker rmi digitaltwin-dashboard:latest
```

## 🌐 **Deployment to Render.com**

### **Using Dockerfile.render:**
1. **Push to GitHub** (already done)
2. **Go to Render.com**
3. **Create Web Service**
4. **Select "Docker" as Environment**
5. **Set Dockerfile Path:** `Dockerfile.render`
6. **Deploy**

### **Environment Variables in Render:**
```bash
PORT=10000
SECRET_KEY=your-secret-key
SIMULATOR_DEVICES=21
SIMULATOR_INTERVAL=5
DASHBOARD_TITLE=DigitalTwin Sensor Dashboard
```

---

**🎉 Your Docker deployment is ready for Render.com!**
