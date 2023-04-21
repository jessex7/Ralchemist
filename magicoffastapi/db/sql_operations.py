from datetime import datetime
from sqlalchemy import (
    Connection,
    select,
    insert,
    Result,
    delete,
    update,
    Select,
    or_,
    Row,
)
from magicoffastapi.schemas.recipe import (
    Recipe,
    BaseRecipe,
    RecipeInDB,
    Ingredient,
    JoinedRecipeRecord,
)
from magicoffastapi.db.setup import recipes_table, ingredients_table


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


def select_recipes_by_ids(
    conn: Connection, recipe_ids: list[int] | None
) -> list[RecipeInDB] | None:
    """Basic wrapper for a SELECT of recipes from the recipe_table."""
    if recipe_ids is None:
        return None
    stmt = build_recipe_select()
    conditions = []
    for id in recipe_ids:
        conditions.append(recipes_table.c.recipe_id == id)
    stmt = stmt.filter(or_(*conditions))
    recipes_result: Result = conn.execute(stmt)
    raw_recipes = recipes_result.all()
    if raw_recipes is None:
        return None
    recipes: list[RecipeInDB] = []
    for raw_recipe in raw_recipes:
        raw_recipe_dict = raw_recipe._asdict()
        recipes.append(RecipeInDB(**raw_recipe_dict))
    return recipes


def select_recipes_with_ingredients_by_ids(
    conn: Connection, recipe_ids: list[int]
) -> list[JoinedRecipeRecord] | None:
    stmt = build_recipe_with_ingredients_select_statement()
    conditions = []
    for id in recipe_ids:
        conditions.append(recipes_table.c.recipe_id == id)
    stmt = stmt.filter(or_(*conditions))
    stmt = stmt.order_by(recipes_table.c.recipe_id)
    recipes_result: Result = conn.execute(stmt)
    raw_joined_rows = recipes_result.all()
    if raw_joined_rows is None:
        return None
    joined_recipe_records = []
    for row in raw_joined_rows:
        joined_recipe_record = JoinedRecipeRecord(**row._asdict())
    return joined_recipe_records


def select_recipe_by_id_with_ingredients(
    recipe_id: int, conn: Connection
) -> Recipe | None:
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
            ingredients_table.c.ingred_name,
            ingredients_table.c.amount,
            ingredients_table.c.unit,
            ingredients_table.c.notes,
            ingredients_table.c.group,
        )
        .join_from(recipes_table, ingredients_table)
        .where(recipes_table.c.recipe_id == recipe_id)
    )
    raw_joined_rows = recipe_result.all()
    if len(raw_joined_rows) == 0:
        return None
    recipe_dict = raw_joined_rows[0]._asdict()
    recipe_dict["ingredients"] = []
    recipe = Recipe(**recipe_dict)
    for x in range(0, len(raw_joined_rows)):
        raw_ingredient = raw_joined_rows[x]._asdict()
        recipe.ingredients.append(
            Ingredient(
                ingred_name=raw_ingredient["ingred_name"],
                amount=raw_ingredient["amount"],
                unit=raw_ingredient["unit"],
                notes=raw_ingredient["notes"],
                group=raw_ingredient["group"],
            )
        )
    return recipe


def select_joined_recipes_matching_query(
    conn: Connection,
    name: str | None,
    author: str | None,
    ingredients: list[str] | None,
) -> list[JoinedRecipeRecord] | None:
    stmt = build_recipe_with_ingredients_select_statement()
    filters = []
    if name is not None:
        filters.append(recipes_table.c.name == name)
    if author is not None:
        filters.append(recipes_table.c.author == author)
    if ingredients is not None:
        for ingredient in ingredients:
            filters.append(ingredients_table.c.ingred_name == ingredient)
    stmt = stmt.filter(or_(*filters))
    recipes_result: Result = conn.execute(stmt)
    raw_joined_rows = recipes_result.all()
    if raw_joined_rows is None:
        return None
    joined_recipe_records = []
    for row in raw_joined_rows:
        joined_recipe_record = JoinedRecipeRecord(**row._asdict())
    return joined_recipe_records


def select_recipes(
    conn: Connection, name: str | None, author: str | None
) -> list[RecipeInDB] | None:
    """Basic wrapper for a SELECT of records from the recipe_table"""
    conditions = []
    stmt = build_recipe_select()
    if name is not None:
        conditions.append(recipes_table.c.name == name)
    if author is not None:
        conditions.append(recipes_table.c.author == author)
    if len(conditions) > 0:
        stmt = stmt.filter(or_(*conditions))
    stmt = stmt.order_by(recipes_table.c.name)
    recipe_result: Result = conn.execute(stmt)
    raw_recipes = recipe_result.all()
    recipes: list[RecipeInDB] = []
    if raw_recipes is None:
        return None
    for raw_recipe in raw_recipes:
        raw_recipe_dict = raw_recipe._asdict()
        recipe = RecipeInDB(**raw_recipe_dict)
        recipes.append(recipe)
    return recipes


def select_ingredients_by_recipe_id(
    recipe_id: int, conn: Connection
) -> list[Ingredient]:
    """Basic wrapper for SELECT of ingredients from the ingredients_table."""

    ingred_result: Result = conn.execute(
        select(
            ingredients_table.c.ingred_name,
            ingredients_table.c.amount,
            ingredients_table.c.unit,
            ingredients_table.c.notes,
            ingredients_table.c.group,
        ).where(ingredients_table.c.recipe_id == recipe_id)
    )
    raw_ingredients = ingred_result.all()
    formatted_ingredients: list[Ingredient] = []
    for i in raw_ingredients:
        formatted_ingredients.append(Ingredient(**(i._asdict())))
    return formatted_ingredients


def select_recipe_ids_by_ingredients(
    conn: Connection, ingred_names: list[str] | None
) -> set[int] | None:
    """Basic wrapper for SELECT to find recipes based on ingredient name."""
    if ingred_names is None or len(ingred_names) == 0:
        return None
    stmt = select(ingredients_table.c.recipe_id)
    conditions = []
    for ingredient in ingred_names:
        conditions.append(ingredients_table.c.ingred_name == ingredient)
    if len(conditions) > 0:
        stmt = stmt.filter(or_(*conditions))
    ingred_result: Result = conn.execute(stmt)
    recipe_ids = set()
    for row in ingred_result:
        recipe_ids.add(row[0])
    return recipe_ids


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


def build_recipe_with_ingredients_select_statement() -> Select:
    return select(
        recipes_table.c.recipe_id,
        recipes_table.c.name,
        recipes_table.c.author,
        recipes_table.c.rating,
        recipes_table.c.prep_time,
        recipes_table.c.cook_time,
        recipes_table.c.created_at,
        recipes_table.c.modified_at,
        recipes_table.c.instructions,
        ingredients_table.c.ingred_name,
        ingredients_table.c.amount,
        ingredients_table.c.unit,
        ingredients_table.c.notes,
        ingredients_table.c.group,
    ).join_from(recipes_table, ingredients_table)


def build_recipe_select() -> Select:
    return select(
        recipes_table.c.recipe_id,
        recipes_table.c.name,
        recipes_table.c.author,
        recipes_table.c.rating,
        recipes_table.c.prep_time,
        recipes_table.c.cook_time,
        recipes_table.c.created_at,
        recipes_table.c.modified_at,
        recipes_table.c.instructions,
    )
