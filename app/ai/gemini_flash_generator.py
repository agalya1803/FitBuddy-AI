from app.config import NUTRITION_MODEL
from app.ai.gemini_client import generate_text

def generate_nutrition_tip_with_flash(
    goal: str
) -> str:

    prompt = f"""
Give one simple and practical nutrition or recovery tip
for a person whose fitness goal is:

{goal}

Use simple English.

Do not give medical advice.
Do not recommend extreme calorie restriction.
Do not prescribe supplements.

Keep the answer between 3 and 5 sentences.
"""

    return generate_text(
        NUTRITION_MODEL,
        prompt
    )