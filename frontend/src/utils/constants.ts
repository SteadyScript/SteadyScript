import type { ColorRange, PenColor } from '../types';

export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

export const PEN_COLORS: Record<PenColor, ColorRange> = {
  red: { hMin: 0, hMax: 10, sMin: 100, sMax: 255, vMin: 100, vMax: 255 },
  green: { hMin: 35, hMax: 85, sMin: 100, sMax: 255, vMin: 100, vMax: 255 },
  blue: { hMin: 100, hMax: 130, sMin: 100, sMax: 255, vMin: 100, vMax: 255 },
};

export const ACTIVE_PEN_COLOR: PenColor = 'red';

export const STABILITY_THRESHOLDS = {
  STABLE: 80,
  WARNING: 50,
};

export const STABILITY_COLORS = {
  stable: '#22c55e',
  warning: '#eab308',
  unstable: '#ef4444',
};

export const CAMERA_CONFIG = {
  width: 640,
  height: 480,
  frameRate: 30,
};

export const TRACKING_CONFIG = {
  historyLength: 30,
  smoothingFactor: 0.3,
};

