from sqlalchemy import Connection
from magicoffastapi.schemas.recipe import Recipe, Ingredient
from magicoffastapi.db.sql_operations import (
    select_recipe_ids_by_ingredients,
    select_recipes_by_ids,
    select_recipes_with_ingredients_by_ids,
)


class RecipeFinder:
    def __init__(
        self,
        conn: Connection,
        ingred_amount_is_factor: bool = False,
        prefer_popular_recipes: bool = True,
    ):
        self.conn = conn
        self.ingred_amount_is_factor = ingred_amount_is_factor
        self.prefer_popular_recipes = prefer_popular_recipes

    def find(
        self, planned_recipes: list[Recipe], provided_ingredients: list[Ingredient]
    ):
        # obtain full id list of  possible recipes
        ingred_names = [x.ingred_name for x in provided_ingredients]
        planned_recipe_ids = [x.recipe_id for x in planned_recipes]
        retrieved_recipe_ids = select_recipe_ids_by_ingredients(
            conn=self.conn, ingred_names=ingred_names
        )
        # filter out recipe_ids already in the plan
        de_duplicated_id_set = set()
        if retrieved_recipe_ids is None:
            return None
        for recipe_id in retrieved_recipe_ids:
            if recipe_id in planned_recipe_ids:
                pass
            else:
                de_duplicated_id_set.add(recipe_id)

        max_score = len(provided_ingredients)

        joined_records = select_recipes_with_ingredients_by_ids(
            conn=self.conn, recipe_ids=list(de_duplicated_id_set)
        )
        if joined_records is None:
            raise Exception("No recipes were returned but they should have been.")
        recipes = {}
        for record in joined_records:
            if record.recipe_id in recipes:
                recipes[record.recipe_id].ingredients.append(
                    Ingredient(
                        ingred_name=record.ingred_name,
                        amount=record.amount,
                        unit=record.unit,
                    )
                )
            elif record.recipe_id not in recipes:
                record.ingredients = [
                    Ingredient(
                        ingred_name=record.ingred_name,
                        amount=record.amount,
                        unit=record.unit,
                    )
                ]
                recipe = Recipe(
                    **record.dict(exclude={"ingred_name", "amount", "unit"})
                )
                recipes[record.recipe_id] = recipe

        print(recipes)
        recipes = recipes.values()
        print(recipes)
