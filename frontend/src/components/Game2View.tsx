import { motion } from 'framer-motion';
import { Activity } from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useGame2WebSocket } from '../hooks/useGame2WebSocket';
import { useProfileStats } from '../hooks/useProfileStats';
import { useSessionHistory } from '../hooks/useSessionHistory';
import { CameraSection } from './camera/CameraSection';
import { SessionHistory } from './history/SessionHistory';
import { ProfileSummary } from './metrics/ProfileSummary';
import { SessionPerformance } from './metrics/SessionPerformance';
import { Card, CardContent } from './ui/Card';
import { GradientOrbs } from './ui/GradientOrbs';
import { HelpModal } from './ui/HelpModal';

export function Game2View() {
  const {
    isConnected,
    frameData,
    metrics,
    sessionResults,
    switchMode,
    startSession,
    stopSession,
    changeBPM,
    handleCalibrationClick,
    handleKeyboard,
  } = useGame2WebSocket();

  const { sessions, refetch: refetchSessions } = useSessionHistory();
  const profileStats = useProfileStats(sessions);
  const [dismissedResultsId, setDismissedResultsId] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [currentMode, setCurrentMode] = useState<'HOLD' | 'FOLLOW'>('HOLD');
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  // Create a unique ID for current session results to track dismissal
  const resultsId = sessionResults ? JSON.stringify(sessionResults) : null;

  // Derive local session results - show if exists and not dismissed
  const localSessionResults = resultsId && resultsId !== dismissedResultsId ? sessionResults : null;

  // Refetch sessions when new results arrive (side effect only, no state sync)
  useEffect(() => {
    if (sessionResults) {
      refetchSessions();
    }
  }, [sessionResults, refetchSessions]);

  // Handle mode change
  const handleModeChange = useCallback(
    (mode: 'HOLD' | 'FOLLOW') => {
      setCurrentMode(mode);
      switchMode(mode);
      setDismissedResultsId(resultsId); // Dismiss any current results when switching modes
    },
    [switchMode, resultsId]
  );

  // Handle canvas click for calibration
  const handleCanvasClick = useCallback(
    (x: number, y: number) => {
      if (currentMode === 'HOLD') {
        handleCalibrationClick(x, y);
      }
    },
    [currentMode, handleCalibrationClick]
  );

  // Handle dismissing results
  const handleDismissResults = useCallback(() => {
    setDismissedResultsId(resultsId);
    handleKeyboard(' ');
  }, [handleKeyboard, resultsId]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      if (e.key === '1') {
        handleModeChange('HOLD');
      } else if (e.key === '2') {
        handleModeChange('FOLLOW');
      } else if (e.key === ' ') {
        e.preventDefault();
        if (metrics?.session_state === 'IDLE') {
          startSession();
        } else if (metrics?.session_state === 'RUNNING') {
          stopSession();
        } else if (metrics?.session_state === 'COMPLETE') {
          handleDismissResults();
        }
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        changeBPM(5);
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        changeBPM(-5);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [metrics, handleModeChange, startSession, stopSession, changeBPM, handleDismissResults]);

  // Get stability status
  const getStatus = () => {
    if (currentMode === 'HOLD') {
      return metrics?.stability_level ?? 'unknown';
    }
    return metrics?.feedback_status ?? 'unknown';
  };

  const sessionState = (metrics?.session_state as 'IDLE' | 'RUNNING' | 'COMPLETE') ?? 'IDLE';
  const isRunning = sessionState === 'RUNNING';

  return (
    <div className="min-h-screen text-white relative overflow-hidden">
      {/* Gradient background */}
      <div
        className="fixed inset-0 -z-20"
        style={{
          background: 'linear-gradient(135deg, #0d0f12 0%, #1a1d24 100%)',
        }}
      />

      {/* Animated gradient orbs */}
      <GradientOrbs mode={currentMode} />

      {/* Noise overlay */}
      <div className="noise-overlay" />

      {/* Header */}
      <header
        className="sticky top-0 z-40 px-6 py-4"
        style={{
          background: 'linear-gradient(180deg, rgba(13, 15, 18, 0.95) 0%, rgba(13, 15, 18, 0.8) 100%)',
          backdropFilter: 'blur(12px)',
          borderBottom: '1px solid rgba(42, 47, 56, 0.5)',
        }}
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <motion.div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{
                background: currentMode === 'HOLD'
                  ? 'linear-gradient(135deg, #0ea5e9 0%, #14b8a6 100%)'
                  : 'linear-gradient(135deg, #f97316 0%, #fb923c 100%)',
                boxShadow: currentMode === 'HOLD'
                  ? '0 4px 16px rgba(14, 165, 233, 0.3)'
                  : '0 4px 16px rgba(249, 115, 22, 0.3)',
              }}
              animate={{ scale: isRunning ? [1, 1.05, 1] : 1 }}
              transition={{ duration: 2, repeat: isRunning ? Infinity : 0 }}
            >
              <Activity size={20} className="text-white" />
            </motion.div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">SteadyScript</h1>
              <p className="text-xs text-gray-400">Hand Stability Training</p>
            </div>
          </div>

        </div>
      </header>

      {/* Main content - Grid Layout */}
      <main className="max-w-7xl mx-auto px-6 py-6">
        {/* Top Row - Camera (60%) + Session Performance (40%) */}
        <motion.div
          className="grid grid-cols-1 lg:grid-cols-[1.4fr_1fr] gap-5"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          {/* Camera Section - wider */}
          <div className="h-full">
            <CameraSection
              frameData={frameData}
              isConnected={isConnected}
              markerDetected={metrics?.marker_detected ?? false}
              currentMode={currentMode}
              onModeChange={handleModeChange}
              onCanvasClick={handleCanvasClick}
              sessionState={sessionState}
              sessionResults={localSessionResults}
              onDismissResults={handleDismissResults}
              onStart={startSession}
              onStop={stopSession}
              onHelpClick={() => setIsHelpOpen(true)}
              canvasRef={canvasRef}
            />
          </div>

          {/* Session Performance - narrower but fills height */}
          <div className="h-full">
            <SessionPerformance
              score={metrics?.score ?? 0}
              status={getStatus()}
              mode={currentMode}
              sessionState={sessionState}
              timeRemaining={metrics?.time_remaining ?? 0}
              totalTime={(metrics?.elapsed ?? 0) + (metrics?.time_remaining ?? 0) || 30}
              jitter={metrics?.jitter ?? 0}
              p95Jitter={metrics?.p95_jitter ?? 0}
              lateralJitter={metrics?.lateral_jitter ?? 0}
              p95LateralJitter={metrics?.p95_lateral_jitter ?? 0}
              bpm={metrics?.bpm ?? 60}
              onBpmChange={changeBPM}
              className="h-full"
            />
          </div>
        </motion.div>

        {/* Bottom Row - Profile Summary (40%) + Session History (60%) */}
        <motion.div
          className="grid grid-cols-1 lg:grid-cols-[1.4fr_1fr] gap-5 mt-5"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          {/* Profile Summary - left side */}
          <div>
            <ProfileSummary
              stats={{
                currentStreak: profileStats.currentStreak,
                totalSessions: profileStats.totalSessions,
                avgJitterScore: profileStats.avgJitterScore,
                avgTremorScore: profileStats.avgTremorScore,
                bestJitterScore: profileStats.bestJitterScore,
                bestTremorScore: profileStats.bestTremorScore,
              }}
              sessions={sessions}
            />
          </div>

          {/* Session History - right side, wider */}
          <div>
            <SessionHistory />
          </div>
        </motion.div>

        {/* Quick tips - floating at bottom */}
        <motion.div
          className="mt-6"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card variant="glass" className="text-xs text-gray-400">
            <CardContent className="py-3">
              <div className="flex items-center justify-center gap-6 flex-wrap">
                <div className="flex items-center gap-2">
                  <kbd className="px-2 py-0.5 rounded bg-gray-700/50 text-gray-300 font-mono text-[10px]">1</kbd>
                  <span>HOLD mode</span>
                </div>
                <div className="flex items-center gap-2">
                  <kbd className="px-2 py-0.5 rounded bg-gray-700/50 text-gray-300 font-mono text-[10px]">2</kbd>
                  <span>FOLLOW mode</span>
                </div>
                <div className="flex items-center gap-2">
                  <kbd className="px-2 py-0.5 rounded bg-gray-700/50 text-gray-300 font-mono text-[10px]">Space</kbd>
                  <span>Start/Stop</span>
                </div>
                {currentMode === 'FOLLOW' && (
                  <div className="flex items-center gap-2">
                    <kbd className="px-2 py-0.5 rounded bg-gray-700/50 text-gray-300 font-mono text-[10px]">↑↓</kbd>
                    <span>Adjust BPM</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </main>

      {/* Help Modal */}
      <HelpModal isOpen={isHelpOpen} onClose={() => setIsHelpOpen(false)} />
    </div>
  );
}
