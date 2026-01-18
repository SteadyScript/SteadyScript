import { useMemo } from 'react';
import { type Session } from '../utils/progressCalculations';

interface ProfileStats {
  currentStreak: number;
  longestStreak: number;
  totalSessions: number;
  holdSessions: number;
  followSessions: number;
  avgJitterScore: number;
  avgTremorScore: number;
  bestJitterScore: number;
  bestTremorScore: number;
  avgP95Jitter: number;
  avgP95Lateral: number;
}

// Calculate streak from session dates
function calculateStreak(sessions: Session[]): { current: number; longest: number } {
  if (sessions.length === 0) return { current: 0, longest: 0 };

  // Get unique dates (just the date portion)
  const sessionDates = sessions
    .map((s) => new Date(s.timestamp).toDateString())
    .filter((date, index, arr) => arr.indexOf(date) === index)
    .sort((a, b) => new Date(b).getTime() - new Date(a).getTime()); // Most recent first

  if (sessionDates.length === 0) return { current: 0, longest: 0 };

  const today = new Date().toDateString();
  const yesterday = new Date(Date.now() - 86400000).toDateString();

  let currentStreak = 0;
  let longestStreak = 0;
  let tempStreak = 0;

  // Check if there's a session today or yesterday to start counting
  const startsFromRecent = sessionDates[0] === today || sessionDates[0] === yesterday;

  for (let i = 0; i < sessionDates.length; i++) {
    const currentDate = new Date(sessionDates[i]);
    const nextDate = i + 1 < sessionDates.length ? new Date(sessionDates[i + 1]) : null;

    tempStreak++;

    if (nextDate) {
      const dayDiff = Math.floor(
        (currentDate.getTime() - nextDate.getTime()) / 86400000
      );

      if (dayDiff > 1) {
        // Gap in streak
        longestStreak = Math.max(longestStreak, tempStreak);
        if (i === 0 && startsFromRecent) {
          currentStreak = tempStreak;
        }
        tempStreak = 0;
      }
    } else {
      // Last item
      longestStreak = Math.max(longestStreak, tempStreak);
      if (startsFromRecent && currentStreak === 0) {
        currentStreak = tempStreak;
      }
    }
  }

  return { current: currentStreak, longest: longestStreak };
}

export function useProfileStats(sessions: Session[]): ProfileStats {
  return useMemo(() => {
    if (sessions.length === 0) {
      return {
        currentStreak: 0,
        longestStreak: 0,
        totalSessions: 0,
        holdSessions: 0,
        followSessions: 0,
        avgJitterScore: 0,
        avgTremorScore: 0,
        bestJitterScore: 0,
        bestTremorScore: 0,
        avgP95Jitter: 0,
        avgP95Lateral: 0,
      };
    }

    const holdSessions = sessions.filter((s) => s.type === 'HOLD');
    const followSessions = sessions.filter((s) => s.type === 'FOLLOW');

    // Calculate streak
    const { current: currentStreak, longest: longestStreak } = calculateStreak(sessions);

    // Calculate tremor score averages
    const allTremorScores = sessions.map((s) => s.tremor_score);
    const avgTremorScore =
      allTremorScores.reduce((a, b) => a + b, 0) / allTremorScores.length;
    const bestTremorScore = Math.max(...allTremorScores);

    // Calculate jitter stats (from HOLD sessions)
    const jitterValues = holdSessions
      .map((s) => s.p95_jitter)
      .filter((v): v is number => v !== undefined);
    const avgP95Jitter =
      jitterValues.length > 0
        ? jitterValues.reduce((a, b) => a + b, 0) / jitterValues.length
        : 0;
    const bestJitterScore = jitterValues.length > 0 ? Math.min(...jitterValues) : 0;

    // For "jitter score" we'll invert it so lower jitter = higher score
    // Score = max(0, 100 - (jitter * 5)) approximately
    const avgJitterScore = Math.max(0, 100 - avgP95Jitter * 5);

    // Calculate lateral stats (from FOLLOW sessions)
    const lateralValues = followSessions
      .map((s) => s.p95_lateral_jitter)
      .filter((v): v is number => v !== undefined);
    const avgP95Lateral =
      lateralValues.length > 0
        ? lateralValues.reduce((a, b) => a + b, 0) / lateralValues.length
        : 0;

    return {
      currentStreak,
      longestStreak,
      totalSessions: sessions.length,
      holdSessions: holdSessions.length,
      followSessions: followSessions.length,
      avgJitterScore,
      avgTremorScore,
      bestJitterScore,
      bestTremorScore,
      avgP95Jitter,
      avgP95Lateral,
    };
  }, [sessions]);
}
