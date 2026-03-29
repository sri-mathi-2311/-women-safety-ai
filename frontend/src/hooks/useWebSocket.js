import { useState, useEffect, useRef } from 'react'

function useWebSocket(url) {
  const [connected, setConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState(null)
  const ws = useRef(null)
  const reconnectTimer = useRef(null)
  const heartbeatTimer = useRef(null)
  const isMounted = useRef(true)

  useEffect(() => {
    isMounted.current = true

    const startHeartbeat = () => {
      clearInterval(heartbeatTimer.current)
      heartbeatTimer.current = setInterval(() => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
          ws.current.send(JSON.stringify({ type: 'ping' }))
        }
      }, 30000)
    }

    const connect = () => {
      if (!isMounted.current) return
      
      // Clear existing reconnect timer if we are manually connecting
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current)
      }

      console.log(`📡 Connecting to WebSocket at ${url}...`)
      try {
        ws.current = new WebSocket(url)

        ws.current.onopen = () => {
          console.log('✅ WebSocket connected')
          setConnected(true)
          startHeartbeat()
        }

        ws.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            // console.log('📩 WebSocket message:', data)
            if (data.type !== 'pong') {
              setLastMessage(data)
            }
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        ws.current.onerror = (error) => {
          // console.error('❌ WebSocket error:', error)
          // Avoid flooding logs with ECONNRESET during dev reloads
        }

        ws.current.onclose = (event) => {
          if (isMounted.current) {
            console.log(`❌ WebSocket closed (code: ${event.code}, reason: ${event.reason || 'none'}). Reconnecting...`)
            setConnected(false)
            clearInterval(heartbeatTimer.current)
            
            reconnectTimer.current = setTimeout(() => {
              connect()
            }, 3000)
          }
        }
      } catch (err) {
        console.error('WebSocket creation failed:', err)
        reconnectTimer.current = setTimeout(connect, 5000)
      }
    }

    connect()

    return () => {
      isMounted.current = false
      clearTimeout(reconnectTimer.current)
      clearInterval(heartbeatTimer.current)
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [url])

  const sendMessage = (message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message))
    }
  }

  return { connected, lastMessage, sendMessage }
}

export default useWebSocket