from app.config import GEMINI_API_KEY

_client = None

def get_client():
    global _client

    if _client is not None:
        return _client

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "google-genai is not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc

    _client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    return _client

def generate_text(
    model: str,
    prompt: str
) -> str:
    client = get_client()

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    text = getattr(
        response,
        "text",
        None
    )

    if not text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return text.strip()