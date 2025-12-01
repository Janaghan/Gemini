from pydantic import BaseModel, Field
from typing import List, Optional
from google import genai
from google.genai import types
import io
import httpx
from dotenv import load_dotenv
import os
from lmnr import Laminar, observe

load_dotenv()
Laminar.initialize(project_api_key=os.environ.get("laminar_api_key"))
client = genai.Client(api_key=os.environ.get("gemini_api_key"))

@observe()
def structured_output():
    class Ingredient(BaseModel):
        name: str = Field(description="Name of the ingredient.")
        quantity: str = Field(description="Quantity of the ingredient, including units.")
    
    class Recipe(BaseModel):
        recipe_name: str = Field(description="The name of the recipe.")
        prep_time_minutes: Optional[int] = Field(description="Optional time in minutes to prepare the recipe.")
        ingredients: List[Ingredient]
        instructions: List[str]

    prompt = """
     Please extract the recipe from the following text.
    The user wants to make a classic Margherita Pizza.
    For the dough, they need 2 cups of all-purpose flour, 1 teaspoon of instant yeast,
    1 teaspoon of sugar, 3/4 cup of warm water, 1 tablespoon of olive oil, and 1 teaspoon of salt.
    For the topping, they'll need 1/2 cup of tomato sauce, 8 ounces of fresh mozzarella cheese (sliced),
    and a handful of fresh basil leaves.
    First, mix the flour, yeast, sugar, and salt in a bowl. Add water and oil, and knead until smooth.
    Let it rise for 1 hour. Preheat oven to 475°F (245°C). Roll out the dough. Spread tomato sauce over it.
    Top with mozzarella slices. Bake for 10-12 minutes until crust is golden. Garnish with fresh basil.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt],
        config={
            "response_mime_type": "application/json",
            "response_json_schema": Recipe.model_json_schema(),
        },
    )

    recipe = Recipe.model_validate_json(response.text)
    print(recipe)

structured_output()
