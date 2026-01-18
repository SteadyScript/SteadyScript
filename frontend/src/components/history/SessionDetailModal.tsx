import { Modal } from '../ui/Modal';
import { Target, Move, Clock, Eye, Activity } from 'lucide-react';
import {
  type Session,
  formatSessionDateTime,
  getScoreColor,
  getScoreStatus,
  calculateDetectionRate,
} from '../../utils/progressCalculations';

interface SessionDetailModalProps {
  session: Session | null;
  isOpen: boolean;
  onClose: () => void;
}

export function SessionDetailModal({ session, isOpen, onClose }: SessionDetailModalProps) {
  if (!session) return null;

  const scoreColor = getScoreColor(session.tremor_score);
  const status = getScoreStatus(session.tremor_score);
  const detectionRate = calculateDetectionRate(session);
  const isHold = session.type === 'HOLD';

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Session Details">
      {/* Header with score */}
      <div className="flex items-center gap-4 mb-6">
        <div
          className="w-20 h-20 rounded-full flex items-center justify-center text-2xl font-bold"
          style={{
            backgroundColor: `${scoreColor}20`,
            color: scoreColor,
            border: `3px solid ${scoreColor}60`,
          }}
        >
          {Math.round(session.tremor_score)}
        </div>
        <div>
          <div className="flex items-center gap-2 mb-1">
            {isHold ? (
              <Target size={18} className="text-cyan-400" />
            ) : (
              <Move size={18} className="text-orange-400" />
            )}
            <span
              className={`text-lg font-semibold ${isHold ? 'text-cyan-400' : 'text-orange-400'}`}
            >
              {session.type} Mode
            </span>
          </div>
          <p className="text-sm text-gray-400">{formatSessionDateTime(session.timestamp)}</p>
          <span
            className="inline-block mt-1 px-2 py-0.5 rounded text-xs capitalize"
            style={{
              backgroundColor: `${scoreColor}20`,
              color: scoreColor,
            }}
          >
            {status}
          </span>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-4">
        <StatItem
          icon={<Clock size={16} className="text-gray-400" />}
          label="Duration"
          value={`${session.duration_s}s`}
        />
        <StatItem
          icon={<Eye size={16} className="text-gray-400" />}
          label="Detection Rate"
          value={`${detectionRate}%`}
        />

        {isHold ? (
          <>
            <StatItem
              icon={<Activity size={16} className="text-cyan-400" />}
              label="Avg Jitter"
              value={`${session.avg_jitter?.toFixed(1) ?? '--'} px`}
            />
            <StatItem
              icon={<Activity size={16} className="text-cyan-400" />}
              label="P95 Jitter"
              value={`${session.p95_jitter?.toFixed(1) ?? '--'} px`}
            />
          </>
        ) : (
          <>
            <StatItem
              icon={<Activity size={16} className="text-orange-400" />}
              label="Avg Lateral"
              value={`${session.avg_lateral_jitter?.toFixed(1) ?? '--'} px`}
            />
            <StatItem
              icon={<Activity size={16} className="text-orange-400" />}
              label="P95 Lateral"
              value={`${session.p95_lateral_jitter?.toFixed(1) ?? '--'} px`}
            />
            <StatItem
              icon={<Activity size={16} className="text-orange-400" />}
              label="Max Lateral"
              value={`${session.max_lateral_jitter?.toFixed(1) ?? '--'} px`}
            />
            {session.beats_total !== undefined && (
              <StatItem
                icon={<Activity size={16} className="text-orange-400" />}
                label="Beats"
                value={`${session.beats_total}`}
              />
            )}
          </>
        )}

        <StatItem
          icon={<Eye size={16} className="text-gray-400" />}
          label="Frames Total"
          value={`${session.frames_total}`}
        />
        <StatItem
          icon={<Eye size={16} className="text-gray-400" />}
          label="Frames Detected"
          value={`${session.frames_marker_found}`}
        />
      </div>

      {/* Tips based on performance */}
      <div className="mt-6 p-3 rounded-lg bg-gray-700/30 border border-gray-700/50">
        <h4 className="text-sm font-medium text-gray-300 mb-2">Tips</h4>
        <p className="text-xs text-gray-400">
          {session.tremor_score >= 70
            ? 'Excellent stability! Keep practicing to maintain this level.'
            : session.tremor_score >= 40
              ? 'Good progress. Try anchoring your wrist on the table for better stability.'
              : 'Room for improvement. Practice slow, controlled movements and ensure good lighting for marker detection.'}
        </p>
      </div>
    </Modal>
  );
}

interface StatItemProps {
  icon: React.ReactNode;
  label: string;
  value: string;
}

function StatItem({ icon, label, value }: StatItemProps) {
  return (
    <div className="p-3 rounded-lg bg-gray-700/30 border border-gray-700/50">
      <div className="flex items-center gap-2 mb-1">
        {icon}
        <span className="text-xs text-gray-400">{label}</span>
      </div>
      <p className="text-sm font-semibold text-white">{value}</p>
    </div>
  );
}
