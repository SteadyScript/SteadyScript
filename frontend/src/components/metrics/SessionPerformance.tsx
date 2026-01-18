import { motion } from 'framer-motion';
import { Activity, Target, Move, Zap, Info } from 'lucide-react';
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

  // Tips based on mode and status
  const getTip = () => {
    if (isRunning) {
      if (isHold) {
        return 'Keep your hand as still as possible. Focus on a fixed point.';
      }
      return 'Follow the target smoothly. Avoid jerky movements.';
    }
    if (sessionState === 'COMPLETE') {
      if (score >= 70) return 'Excellent performance! Your stability is improving.';
      if (score >= 40) return 'Good effort! Try to relax your hand muscles more.';
      return 'Keep practicing! Focus on smooth, controlled movements.';
    }
    if (isHold) {
      return 'Position your marker and click START to begin the stability test.';
    }
    return 'Adjust your BPM in the header, then click START to begin.';
  };

  return (
    <Card
      variant={isRunning ? 'glow' : 'default'}
      glowMode={isHold ? 'hold' : 'follow'}
      className={`flex flex-col ${className}`}
    >
      <CardContent className="flex flex-col h-full">
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
        <div className="py-6 flex flex-col items-center">
          <motion.div
            key={Math.floor(score / 5)}
            initial={{ scale: 0.95, opacity: 0.8 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            <span
              className="text-7xl font-bold tabular-nums"
              style={{ color: statusColor }}
            >
              {Math.round(score)}
            </span>
            <span className="text-2xl text-gray-500 ml-1">%</span>
          </motion.div>

          {/* Status badge - below the score */}
          <motion.div
            className="mt-3 inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium capitalize"
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

        {/* Test type cards - show BOTH with active one highlighted */}
        <div className="space-y-3 flex-1">
          <TestCard
            mode="HOLD"
            title="Stability Test"
            primaryValue={p95Jitter}
            primaryLabel="P95 Jitter (px)"
            secondaryValue={jitter}
            secondaryLabel="Avg Jitter"
            status={isHold ? scoreStatus : undefined}
            compact
            className={!isHold ? 'opacity-40' : ''}
          />

          <TestCard
            mode="FOLLOW"
            title="Movement Test"
            primaryValue={p95LateralJitter}
            primaryLabel="P95 Lateral (px)"
            secondaryValue={lateralJitter}
            secondaryLabel="Avg Lateral"
            status={!isHold ? scoreStatus : undefined}
            compact
            className={isHold ? 'opacity-40' : ''}
          />
        </div>

        {/* Session Tip */}
        <div className="mt-4 pt-4 border-t border-gray-700/50">
          <div className="flex items-start gap-2 p-3 rounded-xl bg-gray-800/50">
            <div className="flex-shrink-0 mt-0.5">
              {isRunning ? (
                <Zap size={14} className="text-amber-400" />
              ) : (
                <Info size={14} className="text-gray-500" />
              )}
            </div>
            <p className="text-xs text-gray-400 leading-relaxed">{getTip()}</p>
          </div>
        </div>

        {/* Quick mode labels */}
        <div className="flex items-center justify-center gap-4 mt-4 pt-3 border-t border-gray-700/50">
          <div className={`flex items-center gap-1.5 ${isHold ? '' : 'opacity-40'}`}>
            <Target size={14} className="text-cyan-400" />
            <span className="text-xs text-gray-400">HOLD</span>
          </div>
          <div className={`flex items-center gap-1.5 ${!isHold ? '' : 'opacity-40'}`}>
            <Move size={14} className="text-orange-400" />
            <span className="text-xs text-gray-400">FOLLOW</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
