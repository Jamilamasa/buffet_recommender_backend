import httpx
import os
import json
from app.schemas import UserInput
from openai import OpenAI
from app.models import BuffetItem
from dotenv import load_dotenv, find_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """
You are an AI-powered dietary assistant embedded in the recommendation engine of a five-star hotel buffet system. Your purpose is to provide **nutritionally sound, personalized meal recommendations** to guests based on their health goals, dietary preferences, allergies, and other constraints.

The buffet includes a wide variety of high-quality international and local dishes, and the AI's role is to curate a selection that is both safe and optimized for the guest's goals and health conditions.

You will be provided:
1. Detailed guest input (age, gender, dietary goal, health conditions, spice preference, allergies, etc.)
2. A list of available buffet items for a given meal (breakfast, lunch, or dinner)

Your response must adhere **strictly** to valid **raw JSON** — no markdown, no LaTeX, no commentary outside the JSON. You are expected to act as a backend system returning a payload to a UI.

### Return Format:

{{
  "items": [
    {{
      "name": "string",  // name of the recommended buffet item
      "serving_size": "string",  // e.g. '1 cup', '200g', '2 slices'
      "dietary_quality_score": integer (1-10),  // nutritional score (higher is better)
      "explanation": "string",  // why this item is suitable for this guest
      "additional_suggestion": "string (optional)"  // optional tip to enhance or adjust the meal
    }}
  ],
  "description": "string"  // overall explanation of how this selection meets the guest's needs
}}
Important: Your response must begin with \"{{\" and end with \"}}\" must be valid JSON with no leading or trailing characters.
DO NOT include:
- Bullet points
- Markdown formatting
- Any text outside the JSON

Consider:
- Medical safety (e.g. allergies, malaria recovery)
- Caloric needs (e.g. fat loss, muscle gain)
- Taste preferences (e.g. spice level, cuisine bias)
- Cultural sensitivity (avoid suggesting pork for guests with halal preferences, etc.)

Be concise, accurate, and professional. Personalize the tone of the explanations to sound helpful and expert, not robotic.

User Input:
{user_input}

Available Buffet Items for {meal_type}:
{buffet_items}
"""


def generate_recommendation(user_input: UserInput, buffet_items: list[BuffetItem]) -> dict:
    formatted_items = [
        {"name": item.name, "ingredients": item.ingredients} for item in buffet_items
    ]

    prompt = SYSTEM_PROMPT.format(
        user_input=user_input.dict(),
        meal_type=user_input.meal_type,
        buffet_items=formatted_items
    )

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    completion = client.chat.completions.create(
        model="deepseek/deepseek-r1-zero:free",
        messages=[
            {"role": "system", "content": "You are a helpful nutrition assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    output = completion.choices[0].message.content

   # Clean LaTeX-style wrapping like \boxed{...}
    if output.startswith("\\boxed{") and output.endswith("}"):
        output = output[len("\\boxed{"):-1].strip()
        print("AI RESPONSE:\n", output)

    try:
        return json.loads(output)
    except json.JSONDecodeError:
        print("JSON parse failed. Raw output was:", output)
        return {
            "items": formatted_items[:3],
            "description": "AI fallback: recommended top 3 items based on general balance."
        }
