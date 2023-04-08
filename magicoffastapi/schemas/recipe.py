from datetime import datetime
from pydantic import BaseModel


class Ingredient(BaseModel):
    ingred_name: str
    amount: float | None
    unit: str | None


class BaseRecipe(BaseModel):
    name: str
    author: str
    rating: int | None
    prep_time: float | None
    cook_time: float | None
    ingredients: list[Ingredient]
    instructions: str | None


class Recipe(BaseRecipe):
    recipe_id: int
    created_at: datetime
    modified_at: datetime
    ingredients: list[Ingredient]


class RecipeInDB(Recipe):
    ingredients: list[Ingredient] | None
