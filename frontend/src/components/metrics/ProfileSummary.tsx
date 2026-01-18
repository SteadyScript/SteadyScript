import { motion } from 'framer-motion';
import { BarChart2, Grid3X3, TrendingUp, Trophy, User } from 'lucide-react';
import { useState } from 'react';
import { type Session } from '../../utils/progressCalculations';
import { Card, CardContent } from '../ui/Card';
import { CircularProgress } from '../ui/CircularProgress';
import { ProgressGraph } from '../ui/ProgressGraph';
import { StreakIndicator } from '../ui/StreakIndicator';

interface ProfileStats {
  currentStreak: number;
  totalSessions: number;
  avgJitterScore: number;
  avgTremorScore: number;
  bestJitterScore: number;
  bestTremorScore: number;
}

interface ProfileSummaryProps {
  stats: ProfileStats;
  sessions?: Session[];
  className?: string;
}

export function ProfileSummary({ stats, sessions = [], className = '' }: ProfileSummaryProps) {
  const [showGraph, setShowGraph] = useState(false);
  const {
    currentStreak,
    totalSessions,
    avgJitterScore,
    avgTremorScore,
    bestJitterScore,
    bestTremorScore,
  } = stats;

  return (
    <Card className={className}>
      <CardContent>
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <User size={18} className="text-gray-400" />
            <span className="text-sm font-medium text-gray-300">Profile Summary</span>
          </div>
          <div className="flex items-center gap-2">
            {/* View toggle */}
            <div className="flex items-center bg-gray-800/50 rounded-lg p-0.5">
              <button
                onClick={() => setShowGraph(false)}
                className={`p-1.5 rounded-md transition-colors ${
                  !showGraph ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'
                }`}
              >
                <Grid3X3 size={14} />
              </button>
              <button
                onClick={() => setShowGraph(true)}
                className={`p-1.5 rounded-md transition-colors ${
                  showGraph ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'
                }`}
              >
                <BarChart2 size={14} />
              </button>
            </div>
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <span>{totalSessions}</span>
              <span>sessions</span>
            </div>
          </div>
        </div>

        {showGraph ? (
          <>
            {/* Graph View */}
            <div className="mb-4">
              <ProgressGraph sessions={sessions} />
            </div>

            {/* Compact stats below graph */}
            <div className="grid grid-cols-2 gap-3 pt-4 border-t border-gray-700/50">
              <div className="text-center p-2 rounded-lg bg-gray-800/30">
                <div className="text-lg font-bold text-cyan-400">{avgJitterScore.toFixed(0)}</div>
                <div className="text-xs text-gray-500">Avg Jitter</div>
              </div>
              <div className="text-center p-2 rounded-lg bg-gray-800/30">
                <div className="text-lg font-bold text-orange-400">{avgTremorScore.toFixed(0)}</div>
                <div className="text-xs text-gray-500">Avg Tremor</div>
              </div>
            </div>
          </>
        ) : (
          <>
            {/* Streak Section */}
            <div className="mb-6">
              <StreakIndicator
                currentStreak={currentStreak}
                targetStreak={7}
              />
            </div>

            {/* Progress Gauges */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="text-center">
                <CircularProgress
                  value={avgJitterScore}
                  max={100}
                  size={80}
                  strokeWidth={6}
                  gradientColors={['#0ea5e9', '#14b8a6']}
                  glowColor="rgba(14, 165, 233, 0.3)"
                  label="Jitter"
                />
                <p className="text-xs text-gray-500 mt-2">Avg Score</p>
              </div>
              <div className="text-center">
                <CircularProgress
                  value={avgTremorScore}
                  max={100}
                  size={80}
                  strokeWidth={6}
                  gradientColors={['#f97316', '#fb923c']}
                  glowColor="rgba(249, 115, 22, 0.3)"
                  label="Tremor"
                />
                <p className="text-xs text-gray-500 mt-2">Avg Score</p>
              </div>
            </div>

            {/* Best Scores */}
            <div className="border-t border-gray-700/50 pt-4">
              <div className="flex items-center gap-2 mb-3">
                <Trophy size={14} className="text-amber-400" />
                <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                  Best Scores
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <motion.div
                  className="p-3 rounded-xl bg-gradient-to-br from-cyan-500/10 to-transparent border border-cyan-500/20"
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="text-xs text-cyan-400 mb-1">Best Jitter</div>
                  <div className="text-xl font-bold text-white">
                    {bestJitterScore.toFixed(1)}
                    <span className="text-xs text-gray-500 ml-1">px</span>
                  </div>
                </motion.div>

                <motion.div
                  className="p-3 rounded-xl bg-gradient-to-br from-orange-500/10 to-transparent border border-orange-500/20"
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="text-xs text-orange-400 mb-1">Best Tremor</div>
                  <div className="text-xl font-bold text-white">
                    {bestTremorScore.toFixed(0)}
                    <span className="text-xs text-gray-500 ml-1">/100</span>
                  </div>
                </motion.div>
              </div>
            </div>
          </>
        )}

        {/* Trend indicator */}
        <div className="flex items-center justify-center gap-2 mt-4 pt-3 border-t border-gray-700/50">
          <TrendingUp size={14} className="text-emerald-400" />
          <span className="text-xs text-gray-400">Keep practicing for better results!</span>
        </div>
      </CardContent>
    </Card>
  );
}
