import json
from typing import Any
from ..config import settings

def demo_plan(profile: dict[str, Any]) -> dict[str, Any]:
    level = profile["fitness_level"].lower()
    days = profile["days_per_week"]
    equipment = profile["equipment"]

    if level == "beginner":
        exercises = ["Bodyweight Squat", "Wall/Incline Push-up", "Glute Bridge", "Bird Dog"]
    elif level == "intermediate":
        exercises = ["Squat", "Push-up", "Reverse Lunge", "Row variation"]
    else:
        exercises = ["Squat variation", "Push-up variation", "Lunge variation", "Row variation"]

    focuses = ["Full Body", "Lower Body", "Upper Body", "Conditioning", "Full Body", "Mobility", "Recovery"]

    return {
        "mode": "demo",
        "summary": f"A {days}-day plan focused on {profile['goal']} for a {level} level.",
        "equipment": equipment,
        "workouts": [
            {
                "day": f"Day {i}",
                "focus": focuses[i - 1],
                "exercises": exercises,
                "note": "Use controlled form, start comfortably, and stop if you feel pain or unwell."
            }
            for i in range(1, days + 1)
        ],
        "nutrition": [
            "Build meals around varied whole foods and adequate protein.",
            "Drink water regularly throughout the day.",
            "Avoid extreme dieting; adjust food intake to your needs and activity."
        ],
        "recovery": [
            "Prioritize regular sleep.",
            "Include rest or light-activity days.",
            "Increase training gradually rather than making sudden jumps."
        ]
    }

def generate_plan(profile: dict[str, Any]) -> dict[str, Any]:
    if not settings.google_api_key:
        return demo_plan(profile)

    try:
        from google import genai
        client = genai.Client(api_key=settings.google_api_key)
        prompt = f'''
Create a safe, general fitness plan as JSON for this profile:
{json.dumps(profile)}

Return JSON with keys:
summary, equipment, workouts, nutrition, recovery.
workouts must be a list of objects with day, focus, exercises, note.
Do not provide medical diagnosis, extreme dieting, or unsafe instructions.
'''
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        data["mode"] = "gemini"
        return data
    except Exception:
        fallback = demo_plan(profile)
        fallback["mode"] = "fallback"
        return fallback
