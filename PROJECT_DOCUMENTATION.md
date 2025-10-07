# DigitalTwin SensorPlus - Project Documentation

## 📋 Project Overview

**DigitalTwin SensorPlus** is a comprehensive IoT sensor monitoring system that combines real-time data visualization with database persistence. The system receives sensor data via MQTT protocol, stores it in a MySQL database, and provides real-time dashboards and REST APIs for data access.

**هیچ گزینه و اطلاعاتی در صفحات برنامه به فارسی نباشد و همه چیز به انگلیسی باشد

## 🏗️ System Architecture

### Core Components

1. **MQTT Subscriber** - Receives sensor data from MQTT broker
2. **Database Manager** - Handles data persistence to MySQL/SQLite
3. **Web Dashboard** - Real-time visualization interface
4. **REST API** - Data access endpoints
5. **WebSocket Server** - Real-time data streaming

### Data Flow

```
Sensors → MQTT Broker → MQTT Subscriber → Database 
                                    ↓
                            WebSocket → Dashboard + Real-time Display
                                    ↓
                            REST API → External Apps
```

## 📁 File Structure

### Core System Files

- `database.py` - Database connection and operations
- `mqtt_subscriber.py` - Main MQTT subscriber (legacy)
- `sensor_api.py` - REST API endpoints
- `web_dashboard.py` - Web dashboard interface

### Live System Files

- `realtime_dashboard.py` - Real-time dashboard with WebSocket
- `live_sensor_api.py` - Live data API endpoints
- `mqtt_subscriber_hybrid.py` - Hybrid MQTT subscriber (DB + real-time)

### Testing & Development Files

- `simple_dashboard.py` - Simple dashboard for testing
- `final_working_dashboard.py` - Production-ready dashboard
- `test_*.py` - Various test scripts
- `simple_mqtt_*.py` - Simple MQTT components for testing

### Configuration Files

- `requirements.txt` - Python dependencies
- `requirements_live.txt` - Live system dependencies
- `docker-compose*.yml` - Docker configurations
- `env.example` - Environment variables template

## 🔧 Technical Specifications

### Database Schema

### MySQL

#### Separate Tables (Alternative Schema)
- `temperature_data` - Temperature sensor data
- `humidity_data` - Humidity sensor data
- `co2_data` - CO2 sensor data
- `light_data` - Light sensor data
- `solar_data` - Solar panel data

### MQTT Protocol

#### Topic Structure
```
building/demo/{sensor_type}/{device_id}
```

#### Message Format
```json
{
    "deviceId": "temp-1",
    "kind": "temperature",
    "value": 25.5,
    "unit": "°C",
    "roomId": "room1",
    "ts": 1640995200000,
    "powerW": 12.5,      // Optional for solar sensors
    "voltage": 24.0,     // Optional for solar sensors
    "current": 0.52,     // Optional for solar sensors
    "on": true           // Optional for switch sensors
}
```

### API Endpoints

#### Main API (`sensor_api.py`)
- `GET /api/sensors` - Get recent sensor data
- `GET /api/stats` - Get sensor statistics

#### Live API (`live_sensor_api.py`)
- `GET /api/live/stats` - Live sensor statistics
- `GET /api/live/devices` - Connected devices
- `GET /api/live/device/<id>` - Specific device data

#### Dashboard API (`web_dashboard.py`)
- `GET /api/data` - Dashboard data
- `GET /` - Dashboard interface

#### Working Dashboard API (`final_working_dashboard.py`)
- `GET /api/data` - Current sensor data with DB status
- `GET /api/test-db` - Database connection test
- `GET /` - Dashboard interface

## 🚀 Deployment Configurations

### Local Development

#### Prerequisites
```bash
pip install flask flask-socketio paho-mqtt flask-cors sqlalchemy mysql-connector-python
```

#### Running the System
```bash
# Option 1: Simple dashboard (memory only)
python simple_dashboard.py

# Option 2: Working dashboard (with database)
python final_working_dashboard.py

# Option 3: Full system
python mqtt_subscriber_hybrid.py  # Terminal 1
python hybrid_dashboard.py        # Terminal 2
```

### Docker Deployment

#### Docker Compose Services
- `broker` - Mosquitto MQTT broker
- `mqtt-sim` - MQTT data simulator
- `mqtt-subscriber-hybrid` - Hybrid MQTT subscriber
- `hybrid-dashboard` - Dashboard service
- `hybrid-sensor-api` - API service

