from typing import Annotated
from fastapi import APIRouter, Depends, Response, HTTPException, Query
from sqlalchemy import Connection
from src.db.setup import get_db_conn
from src.db.operations import (
    create_recipe,
    read_recipe_by_id,
    update_recipe,
    delete_recipe,
    read_recipes_matching_query,
    read_recipes,
)
from src.schemas.recipe import BaseRecipe, Recipe, ScoredRecipe
from src.smarts.recipe_finder import RecipeFinder

router = APIRouter(prefix="/recipes")


@router.get("/prototype")
async def prototype_functionality(
    db: Connection = Depends(get_db_conn),
) -> list[Recipe]:
    recipes = read_recipes(conn=db)
    if recipes is None:
        raise HTTPException(status_code=500)
    return recipes


@router.get("/find")
async def find_recipes(
    ingredients: Annotated[set[str], Query()],
    exclude: Annotated[set[int] | None, Query()] = None,
    db: Connection = Depends(get_db_conn),
) -> list[ScoredRecipe]:
    r_finder = RecipeFinder(conn=db)
    return r_finder.find(ingredients, exclude)


@router.get("/{recipe_id}")
async def get_recipe_by_id(
    recipe_id: int, db: Connection = Depends(get_db_conn)
) -> Recipe:
    recipe = read_recipe_by_id(id=recipe_id, conn=db)
    if recipe is None:
        raise HTTPException(status_code=404)
    return recipe


@router.get("/")
async def get_recipes(
    name: str | None = None,
    author: str | None = None,
    ingredients: Annotated[list[str] | None, Query()] = None,
    db: Connection = Depends(get_db_conn),
) -> list[Recipe]:
    recipes = read_recipes_matching_query(
        conn=db, name=name, author=author, ingredients=ingredients
    )
    if recipes is None:
        return []
    return recipes


@router.post("/", status_code=201)
async def post_recipe(
    new_recipe: BaseRecipe, db: Connection = Depends(get_db_conn)
) -> Recipe:
    response = create_recipe(new_recipe, db)
    return response


@router.put("/{recipe_id}")
async def put_recipe_by_id(
    recipe_id: int, recipe: Recipe, db: Connection = Depends(get_db_conn)
) -> Recipe:
    response = update_recipe(recipe, db)
    return response


@router.delete("/{recipe_id}", status_code=204)
async def delete_recipe_by_id(recipe_id: int, db: Connection = Depends(get_db_conn)):
    delete_recipe(recipe_id=recipe_id, conn=db)
    return Response(status_code=204)
