import { API_BASE_URL } from '../utils/api'

function LiveFeed({ threatLevel, confidence, personsDetected, running }) {
  const getThreatColor = (level) => {
    const colors = {
      LOW: 'text-green-400 bg-green-500/20 border-green-500/50',
      MEDIUM: 'text-yellow-400 bg-yellow-500/20 border-yellow-500/50',
      HIGH: 'text-orange-400 bg-orange-500/20 border-orange-500/50',
      CRITICAL: 'text-red-400 bg-red-500/20 border-red-500/50'
    }
    return colors[level] || colors.LOW
  }

  const getThreatEmoji = (level) => {
    const emojis = {
      LOW: '✅',
      MEDIUM: '⚠️',
      HIGH: '🚨',
      CRITICAL: '🔴'
    }
    return emojis[level] || '✅'
  }

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-purple-500/20 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-purple-500/20">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          📹 Live Camera Feed
          {running && (
            <span className="flex items-center gap-1 text-sm font-normal text-green-400">
              <span className="w-2 h-2 bg-green-400 rounded-full pulse-glow"></span>
              LIVE
            </span>
          )}
        </h2>
      </div>

      {/* Video Feed */}
      <div className="relative aspect-video bg-slate-900">
        {running ? (
          <img 
            src={`${API_BASE_URL}/api/video/feed`}
            alt="Live Camera Feed"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-center">
              <div className="w-20 h-20 mx-auto mb-4 bg-slate-700 rounded-full flex items-center justify-center">
                <span className="text-4xl opacity-50">📹</span>
              </div>
              <p className="text-slate-400">Camera offline</p>
              <p className="text-sm text-slate-500 mt-1">Start detection to view feed</p>
            </div>
          </div>
        )}

        {/* Live Overlay - Only show on hover to not block video overlays */}
        {running && (
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-slate-900/90 to-transparent p-6 opacity-0 hover:opacity-100 transition-opacity">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`px-4 py-2 rounded-lg border ${getThreatColor(threatLevel)}`}>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{getThreatEmoji(threatLevel)}</span>
                    <div>
                      <div className="text-xs opacity-75">Threat Level</div>
                      <div className="text-lg font-bold">{threatLevel}</div>
                    </div>
                  </div>
                </div>

                <div className="px-4 py-2 rounded-lg border border-purple-500/30 bg-purple-500/10">
                  <div className="text-xs text-purple-300">Confidence</div>
                  <div className="text-lg font-bold text-purple-200">{confidence.toFixed(1)}%</div>
                </div>

                <div className="px-4 py-2 rounded-lg border border-blue-500/30 bg-blue-500/10">
                  <div className="text-xs text-blue-300">Persons</div>
                  <div className="text-lg font-bold text-blue-200">{personsDetected}</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default LiveFeed
