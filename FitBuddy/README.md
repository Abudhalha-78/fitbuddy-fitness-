# FitBuddy

A beginner-friendly AI fitness planner built with FastAPI, Jinja2, SQLite/SQLAlchemy, and optional Google Gemini integration.

## Features
- User profile and fitness goals
- AI-assisted workout plan generation
- Nutrition and recovery suggestions
- Feedback-based plan updates
- SQLite persistence
- REST API
- Responsive web UI
- Demo mode when no Gemini key is configured
- Basic automated tests

## Requirements
- Python 3.11+
- Optional: Google Gemini API key

## Setup — Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

## Troubleshooting

The project uses the current Starlette/Jinja template API (`request=`, `name=`, `context=`) and includes `python-multipart` for HTML form submissions.

## Test

```powershell
pytest -q
```

## Gemini configuration

Create a NEW API key and put it only in `.env`:

```env
GOOGLE_API_KEY=your_new_key_here
```

Never commit `.env`.

If no key is configured, FitBuddy automatically uses deterministic demo recommendations.

## API
- GET `/api/health`
- POST `/api/profile`
- POST `/api/plan`
- POST `/api/feedback`
- GET `/api/profile/{user_id}`
- GET `/api/plan/{user_id}`
