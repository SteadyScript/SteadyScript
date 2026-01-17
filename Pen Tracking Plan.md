# Tremor Tracker - Project Structure & Implementation Plan

## 📁 File Structure

```
tremor-tracker/
│
├── docker-compose.yml              # Orchestrates frontend + backend
├── .env.example                    # Environment variables template
├── .gitignore
├── README.md
│
├── frontend/                       # React + Vite + TypeScript + Tailwind
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json               # TypeScript config
│   ├── tsconfig.node.json          # TypeScript config for Vite
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   │
│   └── src/
│       ├── main.tsx                # Entry point
│       ├── App.tsx                 # Main app component
│       ├── index.css               # Global styles + Tailwind
│       ├── vite-env.d.ts           # Vite type declarations
│       │
│       ├── components/
│       │   ├── CameraTracker.tsx   # Camera feed + canvas overlay
│       │   ├── StabilityIndicator.tsx  # Real-time stability meter
│       │   ├── ModeSelector.tsx    # Tabs for Learn/Practice/Review/Trace
│       │   ├── TargetOverlay.tsx   # Target points for Learn mode
│       │   ├── TracingCanvas.tsx   # Letter tracing for Trace mode
│       │   └── CoachingSummary.tsx # Tips and feedback panel
│       │
│       ├── hooks/
│       │   ├── useWebSocket.ts     # WebSocket connection management
│       │   ├── useCamera.ts        # Camera access (getUserMedia)
│       │   └── useStabilityTracker.ts  # State management for tracking
│       │
│       ├── types/
│       │   └── index.ts            # TypeScript interfaces/types
│       │
│       └── utils/
│           ├── constants.ts        # Color thresholds, API URLs
│           └── helpers.ts          # Utility functions
│
├── backend/                        # Python + FastAPI + OpenCV
│   ├── Dockerfile
│   ├── requirements.txt
│   │
│   └── app/
│       ├── __init__.py
│       ├── main.py                 # FastAPI app entry point
│       ├── config.py               # Settings and configuration
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   ├── websocket.py        # WebSocket endpoint for real-time tracking
│       │   └── coaching.py         # Coaching tips endpoints (optional)
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── tracking.py         # OpenCV color tracking logic
│       │   ├── stability.py        # Jitter/stability calculations
│       │   └── feedback.py         # Feedback message generation
│       │
│       └── models/
│           ├── __init__.py
│           └── tracking.py         # Tracking data models (Pydantic)
│
└── docker/                         # Additional Docker configs (optional)
    └── nginx.conf                  # Production reverse proxy (optional)
```

---

## 🎯 Implementation Plan

### Phase 1: Project Setup (30 min)
- [ ] Initialize project directories
- [ ] Create `docker-compose.yml`
- [ ] Set up frontend: Vite + React + TypeScript + Tailwind
- [ ] Set up backend: FastAPI + OpenCV
- [ ] Verify both services run with `docker-compose up`

### Phase 2: Camera + Basic Tracking (1-2 hours)
- [ ] **Frontend**: Implement `useCamera.ts` hook with `getUserMedia`
- [ ] **Frontend**: Display video feed in `CameraTracker.tsx`
- [ ] **Backend**: Set up WebSocket endpoint in `websocket.py`
- [ ] **Backend**: Implement OpenCV color tracking in `tracking.py`
- [ ] **Frontend**: Implement `useWebSocket.ts` hook
- [ ] **Frontend**: Send video frames → Backend → Receive position

### Phase 3: Stability Calculation (1 hour)
- [ ] **Backend**: Implement jitter algorithm in `stability.py`
- [ ] **Backend**: Return stability score (0-100) via WebSocket
- [ ] **Frontend**: Create `StabilityIndicator.tsx` component
- [ ] **Frontend**: Color-coded feedback (green/yellow/red)

### Phase 4: Learn Mode (1 hour)
- [ ] **Frontend**: `TargetOverlay.tsx` - draw two target points
- [ ] **Frontend**: Show path line between targets
- [ ] **Backend**: Calculate deviation from ideal path
- [ ] **Frontend**: Visual feedback when movement is stable

### Phase 5: Practice Mode (30 min)
- [ ] **Frontend**: Free movement with trail visualization
- [ ] **Frontend**: Real-time stats display

### Phase 6: Trace Mode (1 hour) - STRETCH GOAL
- [ ] **Frontend**: `TracingCanvas.tsx` - text input
- [ ] **Frontend**: Render text at 50% opacity
- [ ] **Backend**: Calculate tracing accuracy
- [ ] **Frontend**: Show accuracy percentage

### Phase 7: Polish (30 min)
- [ ] Add `CoachingSummary.tsx` with tips
- [ ] Improve styling
- [ ] Test full flow
- [ ] Demo prep

---

## 🔌 Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND                               │
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │   Camera    │───▶│ CameraTracker│───▶│  Canvas Overlay  │   │
│  │ getUserMedia│    │  Component   │    │  (trail, marker) │   │
│  └─────────────┘    └──────┬───────┘    └──────────────────┘   │
│                            │                                    │
│                     Base64 Frame                                │
│                            │                                    │
│                            ▼                                    │
│                   ┌────────────────┐                            │
│                   │  useWebSocket  │                            │
│                   │     Hook       │                            │
│                   └────────┬───────┘                            │
└────────────────────────────┼────────────────────────────────────┘
                             │
                      WebSocket Connection
                             │
┌────────────────────────────┼────────────────────────────────────┐
│                            ▼                        BACKEND     │
│                   ┌────────────────┐                            │
│                   │   WebSocket    │                            │
│                   │   Endpoint     │                            │
│                   └────────┬───────┘                            │
│                            │                                    │
│         ┌──────────────────┼──────────────────┐                 │
│         ▼                  ▼                  ▼                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │  tracking.py│   │ stability.py│   │ feedback.py │           │
│  │   OpenCV    │──▶│   Jitter    │──▶│  Messages   │           │
│  │ Color Track │   │   Calc      │   │  Generator  │           │
│  └─────────────┘   └─────────────┘   └─────────────┘           │
│                            │                                    │
│                            ▼                                    │
│              { position, stability, feedback }                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Key Dependencies

### Frontend
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.312.0",
    "recharts": "^2.10.4"
  },
  "devDependencies": {
    "typescript": "^5.3.3",
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18",
    "@vitejs/plugin-react": "^4.2.1",
    "tailwindcss": "^3.4.1",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.33",
    "vite": "^5.0.12"
  }
}
```

### Backend
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
websockets==12.0
opencv-python-headless==4.9.0.80
numpy==1.26.3
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
```

---

## 🚀 MVP Priority Order

1. ✅ Docker setup working
2. ✅ Camera feed displaying
3. ✅ LED color tracking (position detected)
4. ✅ Stability score calculating
5. ✅ Visual feedback indicator
6. ⭐ Practice mode working end-to-end
7. ⭐ Learn mode with targets
8. 💫 Trace mode (stretch goal)

---

## 🔜 Next Steps

Ready to generate all code files:
1. Docker configuration files
2. All backend Python files  
3. All frontend TypeScript files
4. Run `docker-compose up --build` and it works!

---

## ❓ Quick Questions (Optional)

1. **LED Color** - What color LED are you using? (Red is default/easiest)
2. **Arduino** - Using it or skipping? (Affects serial communication setup)
3. **Time Left** - Rough hours remaining? (Helps prioritize features)
