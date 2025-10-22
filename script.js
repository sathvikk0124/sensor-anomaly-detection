// Sensor Anomaly Detection - Client-side Implementation

let statsChart = null;
let anomalyChart = null;

// Event Listeners
document.getElementById('loadSample').addEventListener('click', loadSampleData);
document.getElementById('fileInput').addEventListener('change', handleFileUpload);
document.getElementById('processData').addEventListener('click', processData);

// Load Sample Data
function loadSampleData() {
    const sampleData = generateSampleData();
    document.getElementById('dataInput').value = JSON.stringify(sampleData, null, 2);
}

// Generate Sample Sensor Data
function generateSampleData() {
    const sensors = ['sensor_001', 'sensor_002', 'sensor_003', 'sensor_004', 'sensor_005'];
    const data = [];
    const now = new Date();
    
    for (let i = 0; i < 500; i++) {
        const sensorId = sensors[Math.floor(Math.random() * sensors.length)];
        const daysAgo = Math.floor(Math.random() * 10);
        const timestamp = new Date(now - daysAgo * 24 * 60 * 60 * 1000);
        
        // Base values for each sensor
        let baseValue = 20;
        if (sensorId === 'sensor_001') baseValue = 22;
        if (sensorId === 'sensor_002') baseValue = 65;
        if (sensorId === 'sensor_003') baseValue = 1013;
        if (sensorId === 'sensor_004') baseValue = 450;
        if (sensorId === 'sensor_005') baseValue = 350;
        
        // Normal reading with some variation
        let value = baseValue + (Math.random() - 0.5) * (baseValue * 0.1);
        
        // 5% chance of anomaly
        if (Math.random() < 0.05) {
            value = baseValue + (baseValue * (0.5 + Math.random() * 0.5));
        }
        
        data.push({
            sensor_id: sensorId,
            value: parseFloat(value.toFixed(2)),
            timestamp: timestamp.toISOString()
        });
    }
    
    return data;
}

// Handle File Upload
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('dataInput').value = e.target.result;
        };
        reader.readAsText(file);
    }
}

// Process Data and Detect Anomalies
function processData() {
    const dataInput = document.getElementById('dataInput').value;
    const sigmaThreshold = parseFloat(document.getElementById('sigmaThreshold').value);
    const daysBack = parseInt(document.getElementById('daysBack').value);
    
    try {
        const data = JSON.parse(dataInput);
        
        if (!Array.isArray(data)) {
            throw new Error('Data must be an array');
        }
        
        // Filter data by time range
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - daysBack);
        
        const filteredData = data.filter(reading => {
            const readingDate = new Date(reading.timestamp);
            return readingDate >= cutoffDate;
        });
        
        // Calculate statistics per sensor
        const sensorStats = calculateSensorStats(filteredData);
        
        // Detect anomalies
        const anomalies = detectAnomalies(filteredData, sensorStats, sigmaThreshold);
        
        // Display results
        displayResults(sensorStats, anomalies, sigmaThreshold);
        
    } catch (error) {
        alert('Error processing data: ' + error.message);
    }
}

// Calculate Statistics for Each Sensor
function calculateSensorStats(data) {
    const sensorGroups = {};
    
    // Group by sensor_id
    data.forEach(reading => {
        if (!sensorGroups[reading.sensor_id]) {
            sensorGroups[reading.sensor_id] = [];
        }
        sensorGroups[reading.sensor_id].push(reading.value);
    });
    
    // Calculate mean and std dev for each sensor
    const stats = {};
    for (const sensorId in sensorGroups) {
        const values = sensorGroups[sensorId];
        const mean = values.reduce((a, b) => a + b, 0) / values.length;
        const variance = values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length;
        const stddev = Math.sqrt(variance);
        
        stats[sensorId] = {
            mean: mean,
            stddev: stddev,
            count: values.length,
            min: Math.min(...values),
            max: Math.max(...values)
        };
    }
    
    return stats;
}

// Detect Anomalies
function detectAnomalies(data, sensorStats, sigmaThreshold) {
    const anomalies = [];
    
    data.forEach(reading => {
        const stats = sensorStats[reading.sensor_id];
        const threshold = stats.mean + (sigmaThreshold * stats.stddev);
        
        if (reading.value > threshold) {
            anomalies.push({
                ...reading,
                mean: stats.mean,
                stddev: stats.stddev,
                threshold: threshold,
                deviation: (reading.value - stats.mean) / stats.stddev
            });
        }
    });
    
    return anomalies.sort((a, b) => b.deviation - a.deviation);
}

