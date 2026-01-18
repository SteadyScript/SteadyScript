// Centralized theme definitions for SteadyScript

export const colors = {
  // Backgrounds
  background: {
    primary: '#0d0f12',
    secondary: '#1a1d24',
    surface: '#1e2128',
    surfaceHover: '#252932',
  },

  // Borders
  border: {
    default: '#2a2f38',
    subtle: '#1e2229',
    hover: '#3a4049',
  },

  // Mode-specific accents
  hold: {
    primary: '#0ea5e9',
    secondary: '#14b8a6',
    gradient: 'linear-gradient(135deg, #0ea5e9 0%, #14b8a6 100%)',
    glow: 'rgba(14, 165, 233, 0.4)',
  },

  follow: {
    primary: '#f97316',
    secondary: '#fb923c',
    gradient: 'linear-gradient(135deg, #f97316 0%, #fb923c 100%)',
    glow: 'rgba(249, 115, 22, 0.4)',
  },

  // Status colors
  status: {
    success: '#10b981',
    warning: '#f59e0b',
    error: '#f43f5e',
    info: '#3b82f6',
  },

  // Text
  text: {
    primary: '#ffffff',
    secondary: '#a1a7b3',
    muted: '#6b7280',
  },
} as const;

export const gradients = {
  // Background gradients
  backgroundMain: `linear-gradient(135deg, ${colors.background.primary} 0%, ${colors.background.secondary} 100%)`,

  // Card gradients
  cardDefault: `linear-gradient(145deg, ${colors.background.surface} 0%, #191c22 100%)`,
  cardGlow: 'linear-gradient(145deg, rgba(30, 33, 40, 0.9) 0%, rgba(25, 28, 34, 0.95) 100%)',

  // Accent gradients
  holdGradient: 'linear-gradient(135deg, #0ea5e9 0%, #14b8a6 100%)',
  followGradient: 'linear-gradient(135deg, #f97316 0%, #fb923c 100%)',

  // Status gradients
  successGradient: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
  warningGradient: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
  errorGradient: 'linear-gradient(135deg, #f43f5e 0%, #fb7185 100%)',

  // Orb gradients
  orbCyan: 'radial-gradient(circle, rgba(14, 165, 233, 0.15) 0%, transparent 70%)',
  orbOrange: 'radial-gradient(circle, rgba(249, 115, 22, 0.12) 0%, transparent 70%)',
  orbTeal: 'radial-gradient(circle, rgba(20, 184, 166, 0.1) 0%, transparent 70%)',
} as const;

export const shadows = {
  card: '0 4px 24px rgba(0, 0, 0, 0.3)',
  cardHover: '0 8px 32px rgba(0, 0, 0, 0.4)',
  holdGlow: '0 0 40px rgba(14, 165, 233, 0.3)',
  followGlow: '0 0 40px rgba(249, 115, 22, 0.3)',
  successGlow: '0 0 20px rgba(16, 185, 129, 0.3)',
  warningGlow: '0 0 20px rgba(245, 158, 11, 0.3)',
  errorGlow: '0 0 20px rgba(244, 63, 94, 0.3)',
} as const;

export const typography = {
  // Score display
  scoreXl: {
    fontSize: '64px',
    fontWeight: 700,
    lineHeight: 1,
  },
  scoreLg: {
    fontSize: '48px',
    fontWeight: 700,
    lineHeight: 1,
  },
  scoreMd: {
    fontSize: '32px',
    fontWeight: 600,
    lineHeight: 1.2,
  },

  // Headers
  headerLg: {
    fontSize: '20px',
    fontWeight: 600,
    letterSpacing: '-0.02em',
  },
  headerMd: {
    fontSize: '18px',
    fontWeight: 600,
  },

  // Body
  body: {
    fontSize: '14px',
    fontWeight: 400,
  },

  // Labels
  label: {
    fontSize: '12px',
    fontWeight: 500,
    letterSpacing: '0.05em',
    textTransform: 'uppercase' as const,
  },
} as const;

// Helper function to get mode colors
export function getModeColors(mode: 'HOLD' | 'FOLLOW') {
  return mode === 'HOLD' ? colors.hold : colors.follow;
}

// Helper function to get status colors
export function getStatusColors(status: 'stable' | 'warning' | 'unstable' | 'good' | 'poor' | string) {
  const normalized = status.toLowerCase();
  if (normalized === 'stable' || normalized === 'good') {
    return {
      color: colors.status.success,
      glow: shadows.successGlow,
    };
  }
  if (normalized === 'warning' || normalized === 'moderate') {
    return {
      color: colors.status.warning,
      glow: shadows.warningGlow,
    };
  }
  return {
    color: colors.status.error,
    glow: shadows.errorGlow,
  };
}
