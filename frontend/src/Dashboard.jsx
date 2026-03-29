import { useMemo, useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import useWebSocket from './hooks/useWebSocket'
import {
  getStatus,
  getAlerts,
  getStatistics,
  startDetection,
  stopDetection,
  testAlert,
  API_BASE_URL,
  getWebSocketUrl,
} from './utils/api'
import './Dashboard.css'

function parsePoseData(raw) {
  if (!raw) return {}
  try {
    if (typeof raw === 'object') return raw
    // First try standard JSON.parse
    try {
      return JSON.parse(raw)
    } catch {
      // Fallback for old single-quoted string format
      const normalized = String(raw).replaceAll("'", '"')
      return JSON.parse(normalized)
    }
  } catch {
    return {}
  }
}

function formatUptime(totalSeconds = 0) {
  const s = Number(totalSeconds || 0)
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
}

export default function Dashboard() {
  const [systemStatus, setSystemStatus] = useState({
    running: false,
    current_threat_level: 'LOW',
    current_confidence: 0,
    persons_detected: 0,
    uptime_seconds: 0,
    camera_has_frame: false,
    camera_open: false,
    last_error: null,
  })
  const [alerts, setAlerts] = useState([])
  const [statistics, setStatistics] = useState(null)
  const [reviewLabels, setReviewLabels] = useState({})
  const [busyAction, setBusyAction] = useState('')
  const [selectedSeverity, setSelectedSeverity] = useState('ALL')
  const [feedback, setFeedback] = useState('')
  const [feedKey, setFeedKey] = useState(0)
  const wsUrl = useMemo(() => getWebSocketUrl(), [])
  const { connected, lastMessage } = useWebSocket(wsUrl)

  useEffect(() => {
    const stored = localStorage.getItem('reviewLabels')
    if (stored) {
      try {
        setReviewLabels(JSON.parse(stored))
      } catch {
        setReviewLabels({})
      }
    }
  }, [])

  useEffect(() => {
    localStorage.setItem('reviewLabels', JSON.stringify(reviewLabels))
  }, [reviewLabels])

  useEffect(() => {
    fetchStatus()
    fetchAlerts()
    fetchStatistics()
  }, []) // Initial fetch on mount

  useEffect(() => {
    // Polling loop for status and statistics
    const pollInterval = setInterval(() => {
      fetchStatus()
      // Only fetch statistics if they haven't been loaded yet or we are disconnected
      // In a real app, you might want to poll statistics less frequently
      if (!statistics) {
        fetchStatistics()
      }
    }, connected ? 5000 : 2000)

    const fastInterval = setInterval(() => {
      setSystemStatus(prev => {
        if (!prev.running) return prev
        return {
          ...prev,
          uptime_seconds: prev.uptime_seconds + 1
        }
      })
    }, 1000)

    return () => {
      clearInterval(pollInterval)
      clearInterval(fastInterval)
    }
  }, [connected, !!statistics]) // Stable dependencies (boolean and boolean)

  useEffect(() => {
    if (!lastMessage) return
    if (lastMessage.type === 'alert') {
      setAlerts(prev => [lastMessage.data, ...prev].slice(0, 50))
      fetchStatistics()
    } else if (lastMessage.type === 'system') {
      if (lastMessage.data?.status === 'started') {
        setFeedKey(k => k + 1)
      }
      fetchStatus()
    } else if (lastMessage.type === 'status') {
      setSystemStatus(prev => ({ ...prev, ...lastMessage.data }))
    }
  }, [lastMessage])

  const setMessage = (text) => {
    setFeedback(text)
    setTimeout(() => setFeedback(''), 3000)
  }

  const fetchStatus = async () => {
    try {
      const data = await getStatus()
      // console.log('Fetched status:', data)
      if (data.running && !systemStatus.running) {
        setFeedKey(k => k + 1)
      }
      setSystemStatus(data)
    } catch (error) {
      console.error('Failed to fetch status:', error)
      // Optional: don't clear status on every fetch error to avoid flickering
    }
  }

  const fetchAlerts = async () => {
    try {
      // Use signal for cancellation if needed in future
      const data = await getAlerts(50)
      if (Array.isArray(data)) {
        setAlerts(data)
      }
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Failed to fetch alerts:', error)
      }
    }
  }

  const fetchStatistics = async () => {
    try {
      const data = await getStatistics()
      if (data) {
        setStatistics(data)
      }
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Failed to fetch statistics:', error)
      }
    }
  }

  const handleAction = async (name, actionFn) => {
    try {
      console.log(`Command triggered: ${name}`)
      setBusyAction(name)
      const result = await actionFn()
      console.log(`Command result for ${name}:`, result)
      
      if (name === 'Start Detection') {
        setFeedKey(k => k + 1)
      }
      await fetchStatus()
      await fetchAlerts()
      await fetchStatistics()
      
      let feedbackMsg = `${name} successful`
      if (name === 'Send Test Alert' && result?.sms_status) {
        feedbackMsg += ` (SMS: ${result.sms_status})`
      }
      setMessage(feedbackMsg)
    } catch (error) {
      console.error(`${name} failed:`, error)
      setMessage(`${name} failed: ${error.message || 'Unknown error'}`)
    } finally {
      setBusyAction('')
    }
  }

  const labelAlert = (alertId, label) => {
    setReviewLabels(prev => {
      const next = { ...prev }
      if (next[alertId] === label) {
        delete next[alertId]
      } else {
        next[alertId] = label
      }
      return next
    })
  }

  const enhancedAlerts = useMemo(
    () =>
      alerts.map((alert) => {
        const metadata = parsePoseData(alert.pose_data)
        return {
          ...alert,
          metadata,
          reviewerLabel: reviewLabels[alert.id] ?? '',
        }
      }),
    [alerts, reviewLabels]
  )

  const filteredAlerts = useMemo(() => {
    const today = new Date()
    const isToday = (dateString) => {
      const d = new Date(dateString)
      return d.getDate() === today.getDate() && 
             d.getMonth() === today.getMonth() && 
             d.getFullYear() === today.getFullYear()
    }

    let result = enhancedAlerts.filter(a => isToday(a.timestamp))
    if (selectedSeverity !== 'ALL') {
      result = result.filter(a => a.threat_level === selectedSeverity)
    }
    return result
  }, [enhancedAlerts, selectedSeverity])

  const exportIncidentReports = () => {
    const rows = [
      ['event_id', 'timestamp', 'threat_level', 'confidence', 'description', 'agent_report', 'male_emotion', 'female_emotion', 'reviewer_label']
    ]
    for (const alert of filteredAlerts) {
      rows.push([
        String(alert.id),
        new Date(alert.timestamp).toLocaleString().replace(/,/g, ''),
        alert.threat_level || '',
        Number(alert.confidence || 0).toFixed(1) + '%',
        `"${(alert.description || '').replace(/"/g, '""')}"`,
        `"${(alert.metadata?.agent_summarized_report || '').replace(/"/g, '""')}"`,
        `"${(alert.metadata?.mediapipe_skel_data?.aggressor_male?.facial_emotion || '').replace(/"/g, '""')}"`,
        `"${(alert.metadata?.mediapipe_skel_data?.victim_female?.facial_emotion || '').replace(/"/g, '""')}"`,
        alert.reviewerLabel || 'pending'
      ])
    }
    const csv = rows.map(r => r.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'incident_reports.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  const statusTone =
    systemStatus.current_threat_level === 'CRITICAL'
      ? 'critical'
      : systemStatus.current_threat_level === 'HIGH'
        ? 'high'
        : systemStatus.current_threat_level === 'MEDIUM'
          ? 'medium'
          : 'low'

  return (
    <div className="console-root">
      <div className="console-top-bar">
        <Link to="/" className="console-back-link">
          ← Website
        </Link>
      </div>
      <header className="console-header">
        <div className="brand-row">
          <div className="brand-mark" aria-hidden="true">
            <img src="/women_safety_logo.png" alt="Logo" style={{ width: '100%', height: '100%', objectFit: 'contain', borderRadius: '4px' }} />
          </div>
          <div>
            <h1>
              <span className="title-accent">Women Safety</span>
              Women Safety · Operations Console
            </h1>
            <p>Realtime threat monitoring, triage labeling, and calibration workflow — built for clarity under pressure.</p>
          </div>
        </div>
        <div className="header-chips">
          <span className={`chip ${connected ? 'online' : 'offline'}`}>
            WS {connected ? 'Connected' : 'Disconnected'}
          </span>
          <span className={`chip ${systemStatus.running ? 'online' : 'offline'}`}>
            System {systemStatus.running ? 'Running' : 'Stopped'}
          </span>
          {systemStatus.running ? (
            <span className={`chip ${systemStatus.camera_has_frame ? 'online' : 'offline'}`}>
              Video {systemStatus.camera_has_frame ? 'Live' : 'Starting…'}
            </span>
          ) : null}
          {systemStatus.last_update && (
            <span className="chip status-update">
              Updated {new Date(systemStatus.last_update).toLocaleTimeString()}
            </span>
          )}
        </div>
      </header>

      {systemStatus.last_error && !systemStatus.running ? (
        <p className="console-start-hint" role="status">
          Last issue: {systemStatus.last_error}
        </p>
      ) : null}

      <section className="grid-top">
        <article className="panel live-feed-panel" data-threat={statusTone}>
          <div className="panel-title-row">
            <h2>Live Surveillance Feed</h2>
            <span className={`severity-pill ${statusTone}`}>{systemStatus.current_threat_level}</span>
          </div>
          <div className="video-frame">
            {systemStatus.running ? (
              <img
                key={feedKey}
                src={`${API_BASE_URL}/api/video/feed?t=${feedKey}`}
                alt="Live feed"
              />
            ) : (
              <div className="video-placeholder">
                <div className="placeholder-content">
                  <div className="placeholder-icon">📹</div>
                  <p>Camera offline</p>
                  <span>Start detection to view feed</span>
                </div>
              </div>
            )}
          </div>
          <div className="metrics-row">
            <div className="metric">
              <span>Threat Confidence</span>
              <strong>{Number(systemStatus.current_confidence || 0).toFixed(1)}%</strong>
            </div>
            <div className="metric">
              <span>Persons Detected</span>
              <strong>{systemStatus.persons_detected || 0}</strong>
            </div>
            <div className="metric">
              <span>Uptime</span>
              <strong>{formatUptime(systemStatus.uptime_seconds)}</strong>
            </div>
          </div>
        </article>

        <article className="panel">
          <h2>Command Center</h2>
          <div className="actions-grid">
            <button
              className="btn btn-primary"
              disabled={busyAction === 'Start Detection' || systemStatus.running}
              onClick={() => handleAction('Start Detection', startDetection)}
            >
              Start Detection
            </button>
            <button
              className="btn btn-danger"
              disabled={busyAction === 'Stop Detection' || !systemStatus.running}
              onClick={() => handleAction('Stop Detection', stopDetection)}
            >
              Stop Detection
            </button>
            <button
              className="btn btn-secondary"
              disabled={busyAction === 'Send Test Alert'}
              onClick={() => handleAction('Send Test Alert', testAlert)}
            >
              Send Test Alert
            </button>
            <button className="btn btn-secondary" onClick={exportIncidentReports}>
              Export Incident Reports (CSV)
            </button>
          </div>
          {feedback && <p className="feedback">{feedback}</p>}

          <div className="quick-stats">
            <h3>Safety Snapshot</h3>
            <div className="quick-stats-grid">
              <div>
                <span>Today Alerts</span>
                <strong>{statistics?.today?.total ?? 0}</strong>
              </div>
              <div>
                <span>Week Alerts</span>
                <strong>{statistics?.week?.total ?? 0}</strong>
              </div>
              <div>
                <span>Critical Today</span>
                <strong>{statistics?.today?.distribution?.CRITICAL ?? 0}</strong>
              </div>
              <div>
                <span>High Today</span>
                <strong>{statistics?.today?.distribution?.HIGH ?? 0}</strong>
              </div>
            </div>
          </div>
        </article>
      </section>

      <section className="panel">
        <div className="panel-title-row">
          <h2>Reviewer Triage Queue</h2>
          <div className="filter-row">
            {['ALL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map((severity) => (
              <button
                key={severity}
                className={`filter-btn ${selectedSeverity === severity ? 'active' : ''}`}
                onClick={() => setSelectedSeverity(severity)}
              >
                {severity}
              </button>
            ))}
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Level</th>
                <th>Confidence</th>
                <th>Description</th>
                <th>Signals</th>
                <th>Reviewer Label</th>
              </tr>
            </thead>
            <tbody>
              {filteredAlerts.length === 0 ? (
                <tr>
                  <td colSpan="6" className="empty-state">
                    No events in this filter.
                  </td>
                </tr>
              ) : (
                filteredAlerts.map((alert) => (
                  <tr key={alert.id}>
                    <td>{new Date(alert.timestamp).toLocaleString()}</td>
                    <td>
                      <span className={`severity-pill ${String(alert.threat_level || '').toLowerCase()}`}>
                        {alert.threat_level}
                      </span>
                    </td>
                    <td>{Number(alert.confidence || 0).toFixed(1)}%</td>
                    <td>
                      <div>{alert.description}</div>
                      {alert.metadata.agent_summarized_report && (
                        <div style={{ marginTop: '8px', padding: '8px', background: 'rgba(253, 230, 138, 0.1)', borderLeft: '2px solid #fde68a', fontSize: '0.85em', color: '#fde68a' }}>
                          <strong style={{ display: 'block', marginBottom: '4px' }}>AI Incident Report:</strong> 
                          {alert.metadata.agent_summarized_report}
                          {alert.metadata.mediapipe_skel_data && (
                            <div style={{ marginTop: '6px', fontSize: '0.9em', color: '#d1d5db' }}>
                               <b>Emotions detected:</b> Male: <i>{alert.metadata.mediapipe_skel_data.aggressor_male?.facial_emotion}</i> | Female: <i>{alert.metadata.mediapipe_skel_data.victim_female?.facial_emotion}</i>
                            </div>
                          )}
                        </div>
                      )}
                    </td>
                    <td className="signals-cell">
                      {(alert.metadata.reason_codes || []).slice(0, 2).join(', ') || 'n/a'}
                    </td>
                    <td>
                      <div className="label-actions">
                        <button
                          className={`mini-btn ${alert.reviewerLabel === 'threat' ? 'selected-threat' : ''}`}
                          onClick={() => labelAlert(alert.id, 'threat')}
                        >
                          Threat
                        </button>
                        <button
                          className={`mini-btn ${alert.reviewerLabel === 'normal' ? 'selected-normal' : ''}`}
                          onClick={() => labelAlert(alert.id, 'normal')}
                        >
                          Normal
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      <footer className="console-footer">
        <p>Metadata-only workflow: no image persistence, only event evidence and reviewer labels.</p>
      </footer>
    </div>
  )
}
