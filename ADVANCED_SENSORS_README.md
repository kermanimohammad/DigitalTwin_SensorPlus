# Advanced Sensor Simulation for Digital Twin Sensor Plus

## Overview

This advanced sensor simulation system provides highly realistic sensor data with intelligent patterns that consider multiple environmental and behavioral factors:

1. **Dynamic Weather Conditions**: Real-time weather changes affecting all sensors
2. **Seasonal Variations**: Different patterns for each season
3. **Room-Specific Behaviors**: Unique sensor patterns for different room types
4. **Occupancy Effects**: Realistic impact of human presence
5. **Time-Based Patterns**: Natural daily and seasonal cycles

## Key Features

### 🌞 Solar Panel Simulation
- **Realistic Day/Night Cycle**: 0W at night, gradual increase from sunrise
- **Peak Production**: Maximum at noon (12:00) with 10% boost
- **Seasonal Efficiency**:
  - Spring: 80% efficiency
  - Summer: 120% efficiency (longer days)
  - Autumn: 70% efficiency
  - Winter: 50% efficiency (shorter days)
- **Weather Impact**:
  - Sunny: 100% production
  - Cloudy: 30% production
  - Rainy: 10% production
  - Stormy: 5% production

### 🌡️ Temperature Simulation
- **Room-Specific Base Temperatures**:
  - Bedroom: 20°C (cooler for sleep)
  - Living Room: 22°C (comfortable)
  - Kitchen: 24°C (warmer due to cooking)
  - Office: 21°C (optimal for work)
  - Bathroom: 23°C (warm for comfort)
- **Seasonal Adjustments**:
  - Spring: +0°C
  - Summer: +8°C
  - Autumn: -2°C
  - Winter: -8°C
- **Occupancy Effects**: +0.5-2.0°C per person
- **Weather Effects**: ±2°C based on conditions
- **Time Effects**: Natural daily temperature variations

### 💧 Humidity Simulation
- **Room-Specific Base Humidity**:
  - Bedroom: 45% (comfortable for sleep)
  - Living Room: 50% (balanced)
  - Kitchen: 60% (higher due to cooking)
  - Office: 40% (optimal for work)
  - Bathroom: 70% (highest due to showers)
- **Seasonal Adjustments**:
  - Spring: +0%
  - Summer: +15%
  - Autumn: +10%
  - Winter: -10%
- **Weather Effects**:
  - Sunny: -5% humidity
  - Rainy: +15% humidity
  - Stormy: +20% humidity
- **Occupancy Effects**: +5% per person (breathing, perspiration)

### 🌬️ CO2 Simulation
- **Base CO2 Levels**:
  - Bedroom: 400 ppm
  - Living Room: 450 ppm
  - Kitchen: 500 ppm
  - Office: 420 ppm
  - Bathroom: 480 ppm
- **Occupancy Effects**: +200 ppm per person
- **Ventilation Rates**:
  - Bedroom: 30% (low)
  - Living Room: 50% (medium)
  - Kitchen: 80% (high)
  - Office: 70% (good)
  - Bathroom: 90% (highest)
- **Time-Based Ventilation**:
  - Work Hours (8-18): +30% ventilation
  - Night (22-6): -20% ventilation

### 🌤️ Weather Simulation
- **Dynamic Weather Changes**: Every 30-120 minutes
- **Weather Conditions**:
  - Sunny: Clear skies, maximum solar
  - Cloudy: Reduced solar, stable conditions
  - Rainy: Low solar, increased humidity
  - Stormy: Minimal solar, high humidity
- **Seasonal Weather Patterns**:
  - Spring: 30% rain, 40% clouds
  - Summer: 20% rain, 30% clouds
  - Autumn: 40% rain, 50% clouds
  - Winter: 30% rain, 60% clouds

## Files

### Core Files
- `mqtt_simulator_advanced.py` - Advanced MQTT simulator with realistic sensor patterns
- `test_advanced_sensors.py` - Comprehensive test suite for all sensor types
- `demo_advanced_sensors.py` - Demonstration script with detailed patterns

### Comparison Files
- `mqtt_simulator_enhanced.py` - Enhanced lighting-focused simulator
- `mqtt_simulator.py` - Original simple simulator

## Usage

### Basic Usage
```bash
# Run the advanced simulator
python mqtt_simulator_advanced.py

# Test all sensor patterns
python test_advanced_sensors.py

# View patterns and run demo
python demo_advanced_sensors.py
```

### Environment Variables
```bash
# MQTT Configuration
export BROKER="test.mosquitto.org"
export PORT="1883"
export PREFIX="building/demo"
export QOS="0"
export INTERVAL="10"
export DURATION="300"  # 5 minutes

# Authentication (optional)
export MQTT_USER="username"
export MQTT_PASS="password"
```

### Docker Usage
```bash
# Build and run with Docker Compose
docker compose up --build -d

# View logs
docker compose logs -f mqtt-sim
```

## MQTT Topics

### Room Sensor Topics
- `{prefix}/{room_id}/temperature` - Temperature with occupancy data
- `{prefix}/{room_id}/humidity` - Humidity with occupancy data
- `{prefix}/{room_id}/co2` - CO2 with occupancy data
- `{prefix}/{room_id}/light` - Lighting status and power
- `{prefix}/{room_id}/occupancy` - Occupancy level (0.0-1.0)

### System Topics
- `{prefix}/solar` - Solar panel data with weather and seasonal info
- `{prefix}/weather` - Weather conditions and seasonal data