#### Commands
```bash
# Start full system
docker-compose -f docker-compose-hybrid.yml up

# Start live system
docker-compose -f docker-compose-live.yml up
```

### Production Deployment (Render)

- **URL**: https://digitaltwin-sensorplus.onrender.com
- **Environment**: Production
- **Database**: MySQL (kbz.rew.mybluehost.me)
- **MQTT**: External broker

## 🔄 System Modes

### 1. Legacy Mode
- **Files**: `mqtt_subscriber.py`, `sensor_api.py`, `web_dashboard.py`
- **Features**: Database storage only, basic dashboard
- **Use Case**: Historical data analysis

### 2. Live Mode
- **Files**: `realtime_dashboard.py`, `live_sensor_api.py`
- **Features**: Real-time display, in-memory storage
- **Use Case**: Live monitoring, no persistence

### 3. Hybrid Mode
- **Files**: `mqtt_subscriber_hybrid.py`, `hybrid_dashboard.py`, `hybrid_sensor_api.py`
- **Features**: Both real-time display and database storage
- **Use Case**: Production systems

### 4. Simple Mode
- **Files**: `simple_dashboard.py`, `final_working_dashboard.py`
- **Features**: Testing and development
- **Use Case**: Local testing, debugging

## 📊 Data Processing Rules

### MQTT Message Processing

1. **Connection**: Connect to MQTT broker (test.mosquitto.org or local)
2. **Subscription**: Subscribe to `building/demo/#` topic
3. **Message Parsing**: Parse JSON payload
4. **Validation**: Validate required fields (deviceId, kind, value, unit, ts)
5. **Storage**: Save to database using `db_manager.save_sensor_data()`
6. **Real-time**: Emit to WebSocket clients
7. **Logging**: Log all operations with timestamps

### Database Operations

#### Save Operation
```python
def save_sensor_data(self, data_dict):
    # Parse timestamp from milliseconds
    timestamp = datetime.fromtimestamp(data_dict.get('ts', 0) / 1000)
    
    # Create sensor data record
    sensor_data = SensorData(
        device_id=data_dict.get('deviceId', ''),
        kind=data_dict.get('kind', ''),
        room_id=data_dict.get('roomId'),
        value=data_dict.get('value'),
        unit=data_dict.get('unit'),
        power_w=data_dict.get('powerW'),
        voltage=data_dict.get('voltage'),
        current=data_dict.get('current'),
        on_status=data_dict.get('on'),
        timestamp=timestamp,
        raw_data=json.dumps(data_dict)
    )
    
    # Save to database
    session.add(sensor_data)
    session.commit()
```

#### Retrieval Operations
- `get_recent_data(limit=100)` - Get recent records
- `get_data_by_room(room_id)` - Get data by room
- `get_data_by_device(device_id)` - Get data by device
- `get_data_by_kind(kind)` - Get data by sensor type

### WebSocket Events

#### Client → Server
- `connect` - Client connection
- `disconnect` - Client disconnection

#### Server → Client
- `sensor_data` - New sensor data
```json
{
    "device_id": "temp-1",
    "kind": "temperature",
    "value": 25.5,
    "unit": "°C",
    "timestamp": "2024-01-15T10:30:00",
    "db_saved": true
}
```

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
DB_HOST=kbz.rew.mybluehost.me
DB_NAME=kbzrewmy_sensor
DB_USER=kbzrewmy_mo_kerma
DB_PASSWORD=Mehrafarid.5435
DB_PORT=3306

# MQTT Configuration
MQTT_BROKER=test.mosquitto.org
MQTT_PORT=1883
MQTT_TOPIC=building/demo/#

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key

### Database Configuration

#### MySQL (Production)
```python
DB_CONFIG = {
    'host': 'kbz.rew.mybluehost.me',
    'database': 'kbzrewmy_sensor',
    'user': 'kbzrewmy_mo_kerma',
    'password': 'Mehrafarid.5435',
    'port': 3306,
    'charset': 'utf8mb4',
    'autocommit': True
}
```


## 🧪 Testing

### Test Files

