import { useEffect, useRef, useState, useCallback } from 'react';

interface Game2Metrics {
  mode: 'HOLD' | 'FOLLOW';
  position: { x: number; y: number } | null;
  marker_detected: boolean;
  jitter?: number;
  p95_jitter?: number;
  lateral_jitter?: number;
  p95_lateral_jitter?: number;
  stability_level?: string;
  feedback_status?: string;
  score: number;
  session_state: string;
  time_remaining: number;
  elapsed: number;
  beat_count?: number;
  bpm?: number;
}

interface WebSocketMessage {
  type: string;
  data: any;
}

const WS_URL = 'ws://localhost:8000/ws/game2';

export function useGame2WebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [frameData, setFrameData] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<Game2Metrics | null>(null);
  const [sessionResults, setSessionResults] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      console.log('Game2 WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);

        if (message.type === 'frame') {
          setFrameData(message.data);
        } else if (message.type === 'metrics') {
          setMetrics(message.data);
        } else if (message.type === 'session_complete') {
          setSessionResults(message.data);
        } else if (message.type === 'connected') {
          console.log('Connected:', message.data);
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('Game2 WebSocket disconnected');
      setTimeout(connect, 2000);
    };

    ws.onerror = (error) => {
      console.error('Game2 WebSocket error:', error);
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

  const switchMode = useCallback((mode: 'HOLD' | 'FOLLOW') => {
    sendMessage('mode_switch', { mode });
  }, [sendMessage]);

  const startSession = useCallback(() => {
    setSessionResults(null);  // Clear previous results before starting new session
    sendMessage('session_start');
  }, [sendMessage]);

  const stopSession = useCallback(() => {
    sendMessage('session_stop');
  }, [sendMessage]);

  const changeBPM = useCallback((delta: number) => {
    sendMessage('bpm_change', { delta });
  }, [sendMessage]);

  const handleCalibrationClick = useCallback((x: number, y: number) => {
    sendMessage('calibration_click', { x, y });
  }, [sendMessage]);

  const handleKeyboard = useCallback((key: string) => {
    sendMessage('keyboard', { key });
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
    frameData,
    metrics,
    sessionResults,
    switchMode,
    startSession,
    stopSession,
    changeBPM,
    handleCalibrationClick,
    handleKeyboard,
    updateHSV,
  };
}
