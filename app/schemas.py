from pydantic import BaseModel, Field, field_validator

class UserInput(BaseModel):
    user_id: str = Field(
        min_length=2,
        max_length=50
    )

    name: str = Field(
        min_length=2,
        max_length=100
    )

    age: int = Field(
        ge=13,
        le=100
    )

    weight: float = Field(
        gt=20,
        le=400
    )

    goal: str

    intensity: str

    @field_validator("goal")
    @classmethod
    def validate_goal(cls, value):
        value = value.strip().lower()

        allowed = {
            "weight loss",
            "muscle gain",
            "general wellness",
            "flexibility"
        }

        if value not in allowed:
            raise ValueError(
                "Invalid fitness goal"
            )

        return value

    @field_validator("intensity")
    @classmethod
    def validate_intensity(cls, value):
        value = value.strip().lower()

        allowed = {
            "low",
            "medium",
            "high"
        }

        if value not in allowed:
            raise ValueError(
                "Intensity must be low, medium, or high"
            )

        return value

class FeedbackRequest(BaseModel):
    user_id: str = Field(
        min_length=2,
        max_length=50
    )

    feedback: str = Field(
        min_length=3,
        max_length=2000
    )