1. **`test_database.py`** - Database connection and operations
2. **`test_simple_mqtt.py`** - MQTT connectivity
3. **`test_complete_system.py`** - End-to-end system test
4. **`test_working_system.py`** - Working dashboard test
5. **`test_hybrid_system.py`** - Hybrid system test

### Test Commands

```bash
# Test database
python test_database.py

# Test MQTT
python test_simple_mqtt.py

# Test complete system
python test_complete_system.py

# Test working dashboard
python test_working_system.py
```

### Test Data

#### Sample MQTT Messages
```json
// Temperature sensor
{
    "deviceId": "temp-1",
    "kind": "temperature",
    "value": 25.5,
    "unit": "°C",
    "roomId": "room1",
    "ts": 1640995200000
}

// Humidity sensor
{
    "deviceId": "hum-1",
    "kind": "humidity",
    "value": 60.0,
    "unit": "%",
    "roomId": "room1",
    "ts": 1640995200000
}

// Solar panel
{
    "deviceId": "solar-1",
    "kind": "solar",
    "powerW": 150.0,
    "voltage": 24.0,
    "current": 6.25,
    "roomId": "roof",
    "ts": 1640995200000
}
```

## 🚨 Error Handling

### MQTT Errors
- Connection failures → Retry with exponential backoff
- Message parsing errors → Log and skip message
- Broker disconnection → Auto-reconnect

### Database Errors
- Connection failures → Fallback to SQLite
- Insert errors → Rollback transaction
- Query errors → Return empty results

### WebSocket Errors
- Client disconnection → Clean up resources
- Message errors → Log and continue
- Connection errors → Retry connection

## 📈 Performance Considerations

### Database Optimization
- Indexes on frequently queried columns
- Connection pooling
- Batch inserts for high-volume data
- Regular cleanup of old data

### MQTT Optimization
- QoS levels for message reliability
- Connection pooling
- Message buffering for offline periods
- Topic filtering

### WebSocket Optimization
- Connection limits
- Message rate limiting
- Client-side buffering
- Compression for large payloads

## 🔒 Security Considerations

### MQTT Security
- Use TLS for MQTT connections in production
- Implement authentication and authorization
- Validate all incoming messages
- Rate limiting for message frequency

### Database Security
- Use parameterized queries
- Encrypt sensitive data
- Regular security updates
- Access control and permissions

### Web Security
- HTTPS in production
- CORS configuration
- Input validation
- Rate limiting for APIs

## 📝 Development Guidelines

### Code Structure
- Separate concerns (MQTT, Database, Web)
- Use dependency injection
- Implement proper error handling
- Add comprehensive logging

### Testing
- Unit tests for all components
- Integration tests for data flow
- End-to-end tests for user scenarios
- Performance tests for scalability

### Documentation
- API documentation
- Database schema documentation
- Deployment guides
- Troubleshooting guides

## 🚀 Deployment Checklist

### Pre-deployment
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database schema updated
- [ ] Dependencies installed
- [ ] Security review completed

### Deployment
- [ ] Database connection tested
- [ ] MQTT broker accessible
- [ ] Web services responding
- [ ] WebSocket connections working
- [ ] API endpoints functional

### Post-deployment
- [ ] Monitor system performance
- [ ] Check error logs
- [ ] Verify data flow
- [ ] Test user interfaces
- [ ] Backup procedures in place

## 🔄 Maintenance

### Regular Tasks
- Database cleanup (remove old data)
- Log rotation
- Performance monitoring
- Security updates
- Backup verification

### Monitoring
- System health checks
- Database performance
- MQTT connection status
- Web service availability
- Error rate monitoring

## 📞 Support Information

### Logs Location
- Application logs: Console output
- Database logs: MySQL error log
- MQTT logs: Broker logs
- Web server logs: Flask debug output

### Common Issues
1. **Database connection failed** → Check credentials and network
2. **MQTT connection failed** → Check broker availability
3. **WebSocket not working** → Check CORS and firewall settings
4. **Data not saving** → Check database permissions
5. **Dashboard not updating** → Check WebSocket connection

### Debug Commands
```bash
# Check database connection
python -c "from database import db_manager; print(db_manager.get_recent_data(1))"

# Test MQTT connection
python test_simple_mqtt.py

# Check API endpoints
curl http://localhost:5000/api/data

# Monitor system logs
tail -f application.log
```

---

**Last Updated**: October 2024  
**Version**: 2.0  
**Maintainer**: Development Team
