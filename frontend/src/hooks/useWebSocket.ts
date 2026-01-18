import { useEffect, useRef, useState, useCallback } from 'react';

interface TrackingData {
  position: { x: number; y: number } | null;
  marker_detected: boolean;
  stability: {
    score: number;
    level: string;
    jitter: number;
  };
  session: {
    is_active: boolean;
    elapsed: number;
    remaining: number;
    tremor_score: number;
  };
}

interface WebSocketMessage {
  type: string;
  data: TrackingData | string | Record<string, unknown>;
}

const WS_URL = 'ws://localhost:8000/ws/tracking';

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [trackingData, setTrackingData] = useState<TrackingData | null>(null);
  const [sessionMetrics, setSessionMetrics] = useState<Record<string, unknown> | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);

        if (message.type === 'tracking') {
          setTrackingData(message.data as TrackingData);
        } else if (message.type === 'session_stopped') {
          setSessionMetrics(message.data as Record<string, unknown>);
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
      setTimeout(connect, 2000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const sendMessage = useCallback((type: string, data?: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, data }));
    }
  }, []);

  const startSession = useCallback(() => {
    sendMessage('session_start');
  }, [sendMessage]);

  const stopSession = useCallback(() => {
    sendMessage('session_stop');
  }, [sendMessage]);

  const updateHSV = useCallback((lower: number[], upper: number[]) => {
    sendMessage('hsv_update', {
      lower_h: lower[0],
      lower_s: lower[1],
      lower_v: lower[2],
      upper_h: upper[0],
      upper_s: upper[1],
      upper_v: upper[2],
    });
  }, [sendMessage]);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return {
    isConnected,
    trackingData,
    sessionMetrics,
    startSession,
    stopSession,
    updateHSV,
    sendMessage,
  };
}

