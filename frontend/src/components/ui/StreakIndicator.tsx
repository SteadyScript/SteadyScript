import { motion } from 'framer-motion';
import { Flame } from 'lucide-react';

interface StreakIndicatorProps {
  currentStreak: number;
  targetStreak?: number;
  completedDays?: boolean[];
  className?: string;
}

export function StreakIndicator({
  currentStreak,
  targetStreak = 7,
  completedDays = [],
  className = '',
}: StreakIndicatorProps) {
  // Create an array of dots to show (use completedDays if provided, otherwise generate based on streak)
  const dotsToShow = targetStreak;
  const dots = completedDays.length > 0
    ? completedDays.slice(0, dotsToShow)
    : Array(dotsToShow).fill(false).map((_, i) => i < currentStreak);

  return (
    <div className={`${className}`}>
      {/* Streak count with flame */}
      <div className="flex items-center gap-2 mb-3">
        <motion.div
          className="flex items-center justify-center w-8 h-8 rounded-lg bg-orange-500/20"
          animate={{
            scale: [1, 1.05, 1],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          <Flame size={18} className="text-orange-400" />
        </motion.div>
        <div>
          <span className="text-2xl font-bold text-white">{currentStreak}</span>
          <span className="text-gray-400 text-sm ml-1">day streak</span>
        </div>
      </div>

      {/* Dot indicators */}
      <div className="flex items-center gap-2">
        {dots.map((completed, index) => (
          <motion.div
            key={index}
            className="relative"
            initial={false}
            animate={{
              scale: completed ? 1 : 1,
            }}
          >
            {/* Background dot */}
            <div
              className={`w-4 h-4 rounded-full transition-colors duration-300 ${
                completed ? 'bg-emerald-500' : 'bg-gray-600/50'
              }`}
              style={{
                boxShadow: completed ? '0 0 12px rgba(16, 185, 129, 0.5)' : undefined,
              }}
            />

            {/* Animated fill overlay */}
            {completed && (
              <motion.div
                className="absolute inset-0 rounded-full bg-emerald-400"
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{
                  type: 'spring',
                  stiffness: 300,
                  damping: 20,
                  delay: index * 0.05,
                }}
                style={{
                  boxShadow: '0 0 12px rgba(16, 185, 129, 0.5)',
                }}
              />
            )}
          </motion.div>
        ))}

        {/* Target indicator */}
        {targetStreak > dots.length && (
          <span className="text-xs text-gray-500 ml-1">+{targetStreak - dots.length}</span>
        )}
      </div>

      {/* Goal text */}
      <p className="text-xs text-gray-500 mt-2">
        {currentStreak >= targetStreak
          ? 'Goal reached! Keep going!'
          : `${targetStreak - currentStreak} more days to reach your goal`}
      </p>
    </div>
  );
}
