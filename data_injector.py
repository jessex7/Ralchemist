import json
from sqlalchemy import MetaData, create_engine
from src.db.tables import build_ingredients_table, build_recipes_table
from src.db.operations import create_recipe
from src.settings import settings
from src.schemas.recipe import BaseRecipe

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