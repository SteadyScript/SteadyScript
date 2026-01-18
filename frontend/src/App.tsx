import { useState } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { Game2View } from './components/Game2View';

const API_URL = 'http://localhost:8000';

function App() {
  const [view, setView] = useState<'game1' | 'game2'>('game2');
  const { isConnected, trackingData, startSession, stopSession } = useWebSocket();

  const stabilityColor = trackingData?.stability.level === 'stable' 
    ? 'text-green-500' 
    : trackingData?.stability.level === 'warning' 
    ? 'text-yellow-500' 
    : 'text-red-500';

  const stabilityBorderColor = trackingData?.stability.level === 'stable' 
    ? 'border-green-500' 
    : trackingData?.stability.level === 'warning' 
    ? 'border-yellow-500' 
    : 'border-red-500';

  if (view === 'game2') {
    return <Game2View />;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">SteadyScript</h1>
            <p className="text-gray-400 text-sm">Real-time hand stability tracking</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex gap-2">
              <button
                onClick={() => setView('game1')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  view === 'game1'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                Game 1
              </button>
              <button
                onClick={() => setView('game2')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  view === 'game2'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                Game 2
              </button>
            </div>
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
              <span className="text-sm text-gray-400">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="relative aspect-video bg-gray-700 rounded-lg overflow-hidden">
                <img
                  src={`${API_URL}/video_feed`}
                  alt="Camera Feed"
                  className="w-full h-full object-contain"
                />
                
                {!trackingData?.marker_detected && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                    <p className="text-yellow-400 text-lg font-medium">
                      Marker not detected - Position colored marker in view
                    </p>
                  </div>
                )}
              </div>
              
              <div className="mt-4 flex items-center justify-between">
                <div className="text-sm text-gray-400">
                  {trackingData?.position 
                    ? `Position: (${trackingData.position.x}, ${trackingData.position.y})`
                    : 'Position: --'
                  }
                </div>
                <div className="text-sm text-gray-400">
                  Jitter: {trackingData?.stability.jitter.toFixed(1) ?? '--'} px
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="bg-gray-800 rounded-lg p-4">
              <h2 className="text-lg font-semibold mb-4">Stability Score</h2>
              <div className="flex flex-col items-center">
                <div className={`w-32 h-32 rounded-full border-8 ${stabilityBorderColor} flex items-center justify-center transition-colors`}>
                  <span className={`text-3xl font-bold ${stabilityColor}`}>
                    {trackingData?.stability.score ?? '--'}
                  </span>
                </div>
                <p className={`mt-2 text-sm font-medium capitalize ${stabilityColor}`}>
                  {trackingData?.stability.level ?? 'Unknown'}
                </p>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <h2 className="text-lg font-semibold mb-4">Session</h2>
              
              {trackingData?.session.is_active ? (
                <div className="space-y-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Elapsed:</span>
                    <span>{trackingData.session.elapsed.toFixed(1)}s</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Remaining:</span>
                    <span>{trackingData.session.remaining.toFixed(1)}s</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Tremor Score:</span>
                    <span>{trackingData.session.tremor_score.toFixed(2)}</span>
                  </div>
                  <button
                    onClick={stopSession}
                    className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-sm font-medium transition-colors"
                  >
                    Stop Session
                  </button>
                </div>
              ) : (
                <button
                  onClick={startSession}
                  disabled={!trackingData?.marker_detected}
                  className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-colors"
                >
                  Start Session (10s)
                </button>
              )}
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <h2 className="text-lg font-semibold mb-2">Tips</h2>
              <ul className="text-gray-400 text-sm space-y-2">
                <li>• Position your pen with the colored marker facing the camera</li>
                <li>• Keep your hand steady and move slowly</li>
                <li>• Anchor your wrist on the table for stability</li>
                <li>• Green = stable, Yellow = warning, Red = unstable</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