// Display Results
function displayResults(sensorStats, anomalies, sigmaThreshold) {
    document.getElementById('results').style.display = 'block';
    
    // Display sensor cards
    displaySensorCards(sensorStats, sigmaThreshold);
    
    // Display charts
    displayCharts(sensorStats, anomalies);
    
    // Display anomaly table
    displayAnomalyTable(anomalies);
}

// Display Sensor Statistics Cards
function displaySensorCards(sensorStats, sigmaThreshold) {
    const cardsContainer = document.getElementById('sensorCards');
    cardsContainer.innerHTML = '';
    
    for (const sensorId in sensorStats) {
        const stats = sensorStats[sensorId];
        const threshold = stats.mean + (sigmaThreshold * stats.stddev);
        
        const card = document.createElement('div');
        card.className = 'sensor-card';
        card.innerHTML = `
            <h3>${sensorId}</h3>
            <p><strong>Count:</strong> ${stats.count} readings</p>
            <p><strong>Mean:</strong> ${stats.mean.toFixed(2)}</p>
            <p><strong>Std Dev:</strong> ${stats.stddev.toFixed(2)}</p>
            <p><strong>Min:</strong> ${stats.min.toFixed(2)}</p>
            <p><strong>Max:</strong> ${stats.max.toFixed(2)}</p>
            <p><strong>Threshold (${sigmaThreshold}σ):</strong> ${threshold.toFixed(2)}</p>
        `;
        cardsContainer.appendChild(card);
    }
}

// Display Charts
function displayCharts(sensorStats, anomalies) {
    const sensorIds = Object.keys(sensorStats);
    const means = sensorIds.map(id => sensorStats[id].mean);
    const stddevs = sensorIds.map(id => sensorStats[id].stddev);
    
    // Destroy existing charts
    if (statsChart) statsChart.destroy();
    if (anomalyChart) anomalyChart.destroy();
    
    // Stats Chart
    const statsCtx = document.getElementById('statsChart').getContext('2d');
    statsChart = new Chart(statsCtx, {
        type: 'bar',
        data: {
            labels: sensorIds,
            datasets: [
                {
                    label: 'Mean',
                    data: means,
                    backgroundColor: 'rgba(102, 126, 234, 0.7)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2
                },
                {
                    label: 'Std Deviation',
                    data: stddevs,
                    backgroundColor: 'rgba(118, 75, 162, 0.7)',
                    borderColor: 'rgba(118, 75, 162, 1)',
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Sensor Statistics'
                }
            }
        }
    });
    
    // Anomaly Distribution Chart
    const anomalyCounts = {};
    sensorIds.forEach(id => anomalyCounts[id] = 0);
    anomalies.forEach(a => anomalyCounts[a.sensor_id]++);
    
    const anomalyCtx = document.getElementById('anomalyChart').getContext('2d');
    anomalyChart = new Chart(anomalyCtx, {
        type: 'doughnut',
        data: {
            labels: sensorIds,
            datasets: [{
                data: sensorIds.map(id => anomalyCounts[id]),
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(249, 115, 22, 0.8)',
                    'rgba(234, 179, 8, 0.8)',
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(59, 130, 246, 0.8)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Anomalies by Sensor'
                }
            }
        }
    });
}

// Display Anomaly Table
function displayAnomalyTable(anomalies) {
    const countDiv = document.getElementById('anomalyCount');
    countDiv.textContent = `🚨 Found ${anomalies.length} anomalies`;
    
    const tbody = document.querySelector('#anomalyTable tbody');
    tbody.innerHTML = '';
    
    anomalies.forEach(anomaly => {
        const row = document.createElement('tr');
        const deviationClass = anomaly.deviation > 5 ? 'deviation-high' : 'deviation-medium';
        
        row.innerHTML = `
            <td>${new Date(anomaly.timestamp).toLocaleString()}</td>
            <td>${anomaly.sensor_id}</td>
            <td>${anomaly.value.toFixed(2)}</td>
            <td>${anomaly.mean.toFixed(2)}</td>
            <td>${anomaly.stddev.toFixed(2)}</td>
            <td>${anomaly.threshold.toFixed(2)}</td>
            <td class="${deviationClass}">${anomaly.deviation.toFixed(2)}σ</td>
        `;
        tbody.appendChild(row);
    });
}