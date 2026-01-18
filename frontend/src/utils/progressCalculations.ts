// Progress and trend calculation utilities for session history

export interface Session {
  timestamp: string;
  type: 'HOLD' | 'FOLLOW';
  duration_s: number;
  tremor_score: number;
  avg_jitter?: number;
  p95_jitter?: number;
  avg_lateral_jitter?: number;
  p95_lateral_jitter?: number;
  max_lateral_jitter?: number;
  beats_total?: number;
  frames_total: number;
  frames_marker_found: number;
}

export interface SessionStats {
  totalSessions: number;
  holdSessions: number;
  followSessions: number;
  avgScoreRecent: number;
  avgScorePrevious: number;
  trend: 'improving' | 'declining' | 'stable';
  trendPercent: number;
}

/**
 * Calculate average score from a list of sessions
 */
export function calculateAverageScore(sessions: Session[]): number {
  if (sessions.length === 0) return 0;
  const scores = sessions.map((s) => s.tremor_score);
  return scores.reduce((a, b) => a + b, 0) / scores.length;
}

/**
 * Calculate trend by comparing recent sessions to previous sessions
 */
export function calculateTrend(sessions: Session[]): {
  trend: 'improving' | 'declining' | 'stable';
  percent: number;
} {
  if (sessions.length < 2) {
    return { trend: 'stable', percent: 0 };
  }

  // Sort by timestamp (most recent first)
  const sorted = [...sessions].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  const recent5 = sorted.slice(0, 5);
  const previous5 = sorted.slice(5, 10);

  const avgRecent = calculateAverageScore(recent5);
  const avgPrevious = previous5.length > 0 ? calculateAverageScore(previous5) : avgRecent;

  if (avgPrevious === 0) {
    return { trend: 'stable', percent: 0 };
  }

  const percent = ((avgRecent - avgPrevious) / avgPrevious) * 100;

  if (percent > 5) {
    return { trend: 'improving', percent };
  } else if (percent < -5) {
    return { trend: 'declining', percent };
  }
  return { trend: 'stable', percent };
}

/**
 * Get score color based on value
 */
export function getScoreColor(score: number): string {
  if (score >= 70) return '#22c55e'; // green
  if (score >= 40) return '#f59e0b'; // amber
  return '#ef4444'; // red
}

/**
 * Get score status text
 */
export function getScoreStatus(score: number): 'good' | 'moderate' | 'poor' {
  if (score >= 70) return 'good';
  if (score >= 40) return 'moderate';
  return 'poor';
}

/**
 * Format timestamp for display
 */
export function formatSessionDate(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Format timestamp for full display
 */
export function formatSessionDateTime(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

/**
 * Get trend arrow symbol
 */
export function getTrendSymbol(trend: 'improving' | 'declining' | 'stable'): string {
  switch (trend) {
    case 'improving':
      return '↑';
    case 'declining':
      return '↓';
    default:
      return '→';
  }
}

/**
 * Prepare data for the progress chart
 */
export function prepareChartData(sessions: Session[]): Array<{
  date: string;
  score: number;
  type: string;
  fullDate: string;
}> {
  // Sort by timestamp (oldest first for chart)
  const sorted = [...sessions].sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );

  return sorted.map((session) => ({
    date: formatSessionDate(session.timestamp),
    score: session.tremor_score,
    type: session.type,
    fullDate: formatSessionDateTime(session.timestamp),
  }));
}

/**
 * Calculate detection rate percentage
 */
export function calculateDetectionRate(session: Session): number {
  if (session.frames_total === 0) return 0;
  return Math.round((session.frames_marker_found / session.frames_total) * 100);
}
