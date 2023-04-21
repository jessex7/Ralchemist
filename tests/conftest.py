import pytest
import json
from os import scandir
from datetime import datetime
from sqlalchemy import MetaData, create_engine
from starlette.testclient import TestClient
from magicoffastapi.app import app
from magicoffastapi.db.tables import build_ingredients_table, build_recipes_table
from magicoffastapi.db.operations import create_recipe
from magicoffastapi.settings import settings
from magicoffastapi.schemas.recipe import BaseRecipe

# creates a fresh database
metadata = MetaData()
metadata, recipes_table = build_recipes_table(metadata=metadata)
metadata, ingredients_table = build_ingredients_table(metadata=metadata)
engine = create_engine(settings.DATABASE_URL)
metadata.drop_all(engine)
metadata.create_all(bind=engine)

# insert sample data
with engine.connect() as conn:
    ts = datetime.now()
    with open("tests/full-dataset.json", "r") as f:
        json_data = json.load(f)
        for recipe in json_data:
            print(recipe["name"])
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
