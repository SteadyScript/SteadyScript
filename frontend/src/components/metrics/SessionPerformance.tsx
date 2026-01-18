import { motion } from 'framer-motion';
import { Activity, Target, Move } from 'lucide-react';
import { Card, CardContent, TestCard } from '../ui/Card';
import { getScoreStatus } from '../../utils/progressCalculations';

interface SessionPerformanceProps {
  score: number;
  status: string;
  mode: 'HOLD' | 'FOLLOW';
  sessionState: 'IDLE' | 'RUNNING' | 'COMPLETE';
  timeRemaining?: number;
  totalTime?: number;
  // HOLD metrics
  jitter?: number;
  p95Jitter?: number;
  // FOLLOW metrics
  lateralJitter?: number;
  p95LateralJitter?: number;
  className?: string;
}

export function SessionPerformance({
  score,
  status,
  mode,
  sessionState,
  timeRemaining = 0,
  totalTime = 30,
  jitter = 0,
  p95Jitter = 0,
  lateralJitter = 0,
  p95LateralJitter = 0,
  className = '',
}: SessionPerformanceProps) {
  const isHold = mode === 'HOLD';
  const isRunning = sessionState === 'RUNNING';
  const progress = totalTime > 0 ? ((totalTime - timeRemaining) / totalTime) * 100 : 0;

  // Get status color
  const getStatusColor = () => {
    const normalized = status.toLowerCase();
    if (normalized === 'stable' || normalized === 'good') return '#10b981';
    if (normalized === 'warning' || normalized === 'moderate') return '#f59e0b';
    return '#f43f5e';
  };

  const statusColor = getStatusColor();
  const scoreStatus = getScoreStatus(score);

  return (
    <Card
      variant={isRunning ? 'glow' : 'default'}
      glowMode={isHold ? 'hold' : 'follow'}
      className={className}
    >
      <CardContent>
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Activity size={18} className="text-gray-400" />
            <span className="text-sm font-medium text-gray-300">Session Performance</span>
          </div>
          <div
            className="px-2 py-1 rounded-lg text-xs font-medium uppercase tracking-wide"
            style={{
              backgroundColor: `${isHold ? '#0ea5e9' : '#f97316'}15`,
              color: isHold ? '#0ea5e9' : '#f97316',
            }}
          >
            {mode}
          </div>
        </div>

        {/* Large Score Display */}
        <div className="text-center py-4">
          <motion.div
            className="relative inline-block"
            key={Math.floor(score / 5)}
            initial={{ scale: 0.95, opacity: 0.8 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            <span
              className="text-6xl font-bold tabular-nums"
              style={{ color: statusColor }}
            >
              {Math.round(score)}
            </span>
            <span className="text-xl text-gray-500 ml-1">%</span>
          </motion.div>

          {/* Status badge */}
          <motion.div
            className="mt-2 inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium capitalize"
            style={{
              backgroundColor: `${statusColor}15`,
              color: statusColor,
              border: `1px solid ${statusColor}30`,
            }}
            initial={{ y: 5, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: statusColor }}
            />
            {status}
          </motion.div>
        </div>

        {/* Progress bar (when running) */}
        {isRunning && (
          <div className="mb-4">
            <div className="h-2 bg-gray-700/50 rounded-full overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                style={{
                  background: isHold
                    ? 'linear-gradient(90deg, #0ea5e9 0%, #14b8a6 100%)'
                    : 'linear-gradient(90deg, #f97316 0%, #fb923c 100%)',
                }}
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
            <div className="flex justify-between mt-1 text-xs text-gray-500">
              <span>{Math.round(totalTime - timeRemaining)}s</span>
              <span>{totalTime}s</span>
            </div>
          </div>
        )}

        {/* Test type cards */}
        <div className="space-y-3">
          {isHold ? (
            <TestCard
              mode="HOLD"
              title="Stability Test"
              primaryValue={p95Jitter}
              primaryLabel="P95 Jitter (px)"
              secondaryValue={jitter}
              secondaryLabel="Avg Jitter"
              status={scoreStatus}
              compact
            />
          ) : (
            <TestCard
              mode="FOLLOW"
              title="Movement Test"
              primaryValue={p95LateralJitter}
              primaryLabel="P95 Lateral (px)"
              secondaryValue={lateralJitter}
              secondaryLabel="Avg Lateral"
              status={scoreStatus}
              compact
            />
          )}
        </div>

        {/* Quick metric labels */}
        <div className="flex items-center justify-center gap-4 mt-4 pt-3 border-t border-gray-700/50">
          <div className="flex items-center gap-1.5">
            <Target size={14} className="text-cyan-400" />
            <span className="text-xs text-gray-400">HOLD</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Move size={14} className="text-orange-400" />
            <span className="text-xs text-gray-400">FOLLOW</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
