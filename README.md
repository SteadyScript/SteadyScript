# SteadyScript

Real-time hand stability tracking application using computer vision. Track pen movements via webcam and receive visual feedback on hand steadiness.

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│  FRONTEND (React + Vite)                                        │
│  ┌──────────────────┐    ┌──────────────────────────────────┐  │
│  │ <img> tag        │    │ WebSocket Client                 │  │
│  │ src=/video_feed  │    │ Receives: position, stability    │  │
│  │ (MJPEG stream)   │    │ Sends: session controls          │  │
│  └──────────────────┘    └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    HTTP + WebSocket
                              │
┌─────────────────────────────────────────────────────────────────┐
│  BACKEND (FastAPI + OpenCV)                                     │
│  ┌──────────────────┐    ┌──────────────────────────────────┐  │
│  │ cv2.VideoCapture │───▶│ detect_marker()                  │  │
│  │ (webcam)         │    │ HSV color segmentation           │  │
│  └──────────────────┘    └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Pen Setup

- **Colored marker on pen tip**: OpenCV tracks this using HSV color segmentation (default: blue)
- **LEDs on pen body** (optional hardware): Physical feedback - green = stable, red = jittering

## Quick Start

### Prerequisites

- **Node.js** v20.9+ or v22+ (use `nvm use 22` if you have nvm)
- **Python** 3.10+
- **Webcam** connected to your computer

### 1. Start the Backend

```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:
- API: http://localhost:8000
- Video Feed: http://localhost:8000/video_feed
- API Docs: http://localhost:8000/docs

### 2. Start the Frontend (in a new terminal)

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at: http://localhost:5173

### 3. Use the Application

1. Open http://localhost:5173 in your browser
2. Allow camera access when prompted
3. Position a colored marker (default: blue) in view of the camera
4. The marker will be tracked and stability score displayed
5. Click "Start Session" to begin a 10-second tracking session

## Project Structure

```
SteadyScript/
├── frontend/                    # React + Vite + TypeScript + Tailwind
│   ├── src/
│   │   ├── App.tsx             # Main UI with video display
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts # WebSocket client for tracking data
│   │   ├── types/
│   │   │   └── index.ts        # TypeScript interfaces
│   │   └── utils/
│   │       └── constants.ts    # API URLs, color configs
│   ├── package.json
│   └── Dockerfile
│
├── backend/                     # FastAPI + OpenCV
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── api/
│   │   │   ├── video.py        # MJPEG streaming endpoint
│   │   │   └── websocket.py    # Real-time tracking WebSocket
│   │   └── compvis/
│   │       ├── cv_tracker.py   # OpenCV marker detection
│   │       ├── session.py      # Session & tremor calculation
│   │       ├── calibration.py  # Circle calibration
│   │       └── utils.py        # Helper functions
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml           # Run both services together
├── .env.example                 # Environment variables template
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/video_feed` | GET | MJPEG video stream with marker overlay |
| `/tracking_data` | GET | Current tracking data (polling fallback) |
| `/ws/tracking` | WebSocket | Real-time bidirectional communication |
| `/session/start` | POST | Start a tracking session |
| `/session/stop` | POST | Stop session and get metrics |
| `/hsv` | POST | Update HSV color range |
| `/docs` | GET | Swagger API documentation |

## Configuration

### Change Marker Color

The default tracks a **blue marker**. To change, modify `backend/app/compvis/cv_tracker.py`:

```python
# Blue (default)
DEFAULT_HSV_LOWER = np.array([100, 50, 50])
DEFAULT_HSV_UPPER = np.array([130, 255, 255])

# Green
DEFAULT_HSV_LOWER = np.array([35, 50, 50])
DEFAULT_HSV_UPPER = np.array([85, 255, 255])

# Red (needs two ranges due to HSV wrap)
DEFAULT_HSV_LOWER = np.array([0, 100, 100])
DEFAULT_HSV_UPPER = np.array([10, 255, 255])
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
PEN_COLOR=blue
DEBUG=true
STABILITY_WINDOW_SIZE=30
JITTER_THRESHOLD_LOW=5
JITTER_THRESHOLD_HIGH=15
```

## Docker (Alternative)

Run both frontend and backend with Docker Compose:

```bash
cp .env.example .env
docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000

## Troubleshooting

### Camera not detected
- Ensure no other app is using the camera
- Try changing camera index in `backend/app/api/video.py`: `cv2.VideoCapture(1)`

### Marker not detected
- Ensure good lighting
- Adjust HSV values via `/hsv` endpoint or modify defaults
- Make sure marker color is distinct from background

### Node version errors
```bash
nvm install 22
nvm use 22
nvm alias default 22
```

### uvicorn not found
```bash
python3 -m uvicorn app.main:app --reload
```

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Backend**: Python 3.10+, FastAPI, OpenCV, WebSockets
- **Communication**: MJPEG video stream + WebSocket JSON

## License

MIT
