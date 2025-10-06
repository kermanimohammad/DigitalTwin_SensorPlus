# Enhanced Lighting Scenarios for Digital Twin Sensor Plus

## Overview

This enhanced lighting system provides realistic sensor data simulation with intelligent lighting patterns that consider:

1. **Seasonal Variations**: Different sunrise/sunset times throughout the year
2. **Holiday and Weekend Patterns**: Modified behavior for holidays and weekends
3. **Random Occupancy Variations**: Realistic random usage patterns
4. **Room-Specific Patterns**: Different lighting behaviors for different room types

## Features

### 🌍 Seasonal Adjustments
- **Spring**: Normal sunrise/sunset times
- **Summer**: Early sunrise (-1.5h), late sunset (+2h) - longer days
- **Autumn**: Later sunrise (+1h), earlier sunset (-1h)
- **Winter**: Late sunrise (+2h), early sunset (-2.5h) - shorter days

### 🏠 Room Types and Patterns

#### Bedroom
- **Morning**: 6:30-8:00 AM
- **Evening**: 7:00-11:00 PM
- **Weekend Delay**: 1 hour later
- **Usage**: Sleep and relaxation periods

#### Living Room
- **Morning**: 6:00-9:00 AM
- **Evening**: 5:00 PM-12:00 AM
- **Weekend Delay**: 30 minutes later
- **Usage**: Most active room, family time

#### Kitchen
- **Morning**: 5:30-8:30 AM
- **Evening**: 6:00-9:00 PM
- **Weekend Delay**: 1.5 hours later
- **Usage**: Cooking and dining activities

#### Office
- **Morning**: 7:00 AM-6:00 PM
- **Evening**: 7:00-10:00 PM
- **Weekend Delay**: 2 hours later
- **Usage**: Work hours, reduced weekend activity

#### Bathroom
- **Morning**: 6:00-8:00 AM
- **Evening**: 7:00-11:00 PM
- **Weekend Delay**: 1 hour later
- **Usage**: Short usage periods throughout the day

### 🎲 Random Factors
- **Timing Variation**: ±30-60 minutes random variation
- **Unexpected Usage**: 10-30% chance of random usage
- **Occupancy Levels**: Realistic 0.0-1.0 occupancy ratios
- **Room-Specific Randomness**: Different variation levels per room type

### 🎉 Holiday and Weekend Behavior
- **Fixed Holidays**: New Year (Jan 1), Christmas (Dec 25-26)
- **Weekends**: Saturday and Sunday
- **Behavior Changes**: Delayed start times, different occupancy probabilities

## Files

### Core Files
- `mqtt_simulator_enhanced.py` - Enhanced MQTT simulator with intelligent lighting
- `test_lighting_simple.py` - Simple test script for lighting scenarios
- `demo_enhanced_lighting.py` - Demonstration script with patterns overview

### Original Files (for comparison)
- `mqtt_simulator.py` - Original simple simulator
- `test_lighting_scenarios.py` - Comprehensive test suite (with Persian text)

## Usage

### Basic Usage
```bash
# Run the enhanced simulator
python mqtt_simulator_enhanced.py

# Test lighting scenarios
python test_lighting_simple.py

# View patterns and run demo
python demo_enhanced_lighting.py
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

The enhanced simulator publishes to the following topics:

### Room Data
- `{prefix}/{room_id}/temperature` - Temperature sensor data
- `{prefix}/{room_id}/humidity` - Humidity sensor data
- `{prefix}/{room_id}/co2` - CO2 sensor data
- `{prefix}/{room_id}/light` - Lighting status and power consumption
- `{prefix}/{room_id}/occupancy` - Occupancy level (0.0-1.0)

### Solar Data
- `{prefix}/solar` - Solar panel data with seasonal information

### Enhanced Data Format
```json
{
  "deviceId": "light-1",
  "kind": "light",
  "roomId": "room1",
  "roomType": "bedroom",
  "ts": 1696608000000,
  "on": true,
  "powerW": 18.5
}
```

## Key Improvements

### 1. Realistic Timing
- Seasonal sunrise/sunset adjustments
- Room-specific usage patterns
- Holiday and weekend variations

### 2. Intelligent Occupancy
- Probability-based occupancy simulation
- Room-specific occupancy patterns
- Random variation for realism

### 3. Enhanced Data
- Room type information in all messages
- Occupancy level data
- Seasonal information in solar data

### 4. Configurable Behavior
- Easy to modify room patterns
- Adjustable random variations
- Customizable holiday schedules

## Testing

The system includes comprehensive testing:

```bash
# Run basic tests
python test_lighting_simple.py

# View detailed patterns
python demo_enhanced_lighting.py patterns
```

### Test Coverage
- ✅ Basic lighting scenarios at different times
- ✅ Seasonal variations
- ✅ Holiday and weekend patterns
- ✅ Room-specific behavior
- ✅ Random variation testing

## Customization

### Adding New Room Types
1. Add new room type to `RoomType` class
2. Define pattern in `room_patterns` dictionary
3. Update room configuration in `MQTTSimEnhanced.__init__`

### Modifying Seasonal Behavior
1. Adjust `seasonal_adjustments` dictionary
2. Modify sunrise/sunset offset values
3. Update seasonal multipliers in solar simulation

### Adding Holidays
1. Add dates to `holidays` list in `LightingController`
2. Implement custom holiday behavior if needed

## Performance

- **Memory Usage**: Minimal overhead compared to original simulator
- **CPU Usage**: Slightly higher due to intelligent calculations
- **Network**: Same MQTT message frequency and size
- **Scalability**: Supports any number of rooms with different types

## Future Enhancements

Potential improvements for future versions:

1. **Weather Integration**: Adjust lighting based on weather conditions
2. **User Preferences**: Personalized lighting schedules
3. **Energy Optimization**: Smart energy-saving patterns
4. **Machine Learning**: Learn from usage patterns
5. **Multi-Building Support**: Different buildings with different patterns

## Troubleshooting

### Common Issues

1. **Unicode Errors**: Use `test_lighting_simple.py` instead of `test_lighting_scenarios.py`
2. **MQTT Connection**: Check broker settings and network connectivity
3. **Import Errors**: Ensure all files are in the same directory

### Debug Mode
Set environment variable for detailed logging:
```bash
export DEBUG="1"
```

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is part of the Digital Twin Sensor Plus system.
