from sqlalchemy.orm import Session
from app.models import BuffetItem, Recommendation
from app.schemas import UserInput
from uuid import uuid4

def get_buffet_items_by_meal(db: Session, meal_type: str):
    return db.query(BuffetItem).filter(BuffetItem.meal_type == meal_type).all()

def save_recommendation(db: Session, user_input: UserInput, ai_response: dict):
    rec = Recommendation(
        id=uuid4(),
        user_input=user_input.dict(),
        meal_type=user_input.meal_type,
        recommended_items=ai_response["items"],
        description=ai_response["description"]
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec