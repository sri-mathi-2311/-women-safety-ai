import { useState } from 'react'
import { startDetection, stopDetection, testAlert } from '../utils/api'

function Controls({ running, onStatusChange }) {
  const [loading, setLoading] = useState(false)
  const [testLoading, setTestLoading] = useState(false)

  const handleStart = async () => {
    setLoading(true)
    try {
      await startDetection()
      onStatusChange()
    } catch (error) {
      console.error('Failed to start detection:', error)
      alert('Failed to start detection system')
    } finally {
      setLoading(false)
    }
  }

  const handleStop = async () => {
    setLoading(true)
    try {
      await stopDetection()
      onStatusChange()
    } catch (error) {
      console.error('Failed to stop detection:', error)
      alert('Failed to stop detection system')
    } finally {
      setLoading(false)
    }
  }

  const handleTestAlert = async () => {
    setTestLoading(true)
    try {
      const result = await testAlert()
      alert(`✅ Test alert sent!\nSMS Status: ${result.sms_status}`)
    } catch (error) {
      console.error('Test alert failed:', error)
      alert('❌ Test alert failed. Check backend logs.')
    } finally {
      setTestLoading(false)
    }
  }

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-purple-500/20 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-purple-500/20">
        <h2 className="text-xl font-bold text-white">⚙️ System Controls</h2>
      </div>

      <div className="p-6">
        <div className="flex gap-4">
          {!running ? (
            <button
              onClick={handleStart}
              disabled={loading}
              className="flex-1 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-4 px-6 rounded-lg transition-all transform hover:scale-105 active:scale-95 shadow-lg shadow-green-500/50"
            >
              {loading ? '⏳ Starting...' : '▶️ Start Detection'}
            </button>
          ) : (
            <button
              onClick={handleStop}
              disabled={loading}
              className="flex-1 bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-4 px-6 rounded-lg transition-all transform hover:scale-105 active:scale-95 shadow-lg shadow-red-500/50"
            >
              {loading ? '⏳ Stopping...' : '⏸️ Stop Detection'}
            </button>
          )}

          <button
            className="bg-slate-700 hover:bg-slate-600 text-white font-bold py-4 px-6 rounded-lg transition-all"
            title="Settings"
          >
            ⚙️
          </button>

          <button
            onClick={handleTestAlert}
            disabled={testLoading}
            className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-4 px-6 rounded-lg transition-all"
            title="Test SMS Alert"
          >
            {testLoading ? '⏳ Sending...' : '📱 Test Alert'}
          </button>
        </div>

        {/* System Info */}
        <div className="mt-6 grid grid-cols-3 gap-4">
          <div className="bg-slate-900/50 rounded-lg p-4 border border-purple-500/20">
            <div className="text-xs text-purple-300">Detection Model</div>
            <div className="text-sm font-bold text-white mt-1">YOLOv8n</div>
          </div>

          <div className="bg-slate-900/50 rounded-lg p-4 border border-purple-500/20">
            <div className="text-xs text-purple-300">Pose Analysis</div>
            <div className="text-sm font-bold text-white mt-1">MediaPipe</div>
          </div>

          <div className="bg-slate-900/50 rounded-lg p-4 border border-purple-500/20">
            <div className="text-xs text-purple-300">AI Analyzer</div>
            <div className="text-sm font-bold text-white mt-1">Gemini 2.0</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Controls