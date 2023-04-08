from sqlalchemy import (
    create_engine,
    MetaData,
    inspect,
    Engine,
)

from magicoffastapi.settings import settings
from magicoffastapi.db.tables import build_recipes_table, build_ingredients_table


def construct_db_if_none_exists(engine: Engine, metadata: MetaData) -> None:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if "recipe" not in table_names or "ingredient" not in table_names:
        metadata.create_all(bind=engine)


metadata = MetaData()
metadata, recipes_table = build_recipes_table(metadata=metadata)
metadata, ingredients_table = build_ingredients_table(metadata=metadata)
engine = create_engine(settings.DATABASE_URL)
construct_db_if_none_exists(engine=engine, metadata=metadata)


def get_db_conn():
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()
