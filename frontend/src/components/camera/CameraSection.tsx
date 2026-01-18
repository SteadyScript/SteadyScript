import { useRef, useEffect, type RefObject } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, AlertTriangle, Square, Play, HelpCircle } from 'lucide-react';
import { ConnectionBadge } from '../layout/ConnectionBadge';

interface CameraSectionProps {
  frameData: string | null;
  isConnected: boolean;
  markerDetected: boolean;
  currentMode: 'HOLD' | 'FOLLOW';
  onModeChange: (mode: 'HOLD' | 'FOLLOW') => void;
  onCanvasClick: (x: number, y: number) => void;
  sessionState: 'IDLE' | 'RUNNING' | 'COMPLETE';
  sessionResults?: Record<string, unknown> | null;
  onDismissResults?: () => void;
  onStart?: () => void;
  onStop?: () => void;
  onHelpClick?: () => void;
  canvasRef?: RefObject<HTMLCanvasElement | null>;
  className?: string;
}

export function CameraSection({
  frameData,
  isConnected,
  markerDetected,
  currentMode,
  onModeChange,
  onCanvasClick,
  sessionState,
  sessionResults,
  onDismissResults,
  onStart,
  onStop,
  onHelpClick,
  canvasRef: externalCanvasRef,
  className = '',
}: CameraSectionProps) {
  const internalCanvasRef = useRef<HTMLCanvasElement>(null);
  const canvasRef = externalCanvasRef || internalCanvasRef;

  const isHold = currentMode === 'HOLD';
  const isRunning = sessionState === 'RUNNING';
  const accentColor = isHold ? '#0ea5e9' : '#f97316';

  // Draw frame on canvas
  useEffect(() => {
    if (!frameData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
    };
    img.src = `data:image/jpeg;base64,${frameData}`;
  }, [frameData, canvasRef]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const x = Math.floor((e.clientX - rect.left) * scaleX);
    const y = Math.floor((e.clientY - rect.top) * scaleY);

    onCanvasClick(x, y);
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Camera container with enhanced styling */}
      <div
        className={`relative rounded-2xl overflow-hidden border-2 transition-all duration-300 ${
          isRunning ? 'camera-vignette' : ''
        }`}
        style={{
          background: 'linear-gradient(145deg, #1e2128 0%, #191c22 100%)',
          borderColor: isRunning ? `${accentColor}50` : '#2a2f38',
          boxShadow: isRunning
            ? `0 0 40px ${accentColor}20, 0 4px 24px rgba(0, 0, 0, 0.4)`
            : '0 4px 24px rgba(0, 0, 0, 0.3)',
        }}
      >
        {/* Level/Mode indicator at top */}
        <div
          className="absolute top-0 left-0 right-0 z-20 flex items-center justify-between px-4 py-2"
          style={{
            background: 'linear-gradient(180deg, rgba(0,0,0,0.6) 0%, transparent 100%)',
          }}
        >
          <div className="flex items-center gap-2">
            <div
              className="w-2 h-2 rounded-full"
              style={{
                backgroundColor: accentColor,
                boxShadow: `0 0 8px ${accentColor}`,
              }}
            />
            <span
              className="text-xs font-semibold uppercase tracking-wider"
              style={{ color: accentColor }}
            >
              {currentMode} Mode
            </span>
          </div>
          <div className="flex items-center gap-2">
            {isRunning && (
              <motion.div
                className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
                style={{ backgroundColor: `${accentColor}20`, color: accentColor }}
                animate={{ opacity: [1, 0.6, 1] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-current" />
                RECORDING
              </motion.div>
            )}
            {/* Help button */}
            <button
              onClick={onHelpClick}
              className="p-1.5 rounded-lg bg-black/30 hover:bg-black/50 text-gray-400 hover:text-white transition-colors"
            >
              <HelpCircle size={16} />
            </button>
          </div>
        </div>

        {/* Corner accents */}
        <div className={`corner-accent ${!isHold ? 'corner-accent-follow' : ''}`}>
          {/* Canvas */}
          <canvas
            ref={canvasRef}
            onClick={handleCanvasClick}
            className="w-full h-auto cursor-crosshair"
            style={{ display: 'block' }}
          />
        </div>

        {/* Connection badge - bottom left of camera */}
        <div className="absolute bottom-3 left-3 z-10">
          <ConnectionBadge isConnected={isConnected} />
        </div>

        {/* No connection overlay */}
        <AnimatePresence>
          {!isConnected && (
            <motion.div
              className="absolute inset-0 flex items-center justify-center bg-black/70 backdrop-blur-sm z-20"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="text-center">
                <Camera size={48} className="mx-auto mb-3 text-gray-500" />
                <p className="text-gray-400 font-medium">Connecting to camera...</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Marker not detected overlay */}
        <AnimatePresence>
          {isConnected && !markerDetected && sessionState !== 'COMPLETE' && (
            <motion.div
              className="absolute inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm z-20"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="text-center px-6">
                <AlertTriangle size={40} className="mx-auto mb-3 text-amber-400" />
                <p className="text-amber-400 font-medium">Marker not detected</p>
                <p className="text-gray-400 text-sm mt-1">
                  Position a colored marker in the camera view
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Idle instructions overlay - shows when ready to start or after dismissing results */}
        <AnimatePresence>
          {isConnected && markerDetected && (sessionState === 'IDLE' || (sessionState === 'COMPLETE' && !sessionResults)) && (
            <motion.div
              className="absolute inset-0 flex items-center justify-center z-10"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div
                className="px-6 py-5 rounded-2xl text-center max-w-sm mx-4"
                style={{
                  background: 'rgba(0, 0, 0, 0.85)',
                  backdropFilter: 'blur(12px)',
                  border: `1px solid ${accentColor}40`,
                  boxShadow: `0 0 30px ${accentColor}20`,
                }}
              >
                <div
                  className="text-xs font-semibold uppercase tracking-wider mb-3"
                  style={{ color: accentColor }}
                >
                  {isHold ? 'Stability Test' : 'Movement Test'}
                </div>
                <p className="text-sm text-gray-200 leading-relaxed mb-4">
                  {isHold ? (
                    <>Hold the pen <strong>completely still</strong> for 10 seconds. Focus on keeping your hand steady.</>
                  ) : (
                    <>Move the pen <strong>back and forth</strong> following the metronome beat. Smooth, controlled movements.</>
                  )}
                </p>
                <div className="pt-3 border-t border-gray-700/50">
                  <p className="text-xs text-gray-400">
                    Press <kbd className="px-1.5 py-0.5 rounded bg-gray-700/80 text-gray-200 font-mono mx-1">Space</kbd> or click <span className="font-semibold" style={{ color: accentColor }}>START</span> to begin
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Session results overlay */}
        <AnimatePresence>
          {sessionResults && sessionState === 'COMPLETE' && (
            <motion.div
              className="absolute inset-0 flex items-center justify-center bg-black/80 backdrop-blur-sm z-20"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <motion.div
                className="rounded-2xl p-6 max-w-sm border"
                style={{
                  background: 'linear-gradient(145deg, #1e2128 0%, #191c22 100%)',
                  borderColor: `${accentColor}30`,
                  boxShadow: `0 0 40px ${accentColor}20`,
                }}
                initial={{ scale: 0.9, y: 20 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.9, y: 20 }}
              >
                <h2
                  className="text-xl font-bold mb-4"
                  style={{ color: accentColor }}
                >
                  {currentMode === 'HOLD' ? 'HOLD Results' : 'FOLLOW Results'}
                </h2>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Tremor Score:</span>
                    <span className="font-bold text-white">
                      {((sessionResults.tremor_score as number) ?? 0).toFixed(1)}/100
                    </span>
                  </div>
                  {currentMode === 'HOLD' ? (
                    <>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Avg Jitter:</span>
                        <span>{((sessionResults.avg_jitter as number) ?? 0).toFixed(1)} px</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">P95 Jitter:</span>
                        <span>{((sessionResults.p95_jitter as number) ?? 0).toFixed(1)} px</span>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Avg Lateral:</span>
                        <span>{((sessionResults.avg_lateral_jitter as number) ?? 0).toFixed(1)} px</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">P95 Lateral:</span>
                        <span>{((sessionResults.p95_lateral_jitter as number) ?? 0).toFixed(1)} px</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Beats:</span>
                        <span>{(sessionResults.beats_total as number) ?? '--'}</span>
                      </div>
                    </>
                  )}
                </div>
                <button
                  onClick={onDismissResults}
                  className="mt-4 w-full px-4 py-2 rounded-xl text-sm font-medium transition-all"
                  style={{
                    background: `linear-gradient(135deg, ${accentColor} 0%, ${isHold ? '#14b8a6' : '#fb923c'} 100%)`,
                    boxShadow: `0 4px 16px ${accentColor}40`,
                  }}
                >
                  Exit
                </button>
                <p className="text-xs text-gray-500 mt-2 text-center">
                  Press to return and start another session
                </p>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Mode buttons and session control */}
      <div className="flex gap-3">
        <motion.button
          onClick={() => onModeChange('HOLD')}
          disabled={sessionState === 'RUNNING'}
          className={`flex-1 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
            currentMode === 'HOLD'
              ? 'text-white'
              : 'bg-[#1e2128] text-gray-300 hover:bg-[#252932] border border-[#2a2f38]'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
          style={
            currentMode === 'HOLD'
              ? {
                  background: 'linear-gradient(135deg, #0ea5e9 0%, #14b8a6 100%)',
                  boxShadow: '0 4px 16px rgba(14, 165, 233, 0.3)',
                }
              : undefined
          }
          whileHover={sessionState !== 'RUNNING' ? { scale: 1.02 } : {}}
          whileTap={sessionState !== 'RUNNING' ? { scale: 0.98 } : {}}
        >
          Mode 1: HOLD
        </motion.button>
        <motion.button
          onClick={() => onModeChange('FOLLOW')}
          disabled={sessionState === 'RUNNING'}
          className={`flex-1 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
            currentMode === 'FOLLOW'
              ? 'text-white'
              : 'bg-[#1e2128] text-gray-300 hover:bg-[#252932] border border-[#2a2f38]'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
          style={
            currentMode === 'FOLLOW'
              ? {
                  background: 'linear-gradient(135deg, #f97316 0%, #fb923c 100%)',
                  boxShadow: '0 4px 16px rgba(249, 115, 22, 0.3)',
                }
              : undefined
          }
          whileHover={sessionState !== 'RUNNING' ? { scale: 1.02 } : {}}
          whileTap={sessionState !== 'RUNNING' ? { scale: 0.98 } : {}}
        >
          Mode 2: FOLLOW
        </motion.button>
      </div>

      {/* Start/Stop button */}
      <motion.button
        onClick={isRunning ? onStop : onStart}
        disabled={!markerDetected && !isRunning}
        className="w-full flex items-center justify-center gap-2 px-4 py-4 rounded-xl text-base font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        style={{
          background: isRunning
            ? 'linear-gradient(135deg, #f43f5e 0%, #fb7185 100%)'
            : `linear-gradient(135deg, ${accentColor} 0%, ${isHold ? '#14b8a6' : '#fb923c'} 100%)`,
          boxShadow: isRunning
            ? '0 4px 20px rgba(244, 63, 94, 0.4)'
            : `0 4px 20px ${accentColor}40`,
        }}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        {isRunning ? (
          <>
            <Square size={18} />
            STOP SESSION
          </>
        ) : (
          <>
            <Play size={18} />
            START SESSION
          </>
        )}
      </motion.button>
    </div>
  );
}
