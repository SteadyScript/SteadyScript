"""
Pydantic models for tracking data.

These models define the data structures used for:
- WebSocket messages
- API responses
- Internal data transfer
"""

from pydantic import BaseModel
from typing import Optional, Literal


class Position(BaseModel):
    x: int
    y: int


class StabilityScore(BaseModel):
    score: int
    level: Literal["stable", "warning", "unstable"]
    jitter: float


class TrackingFrame(BaseModel):
    position: Optional[Position]
    stability: StabilityScore
    feedback: str
    timestamp: float


class WebSocketMessage(BaseModel):
    type: Literal["tracking", "error", "connected"]
    data: TrackingFrame | str


class SessionSummary(BaseModel):
    average_stability: float
    duration_seconds: float
    accuracy: float
    targets_completed: int
    total_targets: int
    feedback: str

