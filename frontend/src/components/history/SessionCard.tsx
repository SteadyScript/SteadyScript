import { motion } from 'framer-motion';
import { Clock, Target, Move } from 'lucide-react';
import {
  type Session,
  formatSessionDateTime,
  getScoreColor,
  getScoreStatus,
  calculateDetectionRate,
} from '../../utils/progressCalculations';

interface SessionCardProps {
  session: Session;
  onClick: () => void;
  className?: string;
}

export function SessionCard({ session, onClick, className = '' }: SessionCardProps) {
  const scoreColor = getScoreColor(session.tremor_score);
  const status = getScoreStatus(session.tremor_score);
  const detectionRate = calculateDetectionRate(session);
  const isHold = session.type === 'HOLD';

  return (
    <motion.button
      onClick={onClick}
      className={`w-full text-left p-3 rounded-xl bg-gray-800/60 border border-gray-700/40 hover:bg-gray-800 hover:border-gray-600/50 transition-colors ${className}`}
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="flex items-start justify-between gap-3">
        {/* Score circle */}
        <div
          className="flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-sm font-bold"
          style={{
            backgroundColor: `${scoreColor}20`,
            color: scoreColor,
            border: `2px solid ${scoreColor}40`,
          }}
        >
          {Math.round(session.tremor_score)}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            {isHold ? (
              <Target size={14} className="text-cyan-400" />
            ) : (
              <Move size={14} className="text-orange-400" />
            )}
            <span
              className={`text-xs font-medium ${isHold ? 'text-cyan-400' : 'text-orange-400'}`}
            >
              {session.type}
            </span>
            <span className="text-xs text-gray-500">
              {formatSessionDateTime(session.timestamp)}
            </span>
          </div>

          <div className="mt-1 flex items-center gap-3 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <Clock size={12} />
              {session.duration_s}s
            </span>
            <span>{detectionRate}% detection</span>
          </div>

          {/* Key metric */}
          <div className="mt-1 text-xs text-gray-500">
            {isHold ? (
              <span>P95 Jitter: {session.p95_jitter?.toFixed(1)} px</span>
            ) : (
              <span>P95 Lateral: {session.p95_lateral_jitter?.toFixed(1)} px</span>
            )}
          </div>
        </div>

        {/* Status indicator */}
        <div
          className="flex-shrink-0 px-2 py-0.5 rounded text-xs capitalize"
          style={{
            backgroundColor: `${scoreColor}20`,
            color: scoreColor,
          }}
        >
          {status}
        </div>
      </div>
    </motion.button>
  );
}
