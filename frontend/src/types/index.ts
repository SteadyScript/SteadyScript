export interface Position {
  x: number;
  y: number;
}

export interface TrackingData {
  position: Position | null;
  timestamp: number;
  detected: boolean;
}

export interface StabilityScore {
  score: number;
  level: 'stable' | 'warning' | 'unstable';
  jitter: number;
}

export interface TrackingFrame {
  position: Position;
  stability: StabilityScore;
  feedback: string;
  timestamp: number;
}

export type AppMode = 'learn' | 'practice' | 'review' | 'trace';

export interface WebSocketMessage {
  type: 'tracking' | 'error' | 'connected';
  data: TrackingFrame | string;
}

export type PenColor = 'red' | 'green' | 'blue';

export interface ColorRange {
  hMin: number;
  hMax: number;
  sMin: number;
  sMax: number;
  vMin: number;
  vMax: number;
}

