#!/usr/bin/env python3
"""
Sensor Anomaly Detection using MongoDB Aggregation Pipeline
Detects sensor readings that are 3 standard deviations above the mean
"""

import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'sensor_db')
MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION', 'sensor_readings')

def detect_anomalies(days_back=7, sigma_threshold=3):
    """
    Detect anomalies in sensor data using 3-sigma rule
    
    Args:
        days_back (int): Number of days to look back
        sigma_threshold (float): Number of standard deviations for threshold
    """
    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DATABASE]
    collection = db[MONGODB_COLLECTION]
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days_back)
    
    print(f"\n🔍 Sensor Anomaly Detection Results")
    print(f"{'='*70}")
    print(f"Time Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Sigma Threshold: {sigma_threshold}σ\n")
    
    # MongoDB Aggregation Pipeline
    pipeline = [
        # Stage 1: Filter by date range
        {
            '$match': {
                'timestamp': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
        },
        
        # Stage 2: Group by sensor_id and calculate statistics
        {
            '$group': {
                '_id': '$sensor_id',
                'readings': {'$push': '$$ROOT'},
                'mean': {'$avg': '$value'},
                'count': {'$sum': 1},
                'values': {'$push': '$value'}
            }
        },
        
        # Stage 3: Calculate variance and standard deviation
        {
            '$addFields': {
                'variance': {
                    '$avg': {
                        '$map': {
                            'input': '$values',
                            'as': 'val',
                            'in': {
                                '$pow': [
                                    {'$subtract': ['$$val', '$mean']},
                                    2
                                ]
                            }
                        }
                    }
                }
            }
        },
        
        # Stage 4: Calculate standard deviation
        {
            '$addFields': {
                'stddev': {'$sqrt': '$variance'}
            }
        },
        
        # Stage 5: Calculate threshold (mean + N * stddev)
        {
            '$addFields': {
                'threshold': {
                    '$add': [
                        '$mean',
                        {'$multiply': [sigma_threshold, '$stddev']}
                    ]
                }
            }
        },
        
        # Stage 6: Filter readings that exceed threshold
        {
            '$addFields': {
                'anomalies': {
                    '$filter': {
                        'input': '$readings',
                        'as': 'reading',
                        'cond': {
                            '$gt': ['$$reading.value', '$threshold']
                        }
                    }
                }
            }
        },
        
        # Stage 7: Sort by sensor_id
        {
            '$sort': {'_id': 1}
        }
    ]
    
    # Execute aggregation
    results = list(collection.aggregate(pipeline))
    
    # Display results
    total_anomalies = 0
    
    for sensor_result in results:
        sensor_id = sensor_result['_id']
        mean = sensor_result['mean']
        stddev = sensor_result['stddev']
        threshold = sensor_result['threshold']
        count = sensor_result['count']
        anomalies = sensor_result['anomalies']
        
        print(f"📊 Sensor: {sensor_id}")
        print(f"   Readings: {count}")
        print(f"   Mean: {mean:.2f} | Std Dev: {stddev:.2f} | Threshold ({sigma_threshold}σ): {threshold:.2f}")
        
        if anomalies:
            print(f"   🚨 Found {len(anomalies)} anomalies:")
            total_anomalies += len(anomalies)
            
            # Sort anomalies by deviation (highest first)
            sorted_anomalies = sorted(
                anomalies,
                key=lambda x: (x['value'] - mean) / stddev if stddev > 0 else 0,
                reverse=True
            )
            
            for anomaly in sorted_anomalies[:5]:  # Show top 5
                value = anomaly['value']
                timestamp = anomaly['timestamp']
                deviation = (value - mean) / stddev if stddev > 0 else 0
                
                print(f"      • {timestamp.strftime('%Y-%m-%d %H:%M:%S')} | "
                      f"Value: {value:.2f} | Deviation: {deviation:.2f}σ")
            
            if len(anomalies) > 5:
                print(f"      ... and {len(anomalies) - 5} more")
        else:
            print(f"   ✅ No anomalies detected")
        
        print()    
    # Summary
    print(f"{'='*70}")
    print(f"📈 Summary: {total_anomalies} total anomalies detected across {len(results)} sensors")
    print(f"{'='*70}\n")
    
    # Close connection
    client.close()
    
    return results

if __name__ == '__main__':
    try:
        detect_anomalies(days_back=7, sigma_threshold=3)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("1. MongoDB is running")
        print("2. .env file is configured correctly")
        print("3. Sample data has been loaded (run sample_data.py)")