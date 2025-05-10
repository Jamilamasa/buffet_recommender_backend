from sqlalchemy import Column, String, Integer, Text, Enum, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import enum
import uuid
from app.database import Base

class MealType(str, enum.Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"

class BuffetItem(Base):
    __tablename__ = "buffet_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    ingredients = Column(ARRAY(String))
    meal_type = Column(Enum(MealType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_input = Column(JSON, nullable=False)
    meal_type = Column(Enum(MealType), nullable=False)
    recommended_items = Column(JSON, nullable=False)
    description = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())