import httpx
import os
import json
from app.schemas import UserInput
from openai import OpenAI
from app.models import BuffetItem
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """
You are an AI-powered dietary assistant embedded in the recommendation engine of a five-star hotel buffet system. Your purpose is to provide **nutritionally sound, personalized meal recommendations** to guests based on their health goals, dietary preferences, allergies, and other constraints.

The buffet includes a wide variety of high-quality international and local dishes, and the AI's role is to curate a selection that is both safe and optimized for the guest's goals and health conditions.

You will be provided:
1. Detailed guest input (age, gender, dietary goal, health conditions, spice preference, allergies, etc.)
2. A list of available buffet items for a given meal (breakfast, lunch, or dinner)

Your response must adhere strictly to valid raw JSON — no markdown, no LaTeX, no commentary outside the JSON.

### Return Format:
{{
  "items": [
    {{
      "name": "string",
      "serving_size": "string",
      "dietary_quality_score": integer,
      "explanation": "string",
      "additional_suggestion": "string (optional)"
    }}
  ],
  "description": "string"
}}

IMPORTANT:
- The response must begin with '{' and end with '}'.
- DO NOT include bullet points, markdown, or extra text.
- Only return a valid JSON object.

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

    output = completion.choices[0].message.content.strip()

    # Clean \boxed{...} if it exists
    if output.startswith("\\boxed{") and output.endswith("}"):
        output = output[len("\\boxed{"):-1].strip()

    # Ensure output starts with "{" and ends with "}"
    if not output.startswith("{"):
        output = "{" + output
    if not output.endswith("}"):
        output = output + "}"

    try:
        return json.loads(output)
    except json.JSONDecodeError:
        print("❌ JSON parse failed. Raw output was:\n", output)
        return {
            "items": formatted_items[:3],
            "description": "AI fallback: recommended top 3 items based on general balance."
        }
