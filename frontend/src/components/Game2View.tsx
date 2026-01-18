import { useEffect, useRef, useState } from 'react';
import { useGame2WebSocket } from '../hooks/useGame2WebSocket';

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

  const [localSessionResults, setLocalSessionResults] = useState<any>(null);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [currentMode, setCurrentMode] = useState<'HOLD' | 'FOLLOW'>('HOLD');

  // Draw frame on canvas
  useEffect(() => {
    if (!frameData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    img.onload = () => {
      // Set canvas size to match image
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
    };
    img.src = `data:image/jpeg;base64,${frameData}`;
  }, [frameData]);

  // Handle canvas click (for calibration)
  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    const x = Math.floor((e.clientX - rect.left) * scaleX);
    const y = Math.floor((e.clientY - rect.top) * scaleY);
    
    if (currentMode === 'HOLD') {
      handleCalibrationClick(x, y);
    }
  };

  // Update local session results when received
  useEffect(() => {
    if (sessionResults) {
      setLocalSessionResults(sessionResults);
    }
  }, [sessionResults]);

  // Clear session results when starting new session
  useEffect(() => {
    if (metrics?.session_state === 'IDLE' && localSessionResults) {
      setLocalSessionResults(null);
    }
  }, [metrics?.session_state, localSessionResults]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === '1') {
        setCurrentMode('HOLD');
        switchMode('HOLD');
        setLocalSessionResults(null);
      } else if (e.key === '2') {
        setCurrentMode('FOLLOW');
        switchMode('FOLLOW');
        setLocalSessionResults(null);
      } else if (e.key === ' ') {
        e.preventDefault();
        if (metrics?.session_state === 'IDLE') {
          setLocalSessionResults(null);
          startSession();
        } else if (metrics?.session_state === 'RUNNING') {
          stopSession();
        } else if (metrics?.session_state === 'COMPLETE') {
          setLocalSessionResults(null);
          handleKeyboard(' ');
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
  }, [metrics, switchMode, startSession, stopSession, changeBPM, handleKeyboard]);

  const stabilityColor = metrics?.stability_level === 'stable' 
    ? 'text-green-500' 
    : metrics?.stability_level === 'warning' 
    ? 'text-yellow-500' 
    : 'text-red-500';

  const feedbackColor = metrics?.feedback_status === 'good'
    ? 'text-green-500'
    : metrics?.feedback_status === 'warning'
    ? 'text-yellow-500'
    : 'text-red-500';

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">SteadyScript Game2</h1>
            <p className="text-gray-400 text-sm">HOLD & FOLLOW Training Modes</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
              <span className="text-sm text-gray-400">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setCurrentMode('HOLD');
                  switchMode('HOLD');
                }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  currentMode === 'HOLD'
                    ? 'bg-cyan-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                Mode 1: HOLD
              </button>
              <button
                onClick={() => {
                  setCurrentMode('FOLLOW');
                  switchMode('FOLLOW');
                }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  currentMode === 'FOLLOW'
                    ? 'bg-orange-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                Mode 2: FOLLOW
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="relative bg-gray-700 rounded-lg overflow-hidden">
                <canvas
                  ref={canvasRef}
                  onClick={handleCanvasClick}
                  className="w-full h-auto cursor-crosshair"
                />
                
                {!metrics?.marker_detected && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                    <p className="text-yellow-400 text-lg font-medium">
                      Marker not detected - Position colored marker in view
                    </p>
                  </div>
                )}

                {localSessionResults && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/80">
                    <div className="bg-gray-800 rounded-lg p-6 max-w-md">
                      <h2 className="text-2xl font-bold mb-4 text-cyan-400">
                        {currentMode === 'HOLD' ? 'HOLD Results' : 'FOLLOW Results'}
                      </h2>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Tremor Score:</span>
                          <span className="font-bold text-white">
                            {localSessionResults.tremor_score?.toFixed(1) ?? '--'}/100
                          </span>
                        </div>
                        {currentMode === 'HOLD' ? (
                          <>
                            <div className="flex justify-between">
                              <span className="text-gray-400">Avg Jitter:</span>
                              <span>{localSessionResults.avg_jitter?.toFixed(1) ?? '--'} px</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-400">P95 Jitter:</span>
                              <span>{localSessionResults.p95_jitter?.toFixed(1) ?? '--'} px</span>
                            </div>
                          </>
                        ) : (
                          <>
                            <div className="flex justify-between">
                              <span className="text-gray-400">Avg Lateral Jitter:</span>
                              <span>{localSessionResults.avg_lateral_jitter?.toFixed(1) ?? '--'} px</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-400">P95 Lateral Jitter:</span>
                              <span>{localSessionResults.p95_lateral_jitter?.toFixed(1) ?? '--'} px</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-400">Beats:</span>
                              <span>{localSessionResults.beats_total ?? '--'}</span>
                            </div>
                          </>
                        )}
                      </div>
                      <button
                        onClick={() => {
                          setLocalSessionResults(null);
                          handleKeyboard(' ');
                        }}
                        className="mt-4 w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors"
                      >
                        Continue
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="space-y-6">
            {/* Metrics Panel */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h2 className="text-lg font-semibold mb-4">
                {currentMode === 'HOLD' ? 'Stability Score' : 'Movement Quality'}
              </h2>
              <div className="flex flex-col items-center">
                <div className={`w-32 h-32 rounded-full border-8 ${
                  currentMode === 'HOLD'
                    ? stabilityColor.replace('text-', 'border-')
                    : feedbackColor.replace('text-', 'border-')
                } flex items-center justify-center transition-colors`}>
                  <span className={`text-3xl font-bold ${
                    currentMode === 'HOLD' ? stabilityColor : feedbackColor
                  }`}>
                    {metrics?.score?.toFixed(0) ?? '--'}
                  </span>
                </div>
                <p className={`mt-2 text-sm font-medium capitalize ${
                  currentMode === 'HOLD' ? stabilityColor : feedbackColor
                }`}>
                  {currentMode === 'HOLD'
                    ? metrics?.stability_level ?? 'Unknown'
                    : metrics?.feedback_status ?? 'Unknown'}
                </p>
              </div>
            </div>

            {/* Session Controls */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h2 className="text-lg font-semibold mb-4">Session</h2>
              
              {metrics?.session_state === 'RUNNING' ? (
                <div className="space-y-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Elapsed:</span>
                    <span>{metrics.elapsed.toFixed(1)}s</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Remaining:</span>
                    <span>{metrics.time_remaining.toFixed(1)}s</span>
                  </div>
                  {currentMode === 'FOLLOW' && (
                    <>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">BPM:</span>
                        <span>{metrics.bpm ?? '--'}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Beats:</span>
                        <span>{metrics.beat_count ?? 0}</span>
                      </div>
                    </>
                  )}
                  <button
                    onClick={stopSession}
                    className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-sm font-medium transition-colors"
                  >
                    Stop Session
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {currentMode === 'FOLLOW' && (
                    <div className="space-y-2">
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-400">BPM:</span>
                        <span className="font-medium">{metrics?.bpm ?? 60}</span>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => changeBPM(-5)}
                          className="flex-1 px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
                        >
                          -5
                        </button>
                        <button
                          onClick={() => changeBPM(5)}
                          className="flex-1 px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
                        >
                          +5
                        </button>
                      </div>
                    </div>
                  )}
                  <button
                    onClick={startSession}
                    disabled={!metrics?.marker_detected}
                    className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-colors"
                  >
                    Start Session
                  </button>
                </div>
              )}
            </div>

            {/* Real-time Metrics */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h2 className="text-lg font-semibold mb-4">Metrics</h2>
              <div className="space-y-2 text-sm">
                {currentMode === 'HOLD' ? (
                  <>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Jitter:</span>
                      <span>{metrics?.jitter?.toFixed(1) ?? '--'} px</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">P95 Jitter:</span>
                      <span>{metrics?.p95_jitter?.toFixed(1) ?? '--'} px</span>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Lateral Jitter:</span>
                      <span>{metrics?.lateral_jitter?.toFixed(1) ?? '--'} px</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">P95 Lateral:</span>
                      <span>{metrics?.p95_lateral_jitter?.toFixed(1) ?? '--'} px</span>
                    </div>
                  </>
                )}
                {metrics?.position && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Position:</span>
                    <span>({metrics.position.x}, {metrics.position.y})</span>
                  </div>
                )}
              </div>
            </div>

            {/* Controls Help */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h2 className="text-lg font-semibold mb-2">Controls</h2>
              <ul className="text-gray-400 text-sm space-y-1">
                <li>• [1] Switch to HOLD mode</li>
                <li>• [2] Switch to FOLLOW mode</li>
                <li>• [SPACE] Start/Stop session</li>
                {currentMode === 'FOLLOW' && (
                  <>
                    <li>• [↑] Increase BPM</li>
                    <li>• [↓] Decrease BPM</li>
                  </>
                )}
                {currentMode === 'HOLD' && (
                  <li>• Click canvas to calibrate circle</li>
                )}
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
