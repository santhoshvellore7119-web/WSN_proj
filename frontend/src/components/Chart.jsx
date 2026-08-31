import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const Chart = ({ data, xKey, yKeys, title, unit = '' }) => {
  if (!data || data.length === 0) {
    return <div className="chart-placeholder">No data available</div>;
  }

  // Convert data to format expected by Recharts
  const chartData = data.map((item, index) => ({
    ...item,
    name: `Round ${item[xKey] || index + 1}`,
  }));

  return (
    <div className="chart-container">
      <h3>{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip formatter={(value) => `${value} ${unit}`} />
          <Legend verticalAlign="top" height={36} />
          {yKeys.map((yKey, index) => (
            <Line
              key={yKey}
              type="monotone"
              dataKey={yKey}
              stroke={`#${['007bff', 'dc3545', '28a745', 'ffc107', '6f42c1'][index % 5]}`}
              strokeWidth={2}
              dot={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default Chart;