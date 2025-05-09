# main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models import BuffetItem, Recommendation
from app.schemas import UserInput, RecommendationResponse
from app.ai import generate_recommendation
from app.crud import get_buffet_items_by_meal
from app.crud import save_recommendation
from dotenv import load_dotenv, find_dotenv
import os
load_dotenv()

print("DEBUG DATABASE_URL =", os.getenv("DATABASE_URL"))  

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/recommendations/", response_model=RecommendationResponse)
def recommend_food(user_input: UserInput, db: Session = Depends(get_db)):
    buffet_items = get_buffet_items_by_meal(db, user_input.meal_type)
    if not buffet_items:
        raise HTTPException(status_code=404, detail="No buffet items available for this meal type.")

    ai_response = generate_recommendation(user_input, buffet_items)
    rec = save_recommendation(db, user_input, ai_response)
    return rec
