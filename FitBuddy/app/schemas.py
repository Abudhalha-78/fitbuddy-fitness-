from pydantic import BaseModel, Field

class ProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=13, le=120)
    goal: str = Field(min_length=1, max_length=100)
    fitness_level: str = Field(min_length=1, max_length=50)
    days_per_week: int = Field(ge=1, le=7)
    equipment: str = Field(default="None", max_length=200)

class PlanRequest(BaseModel):
    user_id: int

class FeedbackCreate(BaseModel):
    user_id: int
    message: str = Field(min_length=1, max_length=2000)
