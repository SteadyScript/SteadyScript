// Framer-motion animation presets for SteadyScript
import type { Transition, Variants } from 'framer-motion';

// Standard transitions
export const springTransition: Transition = {
  type: 'spring',
  stiffness: 300,
  damping: 25,
};

export const smoothTransition: Transition = {
  type: 'tween',
  duration: 0.3,
  ease: 'easeInOut',
};

export const fastTransition: Transition = {
  type: 'tween',
  duration: 0.15,
  ease: 'easeOut',
};

// Fade animations
export const fadeIn: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
};

export const fadeInUp: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 20 },
};

export const fadeInScale: Variants = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 },
};

// Modal animation
export const modalVariants: Variants = {
  initial: { opacity: 0, scale: 0.9, y: 20 },
  animate: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: springTransition,
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: 10,
    transition: fastTransition,
  },
};

export const overlayVariants: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: smoothTransition },
  exit: { opacity: 0, transition: fastTransition },
};

// Card hover effect
export const cardHover: Variants = {
  initial: { y: 0 },
  hover: { y: -4, transition: smoothTransition },
};

// Accordion/collapse animation
export const accordionVariants: Variants = {
  collapsed: {
    height: 0,
    opacity: 0,
    transition: { duration: 0.2, ease: 'easeInOut' },
  },
  expanded: {
    height: 'auto',
    opacity: 1,
    transition: { duration: 0.3, ease: 'easeOut' },
  },
};

// Pulse animation for connection badge
export const pulseVariants: Variants = {
  pulse: {
    scale: [1, 1.1, 1],
    opacity: [1, 0.8, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

// Number count-up (for score gauge)
export const countUpConfig = {
  duration: 0.5,
  ease: 'easeOut' as const,
};

// Circular progress animation
export const circleProgressVariants: Variants = {
  initial: { pathLength: 0 },
  animate: (progress: number) => ({
    pathLength: progress,
    transition: { duration: 0.8, ease: 'easeOut' },
  }),
};

// Stagger children animations
export const staggerContainer: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export const staggerItem: Variants = {
  initial: { opacity: 0, y: 10 },
  animate: {
    opacity: 1,
    y: 0,
    transition: smoothTransition,
  },
};

// Value change pulse
export const valuePulse: Variants = {
  initial: { scale: 1 },
  pulse: {
    scale: [1, 1.05, 1],
    transition: { duration: 0.3 },
  },
};

// Reduced motion variants (for accessibility)
export const reducedMotionVariants: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
};

// Background orb floating animation
export const orbFloatVariants: Variants = {
  animate: {
    x: [0, 30, -20, 0],
    y: [0, -40, 20, 0],
    scale: [1, 1.05, 0.95, 1],
    transition: {
      duration: 40,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

export const orbFloatVariants2: Variants = {
  animate: {
    x: [0, -25, 35, 0],
    y: [0, 30, -25, 0],
    scale: [1, 0.92, 1.08, 1],
    transition: {
      duration: 30,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

// Score counting animation (for AnimatePresence key changes)
export const scoreChangeVariants: Variants = {
  initial: { opacity: 0, y: 10, scale: 0.9 },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.3, ease: 'easeOut' },
  },
  exit: {
    opacity: 0,
    y: -10,
    scale: 0.9,
    transition: { duration: 0.2 },
  },
};

// Streak dot fill animation
export const streakDotVariants: Variants = {
  empty: {
    scale: 1,
    backgroundColor: 'rgba(107, 114, 128, 0.3)',
  },
  filled: {
    scale: [0, 1.3, 1],
    backgroundColor: '#10b981',
    transition: {
      scale: { duration: 0.4, ease: 'easeOut' },
      backgroundColor: { duration: 0.2 },
    },
  },
};

// Card entrance with stagger
export const cardEntranceVariants: Variants = {
  initial: { opacity: 0, y: 20, scale: 0.98 },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.46, 0.45, 0.94],
    },
  },
};

export const staggerContainerFast: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.05,
    },
  },
};

// Glow pulse for active elements
export const glowPulseVariants: Variants = {
  idle: {
    boxShadow: '0 0 20px rgba(14, 165, 233, 0.2)',
  },
  pulse: {
    boxShadow: [
      '0 0 20px rgba(14, 165, 233, 0.2)',
      '0 0 40px rgba(14, 165, 233, 0.4)',
      '0 0 20px rgba(14, 165, 233, 0.2)',
    ],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

// Progress ring animation
export const progressRingVariants: Variants = {
  initial: { strokeDashoffset: 100 },
  animate: (progress: number) => ({
    strokeDashoffset: 100 - progress,
    transition: { duration: 1, ease: 'easeOut' },
  }),
};

// Shimmer effect for loading states
export const shimmerVariants: Variants = {
  animate: {
    backgroundPosition: ['200% 0', '-200% 0'],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

// Metric card hover
export const metricCardHover: Variants = {
  initial: {
    y: 0,
    boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
  },
  hover: {
    y: -4,
    boxShadow: '0 12px 32px rgba(0, 0, 0, 0.4)',
    transition: { duration: 0.25, ease: 'easeOut' },
  },
};
