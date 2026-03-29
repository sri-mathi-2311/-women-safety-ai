import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

function Statistics({ statistics, uptime }) {
  const formatUptime = (seconds) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  const COLORS = {
    LOW: '#4ade80',
    MEDIUM: '#fbbf24',
    HIGH: '#fb923c',
    CRITICAL: '#ef4444'
  }

  const pieData = statistics ? [
    { name: 'Low', value: statistics.today.distribution.LOW, color: COLORS.LOW },
    { name: 'Medium', value: statistics.today.distribution.MEDIUM, color: COLORS.MEDIUM },
    { name: 'High', value: statistics.today.distribution.HIGH, color: COLORS.HIGH },
    { name: 'Critical', value: statistics.today.distribution.CRITICAL, color: COLORS.CRITICAL },
  ].filter(item => item.value > 0) : []

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-purple-500/20 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-purple-500/20">
        <h2 className="text-xl font-bold text-white">📊 Statistics</h2>
      </div>

      <div className="p-6 space-y-6">
        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-lg p-4 border border-purple-500/20">
            <div className="text-sm text-purple-300">Today's Alerts</div>
            <div className="text-3xl font-bold text-white mt-1">
              {statistics?.today.total || 0}
            </div>
          </div>

          <div className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-lg p-4 border border-blue-500/20">
            <div className="text-sm text-blue-300">This Week</div>
            <div className="text-3xl font-bold text-white mt-1">
              {statistics?.week.total || 0}
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 rounded-lg p-4 border border-green-500/20 col-span-2">
            <div className="text-sm text-green-300">System Uptime</div>
            <div className="text-2xl font-bold text-white mt-1">
              {formatUptime(uptime || 0)}
            </div>
          </div>
        </div>

        {/* Threat Distribution */}
        {pieData.length > 0 && (
          <div>
            <h3 className="text-sm font-bold text-purple-300 mb-3">Threat Distribution (Today)</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e293b', 
                    border: '1px solid #a78bfa',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {!statistics && (
          <div className="text-center py-8">
            <div className="text-4xl mb-2 opacity-20">📊</div>
            <p className="text-slate-400 text-sm">Loading statistics...</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Statistics