import { motion } from 'framer-motion';
import { useMemo } from 'react';
import { type Session, prepareChartData } from '../../utils/progressCalculations';

interface ProgressGraphProps {
  sessions: Session[];
  className?: string;
}

export function ProgressGraph({ sessions, className = '' }: ProgressGraphProps) {
  const chartData = useMemo(() => prepareChartData(sessions), [sessions]);

  // Chart dimensions
  const width = 400;
  const height = 180;
  const padding = { top: 20, right: 20, bottom: 30, left: 40 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Scale functions
  const xScale = (index: number) => {
    if (chartData.length <= 1) return chartWidth / 2;
    return (index / (chartData.length - 1)) * chartWidth;
  };

  const yScale = (score: number) => {
    return chartHeight - (score / 100) * chartHeight;
  };

  // Generate path for the line
  const linePath = useMemo(() => {
    if (chartData.length === 0) return '';
    return chartData
      .map((point, i) => {
        const x = xScale(i);
        const y = yScale(point.score);
        return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
      })
      .join(' ');
  }, [chartData]);

  // Generate area path (for fill below line)
  const areaPath = useMemo(() => {
    if (chartData.length === 0) return '';
    const linePoints = chartData
      .map((point, i) => {
        const x = xScale(i);
        const y = yScale(point.score);
        return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
      })
      .join(' ');
    return `${linePoints} L ${xScale(chartData.length - 1)} ${chartHeight} L ${xScale(0)} ${chartHeight} Z`;
  }, [chartData, chartHeight]);

  // Y-axis labels
  const yLabels = [0, 25, 50, 75, 100];

  // X-axis labels (show first, middle, last dates)
  const xLabels = useMemo(() => {
    if (chartData.length === 0) return [];
    if (chartData.length === 1) return [{ label: chartData[0].date, x: xScale(0) }];
    if (chartData.length === 2) {
      return [
        { label: chartData[0].date, x: xScale(0) },
        { label: chartData[1].date, x: xScale(1) },
      ];
    }
    const mid = Math.floor(chartData.length / 2);
    return [
      { label: chartData[0].date, x: xScale(0) },
      { label: chartData[mid].date, x: xScale(mid) },
      { label: chartData[chartData.length - 1].date, x: xScale(chartData.length - 1) },
    ];
  }, [chartData]);

  if (sessions.length === 0) {
    return (
      <div className={`flex items-center justify-center h-[180px] ${className}`}>
        <p className="text-gray-500 text-sm">No session data to display</p>
      </div>
    );
  }

  return (
    <div className={className}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-auto"
        style={{ maxHeight: '180px' }}
      >
        <defs>
          {/* Gradient for area fill */}
          <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#14b8a6" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#14b8a6" stopOpacity="0" />
          </linearGradient>
          {/* Gradient for line */}
          <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#0ea5e9" />
            <stop offset="100%" stopColor="#14b8a6" />
          </linearGradient>
        </defs>

        <g transform={`translate(${padding.left}, ${padding.top})`}>
          {/* Y-axis grid lines and labels */}
          {yLabels.map((label) => (
            <g key={label}>
              <line
                x1={0}
                y1={yScale(label)}
                x2={chartWidth}
                y2={yScale(label)}
                stroke="#374151"
                strokeWidth="1"
                strokeDasharray="4,4"
              />
              <text
                x={-8}
                y={yScale(label)}
                fill="#6b7280"
                fontSize="10"
                textAnchor="end"
                dominantBaseline="middle"
              >
                {label}
              </text>
            </g>
          ))}

          {/* X-axis labels */}
          {xLabels.map((item, i) => (
            <text
              key={i}
              x={item.x}
              y={chartHeight + 18}
              fill="#6b7280"
              fontSize="10"
              textAnchor="middle"
            >
              {item.label}
            </text>
          ))}

          {/* Area fill */}
          {chartData.length > 0 && (
            <motion.path
              d={areaPath}
              fill="url(#areaGradient)"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            />
          )}

          {/* Line */}
          {chartData.length > 0 && (
            <motion.path
              d={linePath}
              fill="none"
              stroke="url(#lineGradient)"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1, ease: 'easeOut' }}
            />
          )}

          {/* Data points */}
          {chartData.map((point, i) => {
            const isHold = point.type === 'HOLD';
            const color = isHold ? '#0ea5e9' : '#f97316';
            return (
              <motion.g
                key={i}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.5 + i * 0.05 }}
              >
                <circle
                  cx={xScale(i)}
                  cy={yScale(point.score)}
                  r="5"
                  fill={color}
                  stroke="#1e2128"
                  strokeWidth="2"
                />
                {/* Tooltip hover area (invisible, larger) */}
                <circle
                  cx={xScale(i)}
                  cy={yScale(point.score)}
                  r="12"
                  fill="transparent"
                  style={{ cursor: 'pointer' }}
                >
                  <title>{`${point.fullDate}\nScore: ${point.score.toFixed(0)}\nType: ${point.type}`}</title>
                </circle>
              </motion.g>
            );
          })}
        </g>
      </svg>

      {/* Legend */}
      <div className="flex items-center justify-center gap-4 mt-2">
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-cyan-500" />
          <span className="text-xs text-gray-400">HOLD</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-orange-500" />
          <span className="text-xs text-gray-400">FOLLOW</span>
        </div>
      </div>
    </div>
  );
}
