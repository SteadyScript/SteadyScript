import { AnimatePresence, motion } from 'framer-motion';
import { ChevronDown, History, Minus, Move, RefreshCw, Target, TrendingDown, TrendingUp } from 'lucide-react';
import { useState } from 'react';
import { useSessionHistory } from '../../hooks/useSessionHistory';
import { staggerContainer, staggerItem } from '../../styles/animations';
import {
  type Session,
  formatSessionDateTime,
  getScoreColor,
  getTrendSymbol,
} from '../../utils/progressCalculations';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { SessionDetailModal } from './SessionDetailModal';

interface SessionHistoryProps {
  className?: string;
}

// Compact horizontal session row
function SessionRow({
  session,
  index,
  onClick,
}: {
  session: Session;
  index: number;
  onClick: () => void;
}) {
  const scoreColor = getScoreColor(session.tremor_score);
  const isHold = session.type === 'HOLD';

  return (
    <motion.button
      onClick={onClick}
      className="w-full text-left p-3 rounded-xl border transition-all hover:border-opacity-60"
      style={{
        background: 'linear-gradient(145deg, rgba(30, 33, 40, 0.6) 0%, rgba(25, 28, 34, 0.8) 100%)',
        borderColor: '#2a2f3830',
      }}
      variants={staggerItem}
      whileHover={{ y: -2, backgroundColor: 'rgba(37, 41, 50, 0.8)' }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="flex items-center gap-4">
        {/* Session number */}
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gray-700/50 flex items-center justify-center">
          <span className="text-xs font-bold text-gray-400">#{index + 1}</span>
        </div>

        {/* Score circle */}
        <div
          className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold"
          style={{
            backgroundColor: `${scoreColor}15`,
            color: scoreColor,
            border: `2px solid ${scoreColor}40`,
            boxShadow: `0 0 12px ${scoreColor}20`,
          }}
        >
          {Math.round(session.tremor_score)}
        </div>

        {/* Test type cards - horizontal layout */}
        <div className="flex-1 flex gap-2">
          {/* HOLD card */}
          <div
            className={`flex-1 px-3 py-2 rounded-lg border ${isHold ? 'opacity-100' : 'opacity-40'
              }`}
            style={{
              background: isHold ? 'rgba(14, 165, 233, 0.1)' : 'rgba(30, 33, 40, 0.5)',
              borderColor: isHold ? 'rgba(14, 165, 233, 0.3)' : 'transparent',
            }}
          >
            <div className="flex items-center gap-1.5 mb-1">
              <Target size={12} className="text-cyan-400" />
              <span className="text-[10px] font-semibold text-cyan-400 uppercase">HOLD</span>
            </div>
            {isHold && (
              <div className="text-xs text-gray-300">
                <span className="font-medium">{session.p95_jitter?.toFixed(1) ?? '--'}</span>
                <span className="text-gray-500 ml-1">P95</span>
              </div>
            )}
          </div>

          {/* FOLLOW card */}
          <div
            className={`flex-1 px-3 py-2 rounded-lg border ${!isHold ? 'opacity-100' : 'opacity-40'
              }`}
            style={{
              background: !isHold ? 'rgba(249, 115, 22, 0.1)' : 'rgba(30, 33, 40, 0.5)',
              borderColor: !isHold ? 'rgba(249, 115, 22, 0.3)' : 'transparent',
            }}
          >
            <div className="flex items-center gap-1.5 mb-1">
              <Move size={12} className="text-orange-400" />
              <span className="text-[10px] font-semibold text-orange-400 uppercase">FOLLOW</span>
            </div>
            {!isHold && (
              <div className="text-xs text-gray-300">
                <span className="font-medium">{session.p95_lateral_jitter?.toFixed(1) ?? '--'}</span>
                <span className="text-gray-500 ml-1">P95</span>
              </div>
            )}
          </div>
        </div>

        {/* Timestamp */}
        <div className="flex-shrink-0 text-right">
          <div className="text-xs text-gray-500">
            {formatSessionDateTime(session.timestamp)}
          </div>
          <div className="text-[10px] text-gray-600">{session.duration_s}s</div>
        </div>
      </div>
    </motion.button>
  );
}

export function SessionHistory({ className = '' }: SessionHistoryProps) {
  const { sessions, isLoading, error, trend, trendPercent, refetch } = useSessionHistory(20);
  const [isExpanded, setIsExpanded] = useState(true);
  const [selectedSession, setSelectedSession] = useState<Session | null>(null);

  const TrendIcon =
    trend === 'improving' ? TrendingUp : trend === 'declining' ? TrendingDown : Minus;
  const trendColor =
    trend === 'improving'
      ? 'text-emerald-400'
      : trend === 'declining'
        ? 'text-rose-400'
        : 'text-gray-400';

  return (
    <>
      <Card className={className}>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{ background: 'rgba(20, 184, 166, 0.15)' }}
            >
              <History size={16} className="text-teal-400" />
            </div>
            <span>Performance History</span>
          </CardTitle>
          <div className="flex items-center gap-3">
            {/* Trend indicator */}
            <motion.div
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg ${trendColor}`}
              style={{ background: 'rgba(30, 33, 40, 0.8)' }}
              whileHover={{ scale: 1.05 }}
            >
              <TrendIcon size={14} />
              <span className="text-xs font-medium">
                {getTrendSymbol(trend)} {Math.abs(trendPercent).toFixed(0)}%
              </span>
            </motion.div>

            {/* Refresh button */}
            <motion.button
              onClick={refetch}
              disabled={isLoading}
              className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-gray-700/50"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
            </motion.button>

            {/* Expand/collapse button */}
            <motion.button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-gray-700/50"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <motion.div
                animate={{ rotate: isExpanded ? 0 : -90 }}
                transition={{ duration: 0.2 }}
              >
                <ChevronDown size={16} />
              </motion.div>
            </motion.button>
          </div>
        </CardHeader>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <CardContent>
                {error ? (
                  <div className="py-8 text-center">
                    <p className="text-rose-400 text-sm">{error}</p>
                    <button
                      onClick={refetch}
                      className="mt-2 text-xs text-teal-400 hover:underline"
                    >
                      Try again
                    </button>
                  </div>
                ) : (
                  <motion.div
                    className="space-y-2 max-h-[393px] overflow-y-auto pr-2"
                    variants={staggerContainer}
                    initial="initial"
                    animate="animate"
                  >
                    {isLoading ? (
                      <div className="py-4 text-center text-gray-500 text-sm">
                        Loading sessions...
                      </div>
                    ) : sessions.length === 0 ? (
                      <div className="py-8 text-center">
                        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gray-800/50 flex items-center justify-center">
                          <History size={24} className="text-gray-600" />
                        </div>
                        <p className="text-gray-500 text-sm">
                          No sessions yet. Complete a session to see your history.
                        </p>
                      </div>
                    ) : (
                      sessions.map((session, index) => (
                        <SessionRow
                          key={`${session.timestamp}-${index}`}
                          session={session}
                          index={sessions.length - 1 - index}
                          onClick={() => setSelectedSession(session)}
                        />
                      ))
                    )}
                  </motion.div>
                )}
              </CardContent>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>

      {/* Detail modal */}
      <SessionDetailModal
        session={selectedSession}
        isOpen={selectedSession !== null}
        onClose={() => setSelectedSession(null)}
      />
    </>
  );
}
