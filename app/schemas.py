from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
import uuid

class UserInput(BaseModel):
    age: int
    gender: Literal["male", "female", "other"]
    primary_dietary_goal: str
    health_conditions: List[str]
    allergies: List[str]
    dietary_preferences: List[str]
    spice_preference: int = Field(ge=0, le=100)
    additional_info: Optional[str] = None
    meal_type: Literal["breakfast", "lunch", "dinner"]

class RecommendationResponse(BaseModel):
    id: uuid.UUID
    user_input: dict
    meal_type: str
    recommended_items: List[dict]
    description: str
    timestamp: datetime
