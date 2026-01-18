import { motion, useSpring, useTransform } from 'framer-motion';
import { useEffect, useId } from 'react';

interface ScoreGaugeProps {
  score: number;
  status: 'stable' | 'warning' | 'unstable' | 'good' | 'poor' | string;
  mode: 'HOLD' | 'FOLLOW';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function ScoreGauge({
  score,
  status,
  mode,
  size = 'md',
  className = '',
}: ScoreGaugeProps) {
  const gradientId = useId();

  // Size configurations
  const sizeConfig = {
    sm: { dimension: 100, strokeWidth: 6, fontSize: 'text-2xl', subSize: 'text-xs' },
    md: { dimension: 144, strokeWidth: 8, fontSize: 'text-4xl', subSize: 'text-sm' },
    lg: { dimension: 180, strokeWidth: 10, fontSize: 'text-5xl', subSize: 'text-base' },
  };

  const config = sizeConfig[size];
  const radius = (config.dimension - config.strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (Math.min(score, 100) / 100) * circumference;

  // Animated score value
  const springScore = useSpring(0, { stiffness: 80, damping: 20 });
  const displayScore = useTransform(springScore, (val) => Math.round(val));

  useEffect(() => {
    springScore.set(score);
  }, [score, springScore]);

  // Status colors with gradients
  const getStatusColors = (status: string) => {
    const normalized = status.toLowerCase();
    if (normalized === 'stable' || normalized === 'good') {
      return {
        gradient: ['#10b981', '#34d399'],
        text: 'text-emerald-400',
        glow: 'rgba(16, 185, 129, 0.4)',
        bg: 'rgba(16, 185, 129, 0.1)',
      };
    }
    if (normalized === 'warning' || normalized === 'moderate') {
      return {
        gradient: ['#f59e0b', '#fbbf24'],
        text: 'text-amber-400',
        glow: 'rgba(245, 158, 11, 0.4)',
        bg: 'rgba(245, 158, 11, 0.1)',
      };
    }
    return {
      gradient: ['#f43f5e', '#fb7185'],
      text: 'text-rose-400',
      glow: 'rgba(244, 63, 94, 0.4)',
      bg: 'rgba(244, 63, 94, 0.1)',
    };
  };

  const colors = getStatusColors(status);

  // Mode-specific accent for label
  const modeColors = mode === 'HOLD'
    ? { primary: '#0ea5e9', secondary: '#14b8a6' }
    : { primary: '#f97316', secondary: '#fb923c' };

  return (
    <div className={`flex flex-col items-center ${className}`}>
      {/* Circular gauge */}
      <div className="relative" style={{ width: config.dimension, height: config.dimension }}>
        {/* Glow effect behind */}
        <div
          className="absolute inset-0 rounded-full blur-xl opacity-30"
          style={{
            background: `radial-gradient(circle, ${colors.glow} 0%, transparent 70%)`,
          }}
        />

        <svg className="w-full h-full transform -rotate-90">
          {/* Gradient definition */}
          <defs>
            <linearGradient id={`score-gradient-${gradientId}`} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={colors.gradient[0]} />
              <stop offset="100%" stopColor={colors.gradient[1]} />
            </linearGradient>
          </defs>

          {/* Background ring */}
          <circle
            cx={config.dimension / 2}
            cy={config.dimension / 2}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={config.strokeWidth}
            className="text-gray-700/30"
          />

          {/* Progress ring */}
          <motion.circle
            cx={config.dimension / 2}
            cy={config.dimension / 2}
            r={radius}
            fill="none"
            stroke={`url(#score-gradient-${gradientId})`}
            strokeWidth={config.strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: circumference - progress }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            style={{
              filter: `drop-shadow(0 0 8px ${colors.glow})`,
            }}
          />
        </svg>

        {/* Score number */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className={`font-bold tabular-nums ${config.fontSize} ${colors.text}`}
            key={Math.round(score / 10)}
            initial={{ scale: 0.9, opacity: 0.5 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            {useTransform(displayScore, (val) => val).get() || 0}
          </motion.span>
          <span className={`text-gray-500 font-medium ${config.subSize}`}>/ 100</span>
        </div>
      </div>

      {/* Status badge */}
      <motion.div
        className={`mt-4 px-4 py-1.5 rounded-full text-sm font-medium capitalize ${colors.text}`}
        style={{
          backgroundColor: colors.bg,
          border: `1px solid ${colors.gradient[0]}30`,
          boxShadow: `0 0 20px ${colors.glow}`,
        }}
        initial={{ y: 10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        {status}
      </motion.div>

      {/* Mode indicator */}
      <div
        className="mt-2 text-xs font-medium uppercase tracking-wide"
        style={{
          background: `linear-gradient(135deg, ${modeColors.primary} 0%, ${modeColors.secondary} 100%)`,
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }}
      >
        {mode === 'HOLD' ? 'Stability Score' : 'Movement Quality'}
      </div>
    </div>
  );
}
