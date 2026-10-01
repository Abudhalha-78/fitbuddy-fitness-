from pathlib import Path
import json

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db, init_db
from .models import Feedback, FitnessPlan, UserProfile
from .schemas import FeedbackCreate, PlanRequest, ProfileCreate
from .services.ai import generate_plan

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title=settings.app_name, version="1.0.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request})

@app.get("/dashboard/{user_id}", response_class=HTMLResponse)
def dashboard(request: Request, user_id: int, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    plan = db.query(FitnessPlan).filter_by(user_id=user_id).order_by(FitnessPlan.id.desc()).first()
    plan_data = json.loads(plan.content) if plan else None
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"request": request, "profile": profile, "plan": plan_data},
    )

@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}

@app.post("/api/profile")
def create_profile(payload: ProfileCreate, db: Session = Depends(get_db)):
    profile = UserProfile(**payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return {"id": profile.id, "message": "Profile created"}

@app.get("/api/profile/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": profile.id, "name": profile.name, "age": profile.age,
        "goal": profile.goal, "fitness_level": profile.fitness_level,
        "days_per_week": profile.days_per_week, "equipment": profile.equipment,
    }

@app.post("/api/plan")
def create_plan(payload: PlanRequest, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, payload.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")

    profile_dict = {
        "name": profile.name, "age": profile.age, "goal": profile.goal,
        "fitness_level": profile.fitness_level,
        "days_per_week": profile.days_per_week,
        "equipment": profile.equipment,
    }
    plan = generate_plan(profile_dict)
    record = FitnessPlan(user_id=profile.id, content=json.dumps(plan))
    db.add(record)
    db.commit()
    return {"user_id": profile.id, "plan": plan}

@app.get("/api/plan/{user_id}")
def get_plan(user_id: int, db: Session = Depends(get_db)):
    if not db.get(UserProfile, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    record = db.query(FitnessPlan).filter_by(user_id=user_id).order_by(FitnessPlan.id.desc()).first()
    if not record:
        raise HTTPException(status_code=404, detail="No plan found")
    return {"user_id": user_id, "plan": json.loads(record.content)}

@app.post("/api/feedback")
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    if not db.get(UserProfile, payload.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    item = Feedback(user_id=payload.user_id, message=payload.message)
    db.add(item)
    db.commit()
    return {"message": "Feedback saved"}

@app.post("/create-profile")
async def create_profile_form(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    try:
        payload = ProfileCreate(
            name=form.get("name", ""),
            age=int(form.get("age", 0)),
            goal=form.get("goal", ""),
            fitness_level=form.get("fitness_level", ""),
            days_per_week=int(form.get("days_per_week", 3)),
            equipment=form.get("equipment", "None"),
        )
    except Exception:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"request": request, "error": "Please enter valid profile details."},
            status_code=400,
        )
    profile = UserProfile(**payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return RedirectResponse(url=f"/dashboard/{profile.id}", status_code=303)
