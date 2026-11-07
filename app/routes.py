from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import (
    get_db,
    save_user,
    get_user,
    get_all_users,
    save_plan,
    get_original_plan,
    update_plan,
    delete_user
)
from app.schemas import UserInput, FeedbackRequest
from app.ai.gemini_generator import generate_workout_gemini
from app.ai.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.ai.updated_plan import update_workout_plan

router = APIRouter()

def render_template(request, filename, **context):
    from app.main import templates
    return templates.TemplateResponse(
        request=request,
        name=filename,
        context=context
    )

def demo_workout(user):
    return f"""Safety note: This is general fitness information. Stop if you feel pain and seek professional advice when needed.

Day 1 - Full Body
Warm-up: 5-10 minutes brisk walking and mobility.
Main workout: Squats 3x10, Push-ups 3x8, Glute bridges 3x12, Plank 3x30 seconds. Rest 60-90 seconds.
Cool-down: 5 minutes easy walking and stretching.

Day 2 - Cardio
Warm-up: 5 minutes easy movement.
Main workout: 25 minutes brisk walking, cycling, or another comfortable cardio activity.
Cool-down: 5 minutes easy movement.

Day 3 - Upper Body
Warm-up: 5-10 minutes.
Main workout: Incline push-ups 3x10, Rows 3x10, Shoulder press 3x10, Dead bug 3x10 each side.
Cool-down: Gentle stretching.

Day 4 - Active Recovery
20-30 minutes easy walking plus light mobility.

Day 5 - Lower Body
Warm-up: 5-10 minutes.
Main workout: Squats 3x10, Reverse lunges 3x8 each leg, Glute bridges 3x12, Calf raises 3x15.
Cool-down: Gentle stretching.

Day 6 - Cardio + Core
Warm-up: 5 minutes.
Main workout: 20 minutes moderate cardio, then bird-dog 3x10 each side and plank 3x30 seconds.
Cool-down: 5 minutes.

Day 7 - Rest
Rest, easy walking if comfortable, hydration, and recovery."""

def demo_tip(goal):
    tips = {
        "muscle gain":
        "Include a protein-rich food in each main meal, such as eggs, fish, chicken, beans, lentils, or yoghurt. Also keep regular meals and adequate hydration.",
        "weight loss":
        "Build meals around vegetables, a protein source, whole grains or other high-fibre foods, and water. Consistent habits are more useful than extreme restriction.",
        "flexibility":
        "Include fruit and vegetables, adequate fluids, and regular balanced meals. Recovery and sleep also support consistent training.",
        "general wellness":
        "Aim for balanced meals with vegetables, fruit, a protein source, whole grains, and enough water. Regular meals and good sleep can support an active routine."
    }
    return tips.get(goal, tips["general wellness"])

def ai_or_demo(generator, fallback):
    try:
        return generator()
    except Exception as exc:
        print("AI ERROR:", exc)
        return fallback

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return render_template(request, "index.html")

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        data = UserInput(
            user_id=user_id,
            name=name,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity
        )
    except Exception as exc:
        return render_template(request, "index.html", error=str(exc))

    existing = get_user(db, data.user_id)
    if existing:
        return render_template(
            request,
            "index.html",
            error="That User ID already exists. Use another ID."
        )

    workout = ai_or_demo(
        lambda: generate_workout_gemini(
            data.name,
            data.age,
            data.weight,
            data.goal,
            data.intensity
        ),
        demo_workout(data)
    )

    tip = ai_or_demo(
        lambda: generate_nutrition_tip_with_flash(data.goal),
        demo_tip(data.goal)
    )

    try:
        user = save_user(db, data.model_dump())
        plan = save_plan(db, user.id, workout, tip)
    except IntegrityError:
        db.rollback()
        return render_template(
            request,
            "index.html",
            error="Could not save the user. Please try a different User ID."
        )

    return render_template(
        request,
        "result.html",
        user=user,
        plan=plan,
        message=None,
        error=None
    )

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        request_data = FeedbackRequest(
            user_id=user_id,
            feedback=feedback
        )
    except Exception as exc:
        return render_template(request, "index.html", error=str(exc))

    user = get_user(db, request_data.user_id)
    if not user:
        return render_template(
            request,
            "index.html",
            error="User ID was not found."
        )

    plan = get_original_plan(db, user.id)
    if not plan:
        return render_template(
            request,
            "index.html",
            error="No workout plan was found for this user."
        )

    revised = ai_or_demo(
        lambda: update_workout_plan(
            plan.original_plan,
            request_data.feedback,
            user.goal,
            user.intensity
        ),
        plan.original_plan +
        "\n\nUpdated using demo feedback: " +
        request_data.feedback
    )

    updated_tip = ai_or_demo(
        lambda: generate_nutrition_tip_with_flash(user.goal),
        plan.nutrition_tip
    )

    update_plan(db, plan, revised, updated_tip)

    return render_template(
        request,
        "result.html",
        user=user,
        plan=plan,
        message="Your workout plan has been updated.",
        error=None
    )

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = get_all_users(db)
    for user in users:
        user.plan = get_original_plan(db, user.id)
    return render_template(
        request,
        "all_users.html",
        users=users
    )

@router.post("/delete-user/{user_id}")
def remove_user(user_id: str, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if user:
        delete_user(db, user)
    return RedirectResponse(
        url="/view-all-users",
        status_code=303
    )

@router.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "FitBuddy"
    }

@router.get("/api/users")
def api_users(db: Session = Depends(get_db)):
    users = get_all_users(db)
    return [
        {
            "user_id": user.user_id,
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "created_at": user.created_at.isoformat()
        }
        for user in users
    ]

@router.get("/api/users/{user_id}")
def api_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    user = get_user(db, user_id)

    if not user:
        return JSONResponse(
            {"detail": "User not found"},
            status_code=404
        )

    plan = get_original_plan(db, user.id)

    return {
        "user": {
            "user_id": user.user_id,
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity
        },
        "plan": {
            "original_plan": plan.original_plan if plan else None,
            "updated_plan": plan.updated_plan if plan else None,
            "nutrition_tip": plan.nutrition_tip if plan else None
        }
    }