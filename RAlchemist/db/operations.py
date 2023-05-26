from datetime import datetime
from sqlalchemy import Connection, select, insert, Result, delete, update, Select, or_
from RAlchemist.schemas.recipe import (
    Recipe,
    BaseRecipe,
    RecipeInDB,
    Ingredient,
    JoinedRecipeRecord,
)
from RAlchemist.db.setup import get_db_conn, recipes_table, ingredients_table
from RAlchemist.db.sql_operations import (
    insert_recipe,
    select_ingredients_by_recipe_id,
    select_recipes,
    update_recipe_entry,
    delete_recipe_by_id,
    delete_ingredients_of_recipe,
    insert_ingredients,
    select_recipe_by_id,
    select_recipe_by_id_with_ingredients,
    select_recipe_ids_by_ingredients,
    select_recipes_by_ids,
    select_joined_recipes_matching_query,
)


def create_recipe(new_recipe: BaseRecipe, conn: Connection) -> Recipe:
    """Creates and stores a new recipe in the datastore."""
    new_pk = insert_recipe(new_recipe=new_recipe, conn=conn)
    insert_ingredients(ingredients=new_recipe.ingredients, recipe_id=new_pk, conn=conn)
    conn.commit()
    recipe_in_db = select_recipe_by_id(id=new_pk, conn=conn)
    if recipe_in_db is None:
        raise Exception(
            "This should never be an error except for some unforeseen race condition"
        )
    ingredient_list = select_ingredients_by_recipe_id(recipe_id=new_pk, conn=conn)
    recipe_in_db.ingredients = ingredient_list
    recipe = Recipe(**recipe_in_db.dict())
    return recipe


def read_recipe_by_id(id: int, conn: Connection) -> Recipe | None:
    """Fetches a stored recipe from the datastore.

    If there is no matching entity in the datastore, returns None
    """
    recipe = select_recipe_by_id_with_ingredients(recipe_id=id, conn=conn)
    if recipe is None:
        return None
    return recipe


def read_recipes_matching_query(
    conn: Connection,
    name: str | None,
    author: str | None,
    ingredients: list[str] | None,
):
    full_recipe_list: list[RecipeInDB] = []
    qualifying_recipe_ids = select_recipe_ids_by_ingredients(
        conn=conn, ingred_names=ingredients
    )
    qualifying_recipes = select_recipes(conn=conn, name=name, author=author)
    if qualifying_recipes is None and qualifying_recipe_ids is None:
        return None
    elif qualifying_recipes is not None and qualifying_recipe_ids is None:
        full_recipe_list = qualifying_recipes
    elif qualifying_recipes is None and qualifying_recipe_ids is not None:
        resp = select_recipes_by_ids(conn=conn, recipe_ids=list(qualifying_recipe_ids))
        if resp is not None:
            full_recipe_list = resp
    elif qualifying_recipes is not None and qualifying_recipe_ids is not None:
        newly_identified_ids = []
        recipe_dict = {x.recipe_id: x for x in qualifying_recipes}
        for id in qualifying_recipe_ids:
            if id not in recipe_dict:
                newly_identified_ids.append(id)

        if len(newly_identified_ids) > 0:
            resp = select_recipes_by_ids(conn=conn, recipe_ids=newly_identified_ids)
            if resp is not None:
                full_recipe_list = qualifying_recipes + resp
        else:
            full_recipe_list = qualifying_recipes

    recipes: list[Recipe] = []
    for partial_recipe in full_recipe_list:
        partial_recipe.ingredients = select_ingredients_by_recipe_id(
            recipe_id=partial_recipe.recipe_id, conn=conn
        )
        recipes.append(Recipe(**partial_recipe.dict()))
    return recipes


def update_recipe(recipe: Recipe, conn: Connection) -> Recipe:
    """Updates a stored recipe and returns it."""
    recipe_in_db = select_recipe_by_id(id=recipe.recipe_id, conn=conn)
    if recipe_in_db is None:
        raise Exception(
            "Recipe does not exist in database and as such cannot be updated"
        )
    update_recipe_entry(recipe=recipe, conn=conn)
    delete_ingredients_of_recipe(recipe_id=recipe.recipe_id, conn=conn)
    insert_ingredients(
        recipe_id=recipe.recipe_id, ingredients=recipe.ingredients, conn=conn
    )
    conn.commit()
    recipe_in_db = select_recipe_by_id(id=recipe.recipe_id, conn=conn)
    if recipe_in_db is None:
        raise Exception(
            "This should never be an error except for some unforeseen race condition"
        )
    ingredient_list = select_ingredients_by_recipe_id(
        recipe_id=recipe.recipe_id, conn=conn
    )
    recipe_in_db.ingredients = ingredient_list
    recipe = Recipe(**recipe_in_db.dict())
    return recipe


def delete_recipe(recipe_id: int, conn: Connection):
    """Removes recipe from datastore"""
    delete_recipe_by_id(recipe_id=recipe_id, conn=conn)
    conn.commit()


def read_recipes(conn: Connection):
    joined_recipe_records = select_joined_recipes_matching_query(
        conn=conn, name=None, author=None, ingredients=None
    )
    if joined_recipe_records is None:
        return None
    return _combine_joined_recipe_records(joined_recipe_records)


def _combine_joined_recipe_records(
    joined_records: list[JoinedRecipeRecord],
) -> list[Recipe]:
    recipes_dict: dict[int, Recipe] = {}
    for r in joined_records:
        if r.recipe_id in recipes_dict:
            recipes_dict[r.recipe_id].ingredients.append(
                Ingredient(
                    ingred_name=r.ingred_name,
                    amount=r.amount,
                    unit=r.unit,
                    notes=r.notes,
                    group=r.group,
                )
            )
        elif r.recipe_id not in recipes_dict:
            r.ingredients = []
            r.ingredients.append(
                Ingredient(
                    ingred_name=r.ingred_name,
                    amount=r.amount,
                    unit=r.unit,
                    notes=r.notes,
                    group=r.group,
                )
            )
            recipe = Recipe(
                **r.dict(exclude={"ingred_name", "amount", "unit", "notes", "group"})
            )
            recipes_dict[r.recipe_id] = recipe

    recipes = [value for value in recipes_dict.values()]
    return recipes
