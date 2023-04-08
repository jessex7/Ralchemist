from datetime import datetime
from sqlalchemy import Connection, select, insert, Result, delete, update
from magicoffastapi.schemas.recipe import (
    Recipe,
    BaseRecipe,
    RecipeInDB,
    Ingredient,
    Ingredient,
)
from magicoffastapi.db.setup import get_db_conn, recipes_table, ingredients_table


# high-level (model) interactions
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
    recipe_in_db = select_recipe_by_id(id=id, conn=conn)
    if recipe_in_db is None:
        return None
    ingredient_list = select_ingredients_by_recipe_id(recipe_id=id, conn=conn)
    recipe_in_db.ingredients = ingredient_list
    recipe = Recipe(**recipe_in_db.dict())
    return recipe


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


# sql-specific (table) interactions
def insert_recipe(new_recipe: BaseRecipe, conn: Connection) -> int:
    """Basic naive wrapper for an INSERT to the recipe_table.

    This is a 'naive' function because
        1) it does no data validation. That must be done elsewhere.
        2) it does not 'commit' anything to the database. That must be done elsewhere
    """

    timestamp = datetime.now()
    result: Result = conn.execute(
        insert(recipes_table).values(
            name=new_recipe.name,
            author=new_recipe.author,
            rating=new_recipe.rating,
            prep_time=new_recipe.prep_time,
            cook_time=new_recipe.cook_time,
            created_at=timestamp,
            modified_at=timestamp,
            instructions=new_recipe.instructions,
        )
    )
    new_pk = result.inserted_primary_key
    if new_pk is None:
        raise Exception("This should never happen")
    else:
        return new_pk[0]


def insert_ingredients(ingredients: list[Ingredient], recipe_id: int, conn: Connection):
    """Basic naive wrapper for a group of INSERTs to the ingredient_table.

    This is a 'naive' function because
        1) it does no data validation. That must be done elsewhere.
        2) it does not 'commit' anything to the database. That must be done elsewhere
    """

    for ingred in ingredients:
        ingred_dict = ingred.dict()
        ingred_dict["recipe_id"] = recipe_id
        result: Result = conn.execute(
            insert(ingredients_table),
            [
                ingred_dict,
            ],
        )


def select_recipe_by_id(id: int, conn: Connection) -> RecipeInDB | None:
    """Basic wrapper for a SELECT from the recipe_table."""
    recipe_result: Result = conn.execute(
        select(
            recipes_table.c.recipe_id,
            recipes_table.c.name,
            recipes_table.c.author,
            recipes_table.c.rating,
            recipes_table.c.prep_time,
            recipes_table.c.cook_time,
            recipes_table.c.created_at,
            recipes_table.c.modified_at,
            recipes_table.c.instructions,
        ).where(recipes_table.c.recipe_id == id)
    )
    raw_recipe = recipe_result.first()
    if raw_recipe is None:
        return None
    raw_recipe_dict = raw_recipe._asdict()
    recipe = RecipeInDB(**raw_recipe_dict)
    return recipe


def select_ingredients_by_recipe_id(
    recipe_id: int, conn: Connection
) -> list[Ingredient]:
    """Basic wrapper for a group of SELECTs from the ingredients_table."""

    ingred_result: Result = conn.execute(
        select(
            ingredients_table.c.ingred_name,
            ingredients_table.c.amount,
            ingredients_table.c.unit,
        ).where(ingredients_table.c.recipe_id == recipe_id)
    )
    raw_ingredients = ingred_result.all()
    formatted_ingredients: list[Ingredient] = []
    for i in raw_ingredients:
        formatted_ingredients.append(Ingredient(**(i._asdict())))
    return formatted_ingredients


def update_recipe_entry(recipe: Recipe, conn: Connection):
    """Basic  naive wrapper for an UPDATE to the recipe_table.
    This is a 'naive' function because
        1) it does no data validation. That must be done elsewhere.
        2) it does not 'commit' anything to the database. That must be done elsewhere
    """
    recipe_result = conn.execute(
        update(recipes_table)
        .where(recipes_table.c.recipe_id == recipe.recipe_id)
        .values(
            recipe_id=recipe.recipe_id,
            name=recipe.name,
            author=recipe.author,
            rating=recipe.rating,
            prep_time=recipe.prep_time,
            cook_time=recipe.cook_time,
            modified_at=datetime.now(),
            instructions=recipe.instructions,
        )
    )


def delete_recipe_by_id(recipe_id: int, conn: Connection):
    """Basic  naive wrapper for an DELETE to the recipe_table.

    Note that this function does not 'commit' anything to the database.
    """
    conn.execute(delete(recipes_table).where(recipes_table.c.recipe_id == recipe_id))


def delete_ingredients_of_recipe(recipe_id: int, conn: Connection):
    """Basic  naive wrapper for a group of DELETEs to the ingredient_table.

    Note that this function does not 'commit' anything to the database.
    """
    conn.execute(
        delete(ingredients_table).where(ingredients_table.c.recipe_id == recipe_id)
    )
