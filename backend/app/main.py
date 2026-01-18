"""
SteadyScript Backend - FastAPI Application
Real-time tremor tracking using computer vision.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import video, websocket, game2_ws, sessions

app = FastAPI(
    title="SteadyScript API",
    description="Real-time hand stability tracking using OpenCV",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(video.router, tags=["video"])
app.include_router(websocket.router, tags=["websocket"])
app.include_router(game2_ws.router, tags=["game2"])
app.include_router(sessions.router, tags=["sessions"])


@app.get("/")
async def root():
    return {
        "name": "SteadyScript API",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "video_feed": "/video_feed",
            "tracking_data": "/tracking_data",
            "websocket": "/ws/tracking",
            "session_start": "/session/start",
            "session_stop": "/session/stop",
            "hsv_update": "/hsv"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.on_event("shutdown")
async def shutdown_event():
    from .api.video import camera
    if camera is not None and camera.isOpened():
        camera.release()
