function StatusBar({ connected, running }) {
  return (
    <div className="flex items-center gap-4">
      {/* WebSocket Status */}
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400 pulse-glow' : 'bg-red-400'}`}></div>
        <span className={`text-sm ${connected ? 'text-green-400' : 'text-red-400'}`}>
          {connected ? 'Connected' : 'Disconnected'}
        </span>
      </div>

      {/* Detection Status */}
      <div className={`px-4 py-2 rounded-lg font-bold text-sm ${
        running 
          ? 'bg-green-500/20 text-green-400 border border-green-500/50' 
          : 'bg-slate-700 text-slate-400 border border-slate-600'
      }`}>
        {running ? '🟢 ACTIVE' : '⚫ INACTIVE'}
      </div>
    </div>
  )
}

export default StatusBar