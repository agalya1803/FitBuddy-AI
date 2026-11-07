from app.config import WORKOUT_MODEL
from app.ai.gemini_client import generate_text

def update_workout_plan(
    original_plan: str,
    feedback: str,
    goal: str,
    intensity: str
) -> str:

    prompt = f"""
Revise the workout plan using the user's feedback.

Fitness goal:
{goal}

Workout intensity:
{intensity}

User feedback:
{feedback}

Original workout plan:
{original_plan}

Return a complete revised 7-day workout plan.

Do not return only the changed days.

Keep useful parts of the original plan.

Apply the user's feedback where reasonable.

Keep the plan safe and realistic.

Do not diagnose medical conditions.
Do not prescribe medical treatment.

Use simple and clear English.
"""

    return generate_text(
        WORKOUT_MODEL,
        prompt
    )