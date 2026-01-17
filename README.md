# Tremor Tracker

Real-time hand stability tracking application using computer vision. Track pen movements via webcam and receive visual feedback on hand steadiness.

## How It Works

- **Colored Pen Top**: OpenCV tracks a colored marker on the pen tip
- **Side LEDs**: Physical LEDs on the pen provide real-time feedback (red = jittering, green = stable)

## Tech Stack

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: Python + FastAPI + OpenCV
- **Infrastructure**: Docker Compose

## Quick Start

1. Copy environment file:
   ```bash
   cp .env.example .env
   ```

2. Build and run with Docker:
   ```bash
   docker-compose up --build
   ```

3. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Development

### Frontend Only
```bash
cd frontend
npm install
npm run dev
```

### Backend Only
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Configuration

Edit `.env` to configure:
- `PEN_COLOR`: Color of pen marker (red, green, blue)
- `STABILITY_WINDOW_SIZE`: Number of frames for stability calculation
- `JITTER_THRESHOLD_LOW/HIGH`: Sensitivity thresholds

## Project Structure

```
tremor-tracker/
├── frontend/          # React + Vite application
├── backend/           # FastAPI + OpenCV server
├── docker-compose.yml # Container orchestration
└── .env.example       # Environment template
```
