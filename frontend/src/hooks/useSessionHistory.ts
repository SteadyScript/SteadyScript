import { useState, useEffect, useCallback } from 'react';
import { type Session, calculateTrend } from '../utils/progressCalculations';

const API_BASE = 'http://localhost:8000';

interface UseSessionHistoryResult {
  sessions: Session[];
  isLoading: boolean;
  error: string | null;
  trend: 'improving' | 'declining' | 'stable';
  trendPercent: number;
  refetch: () => void;
}

export function useSessionHistory(limit: number = 50): UseSessionHistoryResult {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/sessions?limit=${limit}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch sessions: ${response.statusText}`);
      }

      const data = await response.json();
      setSessions(data.sessions || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sessions');
      setSessions([]);
    } finally {
      setIsLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  // Calculate trend
  const { trend, percent: trendPercent } = calculateTrend(sessions);

  return {
    sessions,
    isLoading,
    error,
    trend,
    trendPercent,
    refetch: fetchSessions,
  };
}
