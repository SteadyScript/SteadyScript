import { motion, useSpring, useTransform } from 'framer-motion';
import { useEffect } from 'react';

interface CircularProgressProps {
  value: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  gradientColors?: [string, string];
  glowColor?: string;
  showValue?: boolean;
  label?: string;
  className?: string;
}

export function CircularProgress({
  value,
  max = 100,
  size = 100,
  strokeWidth = 8,
  color = '#10b981',
  gradientColors,
  glowColor,
  showValue = true,
  label,
  className = '',
}: CircularProgressProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = Math.min(value / max, 1);
  const gradientId = `progress-gradient-${Math.random().toString(36).substr(2, 9)}`;

  // Animated value
  const springValue = useSpring(0, { stiffness: 100, damping: 20 });
  const displayValue = useTransform(springValue, (val) => Math.round(val));

  useEffect(() => {
    springValue.set(value);
  }, [value, springValue]);

  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Gradient definition */}
        {gradientColors && (
          <defs>
            <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={gradientColors[0]} />
              <stop offset="100%" stopColor={gradientColors[1]} />
            </linearGradient>
          </defs>
        )}

        {/* Background track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-gray-700/40"
        />

        {/* Progress arc */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={gradientColors ? `url(#${gradientId})` : color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: circumference * (1 - progress) }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          style={{
            filter: glowColor ? `drop-shadow(0 0 8px ${glowColor})` : undefined,
          }}
        />
      </svg>

      {/* Center content */}
      {(showValue || label) && (
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          {showValue && (
            <motion.span
              className="text-xl font-bold text-white tabular-nums"
              style={{ fontSize: size * 0.22 }}
            >
              {useTransform(displayValue, (v) => v).get() || 0}
            </motion.span>
          )}
          {label && (
            <span
              className="text-gray-400 font-medium uppercase tracking-wide"
              style={{ fontSize: Math.max(size * 0.1, 10) }}
            >
              {label}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
