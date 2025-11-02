import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

function VitalsChart({ readings }) {
  // Prepare data for the chart
  const chartData = readings
    .slice()
    .reverse() // Show oldest to newest
    .map((reading, index) => {
      // Parse systolic blood pressure for charting
      const systolic = parseInt(reading.blood_pressure.split('/')[0]);
      
      return {
        index: index + 1,
        date: new Date(reading.recorded_at).toLocaleDateString(),
        time: new Date(reading.recorded_at).toLocaleTimeString([], { 
          hour: '2-digit', 
          minute: '2-digit' 
        }),
        heart_rate: reading.heart_rate,
        temperature: reading.temperature,
        oxygen_saturation: reading.oxygen_saturation,
        systolic_bp: systolic,
        fullDate: new Date(reading.recorded_at).toLocaleString()
      };
    });

  // Custom tooltip to show all vital signs
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{
          backgroundColor: 'white',
          padding: '15px',
          border: '1px solid #ccc',
          borderRadius: '8px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
        }}>
          <p style={{ margin: '0 0 10px 0', fontWeight: 'bold' }}>
            {data.fullDate}
          </p>
          <p style={{ margin: '5px 0', color: '#8884d8' }}>
            Heart Rate: {data.heart_rate} bpm
          </p>
          <p style={{ margin: '5px 0', color: '#82ca9d' }}>
            Temperature: {data.temperature}°F
          </p>
          <p style={{ margin: '5px 0', color: '#ffc658' }}>
            O2 Saturation: {data.oxygen_saturation}%
          </p>
          <p style={{ margin: '5px 0', color: '#ff7300' }}>
            Systolic BP: {data.systolic_bp} mmHg
          </p>
        </div>
      );
    }
    return null;
  };

  if (!readings || readings.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
        No vital signs data to display
      </div>
    );
  }

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={chartData}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 60
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date"
            angle={-45}
            textAnchor="end"
            height={80}
            fontSize={12}
          />
          <YAxis 
            yAxisId="left"
            orientation="left"
            domain={['dataMin - 10', 'dataMax + 10']}
          />
          <YAxis 
            yAxisId="right"
            orientation="right"
            domain={[95, 105]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="heart_rate"
            stroke="#8884d8"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Heart Rate (bpm)"
          />
          
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="temperature"
            stroke="#82ca9d"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Temperature (°F)"
          />
          
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="oxygen_saturation"
            stroke="#ffc658"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="O2 Saturation (%)"
          />
          
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="systolic_bp"
            stroke="#ff7300"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Systolic BP (mmHg)"
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div style={{ 
        marginTop: '20px', 
        fontSize: '0.9rem', 
        color: '#666',
        textAlign: 'center'
      }}>
        Showing {readings.length} readings over time
      </div>
    </div>
  );
}

export default VitalsChart;