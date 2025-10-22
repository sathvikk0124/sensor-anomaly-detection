# Sensor Anomaly Detection System

🔍 **Statistical anomaly detection system** for sensor data using the **3-sigma rule** with both Python/MongoDB backend and interactive web interface.

## 🌟 Features

### Web Dashboard (GitHub Pages)
- ✅ Interactive, responsive web interface
- 📊 Real-time data visualization with Chart.js
- 🎛️ Configurable sigma threshold and time range
- 📈 Statistical analysis per sensor
- 🚨 Detailed anomaly detection and reporting
- 📱 Mobile-friendly design
- 💾 Sample data generator & JSON file upload

### Python Backend (MongoDB)
- ✅ MongoDB aggregation pipeline implementation
- 📊 Statistical analysis (mean, standard deviation)
- 🔍 3-sigma anomaly detection
- 🗄️ Sample data generation with realistic sensor profiles
- ⚙️ Environment-based configuration

## 🚀 Live Demo

**Web Dashboard:** `https://sathvikk0124.github.io/sensor-anomaly-detection/`

## 📁 Project Structure

```
sensor-anomaly-detection/
├── index.html              # Web dashboard UI
├── styles.css              # Modern responsive styling
├── script.js               # Client-side anomaly detection
├── anomaly_detection.py    # Python MongoDB implementation
├── sample_data.py          # Test data generator
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🌐 Web Interface Usage

### Quick Start
1. Visit: `https://sathvikk0124.github.io/sensor-anomaly-detection/`
2. Click **"Load Sample Data"** to generate test data
3. Adjust **Sigma Threshold** (default: 3σ) and **Days Back** (default: 7)
4. Click **"🚀 Detect Anomalies"**
5. View results:
   - 📊 Sensor statistics cards
   - 📈 Interactive charts
   - 📋 Detailed anomaly table

### Upload Your Own Data
```json
[
  {
    "sensor_id": "sensor_001",
    "value": 25.7,
    "timestamp": "2025-10-21T09:30:00Z"
  }
]
```

## 🐍 Python Backend Setup

### Prerequisites
- Python 3.8+
- MongoDB 4.0+

### Installation

```bash
# Clone repository
git clone https://github.com/sathvikk0124/sensor-anomaly-detection.git
cd sensor-anomaly-detection

# Install dependencies
pip install -r requirements.txt

# Configure MongoDB
cp .env.example .env
# Edit .env with your MongoDB connection string
```

## 📊 Data Structure

### Input Format

```json
{
  "sensor_id": "sensor_001",
  "value": 25.7,
  "timestamp": "2025-10-21T09:30:00Z"
}
```

## 🧮 The 3-Sigma Rule

**Mathematical Background:**

An anomaly is detected when:
```
value > mean + (3 × standard_deviation)
```

**Why 3-sigma?**
- In a normal distribution, 99.7% of data falls within 3σ
- Values beyond 3σ have only a 0.3% probability
- Effectively identifies outliers while minimizing false positives


## 👤 Author

**sathvikk0124**
- GitHub: [@sathvikk0124](https://github.com/sathvikk0124)

---

⭐ **Star this repo if you find it helpful!** ⭐