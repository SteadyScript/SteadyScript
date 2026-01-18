function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="border-b border-gray-800 px-6 py-4">
        <h1 className="text-2xl font-bold">Tremor Tracker</h1>
        <p className="text-gray-400 text-sm">Real-time hand stability tracking</p>
      </header>

      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="aspect-video bg-gray-700 rounded-lg flex items-center justify-center">
                <p className="text-gray-400">Camera feed will appear here</p>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="bg-gray-800 rounded-lg p-4">
              <h2 className="text-lg font-semibold mb-4">Stability Score</h2>
              <div className="flex items-center justify-center">
                <div className="w-32 h-32 rounded-full border-8 border-gray-700 flex items-center justify-center">
                  <span className="text-3xl font-bold">--</span>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <h2 className="text-lg font-semibold mb-4">Mode</h2>
              <div className="grid grid-cols-2 gap-2">
                <button className="px-4 py-2 bg-blue-600 rounded-lg text-sm font-medium">
                  Practice
                </button>
                <button className="px-4 py-2 bg-gray-700 rounded-lg text-sm font-medium">
                  Learn
                </button>
                <button className="px-4 py-2 bg-gray-700 rounded-lg text-sm font-medium">
                  Review
                </button>
                <button className="px-4 py-2 bg-gray-700 rounded-lg text-sm font-medium">
                  Trace
                </button>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <h2 className="text-lg font-semibold mb-2">Tips</h2>
              <p className="text-gray-400 text-sm">
                Position your pen with the colored tip facing the camera. Keep your hand steady and move slowly between targets.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
