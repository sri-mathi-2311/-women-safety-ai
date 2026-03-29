function AlertPanel({ alerts }) {
  const getThreatBadge = (level) => {
    const styles = {
      LOW: 'bg-green-500/20 text-green-400 border-green-500/50',
      MEDIUM: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
      HIGH: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
      CRITICAL: 'bg-red-500/20 text-red-400 border-red-500/50'
    }
    return styles[level] || styles.LOW
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-purple-500/20 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-purple-500/20">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          🔔 Recent Alerts
          <span className="text-sm font-normal text-purple-300">
            ({alerts.length} total)
          </span>
        </h2>
      </div>

      {/* Alerts List */}
      <div className="max-h-96 overflow-y-auto">
        {alerts.length === 0 ? (
          <div className="px-6 py-12 text-center">
            <div className="text-6xl mb-4 opacity-20">🔕</div>
            <p className="text-slate-400">No alerts yet</p>
            <p className="text-sm text-slate-500 mt-1">Alerts will appear here when threats are detected</p>
          </div>
        ) : (
          <div className="divide-y divide-purple-500/10">
            {alerts.map((alert, index) => (
              <div 
                key={alert.id || index}
                className="px-6 py-4 hover:bg-purple-500/5 transition-colors"
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-4 flex-1">
                    <div className="text-sm text-purple-400 font-mono min-w-[80px]">
                      {formatTime(alert.timestamp)}
                    </div>
                    
                    <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getThreatBadge(alert.threat_level)}`}>
                      {alert.threat_level}
                    </span>

                    <p className="text-white flex-1">{alert.description}</p>

                    <div className="text-sm text-purple-300">
                      {(alert.confidence ?? 0).toFixed(0)}%
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {alert.sms_sent ? (
                      <span className="text-green-400 text-sm flex items-center gap-1">
                        ✅ Sent
                      </span>
                    ) : (
                      <span className="text-slate-500 text-sm flex items-center gap-1">
                        ⏭️ Skipped
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default AlertPanel