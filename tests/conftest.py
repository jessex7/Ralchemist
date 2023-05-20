import pytest
import json
from sqlalchemy import MetaData, create_engine
from starlette.testclient import TestClient
from RecipeAlchemy.app import app
from RecipeAlchemy.db.tables import build_ingredients_table, build_recipes_table
from RecipeAlchemy.db.sql_operations import select_joined_recipes_matching_query
from RecipeAlchemy.db.operations import create_recipe
from RecipeAlchemy.settings import settings
from RecipeAlchemy.schemas.recipe import BaseRecipe

# creates a fresh database
metadata = MetaData()
metadata, recipes_table = build_recipes_table(metadata=metadata)
metadata, ingredients_table = build_ingredients_table(metadata=metadata)
engine = create_engine(settings.DATABASE_URL, echo=True)
metadata.drop_all(engine)
metadata.create_all(bind=engine)

# insert sample data
with engine.connect() as conn:
    with open("tests/full-dataset.json", "r") as f:
        json_data = json.load(f)
        for recipe in json_data:
            recipe = BaseRecipe(**recipe)
            if create_recipe(recipe, conn) is None:
                raise Exception("Encoding error:")


@pytest.fixture
def db_conn():
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()


@pytest.fixture
def client():
    client = TestClient(app)
    yield client


@pytest.fixture
def joined_recipe_records(db_conn):
    results = select_joined_recipes_matching_query(
        conn=db_conn, name=None, author=None, ingredients=None
    )
    if results is None:
        raise Exception
    return results
