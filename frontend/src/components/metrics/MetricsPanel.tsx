import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Target, Move } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';

interface MetricsPanelProps {
  mode: 'HOLD' | 'FOLLOW';
  jitter?: number;
  p95Jitter?: number;
  lateralJitter?: number;
  p95LateralJitter?: number;
  position?: { x: number; y: number };
  className?: string;
}

export function MetricsPanel({
  mode,
  jitter,
  p95Jitter,
  lateralJitter,
  p95LateralJitter,
  position,
  className = '',
}: MetricsPanelProps) {
  const formatValue = (val?: number) => (val !== undefined ? val.toFixed(1) : '--');

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity size={18} className="text-teal-400" />
          Real-time Metrics
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <AnimatePresence mode="wait">
            {mode === 'HOLD' ? (
              <motion.div
                key="hold-metrics"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                className="space-y-3"
              >
                <MetricRow
                  icon={<Target size={14} className="text-cyan-400" />}
                  label="Jitter"
                  value={`${formatValue(jitter)} px`}
                  highlight={jitter !== undefined && jitter < 5}
                />
                <MetricRow
                  icon={<Activity size={14} className="text-cyan-400" />}
                  label="P95 Jitter"
                  value={`${formatValue(p95Jitter)} px`}
                  highlight={p95Jitter !== undefined && p95Jitter < 10}
                />
              </motion.div>
            ) : (
              <motion.div
                key="follow-metrics"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                className="space-y-3"
              >
                <MetricRow
                  icon={<Move size={14} className="text-orange-400" />}
                  label="Lateral Jitter"
                  value={`${formatValue(lateralJitter)} px`}
                  highlight={lateralJitter !== undefined && lateralJitter < 3}
                />
                <MetricRow
                  icon={<Activity size={14} className="text-orange-400" />}
                  label="P95 Lateral"
                  value={`${formatValue(p95LateralJitter)} px`}
                  highlight={p95LateralJitter !== undefined && p95LateralJitter < 8}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Position */}
          {position && (
            <motion.div
              className="pt-2 border-t border-gray-700/50"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <MetricRow
                icon={<Target size={14} className="text-gray-400" />}
                label="Position"
                value={`(${position.x}, ${position.y})`}
              />
            </motion.div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

interface MetricRowProps {
  icon?: React.ReactNode;
  label: string;
  value: string;
  highlight?: boolean;
}

function MetricRow({ icon, label, value, highlight = false }: MetricRowProps) {
  return (
    <div className="flex items-center justify-between text-sm">
      <div className="flex items-center gap-2 text-gray-400">
        {icon}
        <span>{label}</span>
      </div>
      <motion.span
        className={`font-medium ${highlight ? 'text-green-400' : 'text-white'}`}
        key={value}
        initial={{ scale: 1.1, opacity: 0.8 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.2 }}
      >
        {value}
      </motion.span>
    </div>
  );
}
