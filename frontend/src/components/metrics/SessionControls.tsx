import { motion, AnimatePresence } from 'framer-motion';
import { Play, Square, Clock, Music, ChevronUp, ChevronDown } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';

interface SessionControlsProps {
  sessionState: 'IDLE' | 'RUNNING' | 'COMPLETE';
  elapsed?: number;
  timeRemaining?: number;
  bpm?: number;
  beatCount?: number;
  mode: 'HOLD' | 'FOLLOW';
  markerDetected: boolean;
  onStart: () => void;
  onStop: () => void;
  onBPMChange: (delta: number) => void;
  className?: string;
}

export function SessionControls({
  sessionState,
  elapsed = 0,
  timeRemaining = 0,
  bpm = 60,
  beatCount = 0,
  mode,
  markerDetected,
  onStart,
  onStop,
  onBPMChange,
  className = '',
}: SessionControlsProps) {
  const isRunning = sessionState === 'RUNNING';
  const modeColor = mode === 'HOLD' ? 'cyan' : 'orange';

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock size={18} className="text-teal-400" />
          Session
        </CardTitle>
      </CardHeader>
      <CardContent>
        <AnimatePresence mode="wait">
          {isRunning ? (
            <motion.div
              key="running"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              {/* Timer display */}
              <div className="flex items-center justify-center py-4">
                <motion.div
                  className="text-5xl font-bold tabular-nums text-white"
                  key={Math.floor(timeRemaining)}
                  initial={{ scale: 1.1 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.1 }}
                >
                  {timeRemaining.toFixed(1)}
                  <span className="text-xl text-gray-500 ml-1">s</span>
                </motion.div>
              </div>

              {/* Progress bar */}
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  className={`h-full bg-gradient-to-r ${
                    mode === 'HOLD'
                      ? 'from-cyan-500 to-cyan-400'
                      : 'from-orange-500 to-orange-400'
                  }`}
                  initial={{ width: '100%' }}
                  animate={{ width: `${(timeRemaining / (elapsed + timeRemaining)) * 100}%` }}
                  transition={{ duration: 0.1 }}
                />
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="flex justify-between text-gray-400">
                  <span>Elapsed:</span>
                  <span className="text-white">{elapsed.toFixed(1)}s</span>
                </div>
                {mode === 'FOLLOW' && (
                  <>
                    <div className="flex justify-between text-gray-400">
                      <span>BPM:</span>
                      <span className="text-white">{bpm}</span>
                    </div>
                    <div className="flex justify-between text-gray-400 col-span-2">
                      <span>
                        <Music size={14} className="inline mr-1" />
                        Beats:
                      </span>
                      <span className="text-white">{beatCount}</span>
                    </div>
                  </>
                )}
              </div>

              {/* Stop button */}
              <motion.button
                onClick={onStop}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-red-600 hover:bg-red-500 rounded-lg text-sm font-medium transition-colors"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Square size={16} />
                Stop Session
              </motion.button>
            </motion.div>
          ) : (
            <motion.div
              key="idle"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              {/* BPM controls for FOLLOW mode */}
              {mode === 'FOLLOW' && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400 text-sm">BPM</span>
                    <div className="flex items-center gap-2">
                      <motion.button
                        onClick={() => onBPMChange(-5)}
                        className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <ChevronDown size={16} />
                      </motion.button>
                      <span className="w-12 text-center text-xl font-bold text-orange-400">
                        {bpm}
                      </span>
                      <motion.button
                        onClick={() => onBPMChange(5)}
                        className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <ChevronUp size={16} />
                      </motion.button>
                    </div>
                  </div>
                </div>
              )}

              {/* Start button */}
              <motion.button
                onClick={onStart}
                disabled={!markerDetected}
                className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  markerDetected
                    ? `bg-${modeColor}-600 hover:bg-${modeColor}-500`
                    : 'bg-gray-600 cursor-not-allowed'
                } ${
                  mode === 'HOLD'
                    ? 'bg-cyan-600 hover:bg-cyan-500'
                    : 'bg-orange-600 hover:bg-orange-500'
                } disabled:bg-gray-600 disabled:cursor-not-allowed`}
                whileHover={markerDetected ? { scale: 1.02 } : {}}
                whileTap={markerDetected ? { scale: 0.98 } : {}}
              >
                <Play size={16} />
                Start Session
              </motion.button>

              {/* Helper text */}
              {!markerDetected && (
                <motion.p
                  className="text-center text-xs text-amber-400"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  Position marker in camera view to begin
                </motion.p>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  );
}
