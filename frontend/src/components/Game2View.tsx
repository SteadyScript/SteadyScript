import { useEffect, useRef, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Activity, HelpCircle, ChevronUp, ChevronDown, Music } from 'lucide-react';
import { useGame2WebSocket } from '../hooks/useGame2WebSocket';
import { useSessionHistory } from '../hooks/useSessionHistory';
import { useProfileStats } from '../hooks/useProfileStats';
import { CameraSection } from './camera/CameraSection';
import { SessionPerformance } from './metrics/SessionPerformance';
import { ProfileSummary } from './metrics/ProfileSummary';
import { SessionHistory } from './history/SessionHistory';
import { GradientOrbs } from './ui/GradientOrbs';
import { Card, CardContent } from './ui/Card';

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
  const [localSessionResults, setLocalSessionResults] = useState<Record<string, unknown> | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [currentMode, setCurrentMode] = useState<'HOLD' | 'FOLLOW'>('HOLD');

  // Update local session results when received
  useEffect(() => {
    if (sessionResults) {
      setLocalSessionResults(sessionResults);
      refetchSessions();
    }
  }, [sessionResults, refetchSessions]);

  // Handle mode change
  const handleModeChange = useCallback(
    (mode: 'HOLD' | 'FOLLOW') => {
      setCurrentMode(mode);
      switchMode(mode);
      setLocalSessionResults(null);
    },
    [switchMode]
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
    setLocalSessionResults(null);
    handleKeyboard(' ');
  }, [handleKeyboard]);

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
          setLocalSessionResults(null);
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

          <div className="flex items-center gap-4">
            {/* BPM controls for FOLLOW mode */}
            {currentMode === 'FOLLOW' && (
              <div className="flex items-center gap-2">
                <Music size={14} className="text-orange-400" />
                <motion.button
                  onClick={() => changeBPM(-5)}
                  className="p-1.5 rounded-lg bg-gray-800/80 hover:bg-gray-700 transition-colors"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <ChevronDown size={14} />
                </motion.button>
                <span className="w-10 text-center text-sm font-bold text-orange-400">
                  {metrics?.bpm ?? 60}
                </span>
                <motion.button
                  onClick={() => changeBPM(5)}
                  className="p-1.5 rounded-lg bg-gray-800/80 hover:bg-gray-700 transition-colors"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <ChevronUp size={14} />
                </motion.button>
                <span className="text-xs text-gray-500">BPM</span>
              </div>
            )}

            {/* Help button */}
            <button className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-gray-800/50">
              <HelpCircle size={20} />
            </button>
          </div>
        </div>
      </header>

      {/* Main content - Bento Grid */}
      <main className="max-w-7xl mx-auto px-6 py-6">
        <motion.div
          className="grid grid-cols-1 lg:grid-cols-2 gap-5"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          {/* Top Left - Camera Section */}
          <div className="lg:row-span-1">
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
              canvasRef={canvasRef}
            />
          </div>

          {/* Top Right - Session Performance */}
          <div className="lg:row-span-1">
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
            />
          </div>

          {/* Bottom Left - Session History */}
          <div className="lg:row-span-1">
            <SessionHistory />
          </div>

          {/* Bottom Right - Profile Summary */}
          <div className="lg:row-span-1">
            <ProfileSummary
              stats={{
                currentStreak: profileStats.currentStreak,
                totalSessions: profileStats.totalSessions,
                avgJitterScore: profileStats.avgJitterScore,
                avgTremorScore: profileStats.avgTremorScore,
                bestJitterScore: profileStats.bestJitterScore,
                bestTremorScore: profileStats.bestTremorScore,
              }}
            />
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
                {currentMode === 'HOLD' && (
                  <span className="text-gray-500">Click camera to calibrate target</span>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </main>
    </div>
  );
}
