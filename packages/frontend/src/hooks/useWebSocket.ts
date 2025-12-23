import { useState, useEffect, useCallback, useRef } from 'react'
import type { WSStatusMessage } from '../types'

const WS_URL = import.meta.env.VITE_WS_URL || `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`

interface WebSocketState {
  status: string
  rowCount: number
  errorMessage?: string
  isConnected: boolean
}

export function useWebSocket(migrationId: number | null) {
  const [state, setState] = useState<WebSocketState>({
    status: 'pending',
    rowCount: 0,
    isConnected: false,
  })
  const wsRef = useRef<WebSocket | null>(null)

  const connect = useCallback(() => {
    if (!migrationId) return

    const ws = new WebSocket(`${WS_URL}/ws/migrations/${migrationId}`)

    ws.onopen = () => {
      setState((prev) => ({ ...prev, isConnected: true }))
    }

    ws.onmessage = (event) => {
      try {
        const data: WSStatusMessage = JSON.parse(event.data)
        setState({
          status: data.status,
          rowCount: data.row_count,
          errorMessage: data.error_message,
          isConnected: true,
        })
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    ws.onclose = () => {
      setState((prev) => ({ ...prev, isConnected: false }))
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setState((prev) => ({ ...prev, isConnected: false }))
    }

    wsRef.current = ws
  }, [migrationId])

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  return {
    ...state,
    reconnect: connect,
  }
}
