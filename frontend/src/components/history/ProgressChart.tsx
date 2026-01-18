import { useMemo } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from 'recharts';
import { type Session, prepareChartData, getScoreColor } from '../../utils/progressCalculations';

interface ProgressChartProps {
  sessions: Session[];
  className?: string;
}

export function ProgressChart({ sessions, className = '' }: ProgressChartProps) {
  const chartData = useMemo(() => prepareChartData(sessions), [sessions]);

  if (chartData.length === 0) {
    return (
      <div className={`h-48 flex items-center justify-center text-gray-500 ${className}`}>
        No session data yet
      </div>
    );
  }

  return (
    <div className={`h-48 ${className}`}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.5} />
          <XAxis
            dataKey="date"
            tick={{ fill: '#9ca3af', fontSize: 11 }}
            axisLine={{ stroke: '#4b5563' }}
            tickLine={{ stroke: '#4b5563' }}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fill: '#9ca3af', fontSize: 11 }}
            axisLine={{ stroke: '#4b5563' }}
            tickLine={{ stroke: '#4b5563' }}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.[0]) return null;
              const data = payload[0].payload;
              return (
                <div className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 shadow-lg">
                  <p className="text-xs text-gray-400">{data.fullDate}</p>
                  <p className="text-sm font-semibold" style={{ color: getScoreColor(data.score) }}>
                    Score: {data.score.toFixed(1)}
                  </p>
                  <p className="text-xs text-gray-500">{data.type} mode</p>
                </div>
              );
            }}
          />
          {/* Reference lines for score zones */}
          <ReferenceLine y={70} stroke="#22c55e" strokeDasharray="3 3" opacity={0.3} />
          <ReferenceLine y={40} stroke="#f59e0b" strokeDasharray="3 3" opacity={0.3} />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#14b8a6"
            strokeWidth={2}
            dot={({ cx, cy, payload }) => (
              <circle
                cx={cx}
                cy={cy}
                r={4}
                fill={getScoreColor(payload.score)}
                stroke="#1f2937"
                strokeWidth={2}
              />
            )}
            activeDot={{
              r: 6,
              stroke: '#14b8a6',
              strokeWidth: 2,
              fill: '#fff',
            }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