### Enhanced Data Format
```json
{
  "deviceId": "temp-1",
  "kind": "temperature",
  "roomId": "room1",
  "roomType": "bedroom",
  "ts": 1696608000000,
  "value": 22.4,
  "unit": "C",
  "occupancy": 0.75
}
```

```json
{
  "deviceId": "solar-plant",
  "kind": "solar",
  "ts": 1696608000000,
  "powerW": 755.6,
  "voltage": 48.2,
  "current": 15.7,
  "efficiency": 0.756,
  "season": "autumn",
  "weather": "cloudy"
}
```

## Advanced Features

### 1. Realistic Solar Patterns
- **Sinusoidal Day Curve**: Natural sunrise to sunset pattern
- **Noon Peak**: 10% boost during peak hours (11-13)
- **Weather Integration**: Real-time weather impact
- **Seasonal Adjustments**: Day length variations

### 2. Intelligent Temperature Control
- **Multi-Factor Calculation**: Season + Weather + Occupancy + Time
- **Room-Specific Profiles**: Different base temperatures per room type
- **Gradual Changes**: Realistic temperature transitions
- **Occupancy Heat**: Human body heat simulation

### 3. Dynamic Humidity Management
- **Weather-Driven**: Rain and storm effects
- **Occupancy Impact**: Breathing and perspiration
- **Room Characteristics**: Different humidity profiles
- **Seasonal Patterns**: Natural humidity variations

### 4. Smart CO2 Monitoring
- **Ventilation Simulation**: Room-specific ventilation rates
- **Time-Based Ventilation**: Natural air circulation patterns
- **Occupancy Tracking**: Human respiration effects
- **Environmental Factors**: Outdoor air quality simulation

### 5. Dynamic Weather System
- **Probabilistic Changes**: Realistic weather transitions
- **Seasonal Probabilities**: Weather patterns by season
- **Cross-Sensor Effects**: Weather impact on all sensors
- **Real-Time Updates**: Continuous weather monitoring

## Testing

### Comprehensive Test Suite
```bash
# Run all tests
python test_advanced_sensors.py
```

### Test Coverage
- ✅ Solar panel simulation (day/night, seasonal, weather)
- ✅ Temperature patterns (room-specific, seasonal, occupancy)
- ✅ Humidity simulation (weather effects, seasonal)
- ✅ CO2 monitoring (ventilation, occupancy, time-based)
- ✅ Weather changes (dynamic transitions)
- ✅ Seasonal variations (all sensors)

### Demo Features
```bash
# View sensor patterns
python demo_advanced_sensors.py patterns

# View MQTT topics
python demo_advanced_sensors.py topics

# View usage examples
python demo_advanced_sensors.py usage
```

## Customization

### Adding New Room Types
1. Add new room type to `RoomType` enum
2. Define sensor patterns in `room_sensor_patterns`
3. Update room configuration in `MQTTSimAdvanced.__init__`

### Modifying Weather Patterns
1. Adjust `weather_effects` dictionary
2. Modify seasonal weather probabilities
3. Update weather change intervals

### Customizing Sensor Behaviors
1. Modify calculation functions in `AdvancedSensorController`
2. Adjust seasonal adjustments
3. Update room-specific patterns

## Performance

- **Memory Usage**: Optimized for continuous operation
- **CPU Usage**: Efficient calculations with minimal overhead
- **Network**: Same MQTT message frequency as original
- **Scalability**: Supports unlimited rooms and sensor types

## Real-World Accuracy

### Solar Panel Simulation
- Based on real solar panel efficiency curves
- Accounts for weather conditions and seasonal variations
- Includes realistic day/night transitions

### Temperature Simulation
- Room-specific thermal characteristics
- Human body heat contribution
- Weather and seasonal effects
- Natural daily temperature cycles

### Humidity Simulation
- Weather-driven humidity changes
- Human activity effects
- Room-specific moisture characteristics
- Seasonal humidity patterns

### CO2 Simulation
- Realistic human respiration rates
- Ventilation system simulation
- Time-based air circulation
- Environmental air quality factors

## Future Enhancements

### Planned Features
1. **Machine Learning Integration**: Learn from usage patterns
2. **Energy Optimization**: Smart energy-saving algorithms
3. **Predictive Analytics**: Forecast sensor values
4. **Multi-Building Support**: Different building types
5. **IoT Integration**: Real sensor data integration

### Advanced Weather
1. **Weather API Integration**: Real weather data
2. **Microclimate Simulation**: Building-specific weather
3. **Storm Simulation**: Advanced weather events
4. **Climate Change Modeling**: Long-term climate effects

## Troubleshooting

### Common Issues
1. **High CPU Usage**: Reduce update interval
2. **Memory Issues**: Limit number of rooms
3. **MQTT Connection**: Check broker settings
4. **Import Errors**: Ensure all files are present

### Debug Mode
```bash
export DEBUG="1"
python mqtt_simulator_advanced.py
```

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Ensure all tests pass
5. Submit a pull request

## License

This project is part of the Digital Twin Sensor Plus system.

## Comparison with Previous Versions

### vs. Enhanced Simulator
- **More Sensors**: All sensor types with realistic patterns
- **Weather Integration**: Dynamic weather affecting all sensors
- **Better Accuracy**: More realistic sensor behaviors
- **Comprehensive Testing**: Full test coverage

### vs. Original Simulator
- **Realistic Patterns**: Natural sensor behaviors
- **Environmental Factors**: Weather and seasonal effects
- **Room Intelligence**: Room-specific sensor patterns
- **Advanced Features**: Occupancy, ventilation, and more

This advanced simulator provides the most realistic sensor data simulation available, making it perfect for testing and development of IoT applications, building management systems, and digital twin implementations.
