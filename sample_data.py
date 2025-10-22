#!/usr/bin/env python3
"""
Generate sample sensor data for testing anomaly detection
"""

import os
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'sensor_db')
MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION', 'sensor_readings')

def generate_sample_data(num_readings=500, anomaly_rate=0.05):
    """
    Generate sample sensor data with intentional anomalies
    
    Args:
        num_readings (int): Number of readings to generate
        anomaly_rate (float): Percentage of readings that should be anomalies (0.0 to 1.0)
    """
    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DATABASE]
    collection = db[MONGODB_COLLECTION]
    
    # Clear existing data
    collection.delete_many({})
    print(f"🗑️  Cleared existing data from {MONGODB_COLLECTION}")
    
    # Sensor definitions (realistic sensor types)
    sensors = [
        {'id': 'sensor_001', 'type': 'temperature', 'base': 22, 'unit': 'celsius', 'location': 'Room A'},
        {'id': 'sensor_002', 'type': 'humidity', 'base': 65, 'unit': 'percentage', 'location': 'Room A'},
        {'id': 'sensor_003', 'type': 'pressure', 'base': 1013, 'unit': 'hPa', 'location': 'Room B'},
        {'id': 'sensor_004', 'type': 'co2', 'base': 450, 'unit': 'ppm', 'location': 'Room B'},
        {'id': 'sensor_005', 'type': 'light', 'base': 350, 'unit': 'lux', 'location': 'Room C'}
    ]
    
    readings = []
    now = datetime.utcnow()
    
    print(f"\n📊 Generating {num_readings} sensor readings...")
    print(f"🎯 Target anomaly rate: {anomaly_rate * 100:.1f}%\n")
    
    for i in range(num_readings):
        # Random sensor
        sensor = random.choice(sensors)
        
        # Random timestamp within last 10 days
        days_ago = random.uniform(0, 10)
        timestamp = now - timedelta(days=days_ago)
        
        # Generate value (normal with some variation)
        base_value = sensor['base']
        variation = base_value * 0.1  # 10% variation
        value = base_value + random.uniform(-variation, variation)
        
        # Introduce anomalies
        if random.random() < anomaly_rate:
            # Make it 50-100% higher than base (guaranteed anomaly)
            value = base_value + (base_value * random.uniform(0.5, 1.0))
        
        reading = {
            'sensor_id': sensor['id'],
            'sensor_type': sensor['type'],
            'value': round(value, 2),
            'unit': sensor['unit'],
            'location': sensor['location'],
            'timestamp': timestamp
        }
        
        readings.append(reading)
    
    # Insert into MongoDB
    result = collection.insert_many(readings)
    
    # Print summary
    print(f"✅ Successfully inserted {len(result.inserted_ids)} readings\n")
    
    # Show sensor summary
    print("📈 Sensor Summary:")
    print(f"{'='*60}")
    for sensor in sensors:
        sensor_readings = [r for r in readings if r['sensor_id'] == sensor['id']]
        values = [r['value'] for r in sensor_readings]
        
        if values:
            mean = sum(values) / len(values)
            min_val = min(values)
            max_val = max(values)
            
            print(f"{sensor['id']} ({sensor['type']})")
            print(f"  Location: {sensor['location']}")
            print(f"  Readings: {len(sensor_readings)}")
            print(f"  Range: {min_val:.2f} - {max_val:.2f} {sensor['unit']}")
            print(f"  Mean: {mean:.2f} {sensor['unit']}\n")
    
    print(f"{'='*60}")
    print(f"\n✨ Sample data generation complete!")
    print(f"\n💡 Next step: Run 'python anomaly_detection.py' to detect anomalies\n")
    
    # Close connection
    client.close()

if __name__ == '__main__':
    try:
        generate_sample_data(num_readings=500, anomaly_rate=0.05)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("1. MongoDB is running")
        print("2. .env file is configured correctly")
        print("3. pymongo is installed: pip install pymongo python-dotenv")