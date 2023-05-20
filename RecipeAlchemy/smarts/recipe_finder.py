from sqlalchemy import Connection
from RecipeAlchemy.schemas.recipe import Recipe, Ingredient, ScoredRecipe
from RecipeAlchemy.db.sql_operations import (
    select_joined_recipes_matching_query,
)
from RecipeAlchemy.db.operations import _combine_joined_recipe_records


class RecipeFinder:
    def __init__(
        self,
        conn: Connection,
        # ingred_amount_is_factor: bool = False,
        # prefer_popular_recipes: bool = True,
        # prefer_different_cuisine: bool = True,
    ):
        self.conn = conn
        # self.ingred_amount_is_factor = ingred_amount_is_factor
        # self.prefer_popular_recipes = prefer_popular_recipes
        # self.prefer_different_cuisine = prefer_different_cuisine

    def find(
        self, ingredients: set[str], exclude: set[int] | None
    ) -> list[ScoredRecipe]:
        """Provides a list of recipes that include at least one of the provided ingredients.

        Sorts the returned recipes from best match to worst match.

        Parameters:
        - `ingredients`: a list of ingredient names. At least one of these will be
         a constituent part of each recipe returned by this function.
        - `exclude`: a list of recipe IDs to exclude from the resulting recipes. Note
        that this function does not confirm these IDs are valid. It merely prevents
        any recipe with one of these IDs from being in the results.

        Returns:
        - `scored_recipes`: a list of recipes with scores, sorted by score
        """

        joined_records = select_joined_recipes_matching_query(
            conn=self.conn, name=None, author=None, ingredients=ingredients
        )
        if joined_records is None:
            raise Exception("No recipes were returned but they should have been.")

        if exclude is not None:
            joined_records = [y for y in joined_records if y.recipe_id not in exclude]

        recipes = _combine_joined_recipe_records(joined_records)
        max_score = len(ingredients)
        scored_recipes: list[ScoredRecipe] = []
        for recipe in recipes:
            unique_ingredients = {x.ingred_name for x in recipe.ingredients}
            score = 0
            for i in ingredients:
                for unique_ingredient in unique_ingredients:
                    if i in unique_ingredient:
                        score += 1
                        break
            scored_recipes.append(ScoredRecipe(score=score, recipe=recipe))
            if score > max_score:
                raise Exception("A recipe scored higher than the maximum.")

        scored_recipes.sort(key=lambda recipe: recipe.score, reverse=True)
        return scored_recipes
