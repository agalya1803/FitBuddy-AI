from app.config import WORKOUT_MODEL
from app.ai.gemini_client import generate_text

def generate_workout_gemini(
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str
) -> str:

    prompt = f"""
Create a safe and practical 7-day fitness plan.

User details:

Name: {name}
Age: {age}
Weight: {weight} kg
Fitness goal: {goal}
Workout intensity: {intensity}

Create exactly 7 labelled days.

For each day include:

- Focus
- Warm-up
- Main workout
- Exercise names
- Sets and repetitions or duration
- Rest period
- Cool-down or recovery

Include rest or active recovery where suitable.

The plan should be realistic for a general adult user.

Do not diagnose medical conditions.
Do not prescribe medical treatment.
Do not make extreme exercise or diet claims.

Start with a short safety note.

Use simple and clear English.
"""

    return generate_text(
        WORKOUT_MODEL,
        prompt
    )