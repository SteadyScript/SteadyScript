import { motion, type HTMLMotionProps } from 'framer-motion';
import { smoothTransition, metricCardHover } from '../../styles/animations';
import { type ReactNode } from 'react';

interface CardProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
  children: ReactNode;
  variant?: 'default' | 'glass' | 'glow';
  glowMode?: 'hold' | 'follow';
  hoverable?: boolean;
  noPadding?: boolean;
  className?: string;
}

export function Card({
  children,
  variant = 'default',
  glowMode,
  hoverable = false,
  noPadding = false,
  className = '',
  ...props
}: CardProps) {
  const baseClasses = `rounded-2xl ${noPadding ? '' : 'p-4'} transition-all duration-300`;

  const variantClasses = {
    default: 'bg-gradient-to-br from-[#1e2128] to-[#191c22] border border-[#2a2f38]',
    glass: 'bg-[#1e2128]/60 backdrop-blur-md border border-[#2a2f38]/50',
    glow: `bg-gradient-to-br from-[#1e2128] to-[#191c22] border ${
      glowMode === 'follow'
        ? 'border-orange-500/30 shadow-[0_0_40px_rgba(249,115,22,0.15)]'
        : 'border-cyan-500/30 shadow-[0_0_40px_rgba(14,165,233,0.15)]'
    }`,
  };

  const hoverVariants = hoverable ? metricCardHover : undefined;

  return (
    <motion.div
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      variants={hoverVariants}
      initial={hoverable ? 'initial' : undefined}
      whileHover={hoverable ? 'hover' : undefined}
      transition={smoothTransition}
      style={{
        boxShadow: variant !== 'glow' ? '0 4px 24px rgba(0, 0, 0, 0.3)' : undefined,
      }}
      {...props}
    >
      {children}
    </motion.div>
  );
}

interface CardHeaderProps {
  children: ReactNode;
  className?: string;
}

export function CardHeader({ children, className = '' }: CardHeaderProps) {
  return (
    <div className={`mb-4 ${className}`}>
      {children}
    </div>
  );
}

interface CardTitleProps {
  children: ReactNode;
  className?: string;
}

export function CardTitle({ children, className = '' }: CardTitleProps) {
  return (
    <h2 className={`text-lg font-semibold text-white ${className}`}>
      {children}
    </h2>
  );
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function CardContent({ children, className = '' }: CardContentProps) {
  return (
    <div className={className}>
      {children}
    </div>
  );
}

// Mini card for test type displays (HOLD/FOLLOW cards)
interface TestCardProps {
  mode: 'HOLD' | 'FOLLOW';
  title: string;
  primaryValue: number;
  primaryLabel: string;
  secondaryValue?: number;
  secondaryLabel?: string;
  status?: 'good' | 'moderate' | 'poor';
  compact?: boolean;
  className?: string;
}

export function TestCard({
  mode,
  title,
  primaryValue,
  primaryLabel,
  secondaryValue,
  secondaryLabel,
  status,
  compact = false,
  className = '',
}: TestCardProps) {
  const isHold = mode === 'HOLD';
  const accentColor = isHold ? '#0ea5e9' : '#f97316';
  const accentBg = isHold ? 'rgba(14, 165, 233, 0.1)' : 'rgba(249, 115, 22, 0.1)';

  const statusColors = {
    good: '#10b981',
    moderate: '#f59e0b',
    poor: '#f43f5e',
  };

  return (
    <div
      className={`rounded-xl border transition-all duration-200 hover:border-opacity-60 ${className}`}
      style={{
        background: `linear-gradient(135deg, ${accentBg} 0%, rgba(30, 33, 40, 0.8) 100%)`,
        borderColor: `${accentColor}30`,
      }}
    >
      <div className={compact ? 'p-3' : 'p-4'}>
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <span
            className="text-xs font-semibold uppercase tracking-wide"
            style={{ color: accentColor }}
          >
            {title}
          </span>
          {status && (
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: statusColors[status] }}
            />
          )}
        </div>

        {/* Primary metric */}
        <div className="flex items-baseline gap-1">
          <span className={`font-bold text-white ${compact ? 'text-xl' : 'text-2xl'}`}>
            {primaryValue.toFixed(1)}
          </span>
          <span className="text-xs text-gray-400">{primaryLabel}</span>
        </div>

        {/* Secondary metric */}
        {secondaryValue !== undefined && secondaryLabel && (
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-sm text-gray-300">{secondaryValue.toFixed(1)}</span>
            <span className="text-xs text-gray-500">{secondaryLabel}</span>
          </div>
        )}
      </div>
    </div>
  );
}
