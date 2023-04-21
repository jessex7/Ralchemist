from sqlalchemy import (
    MetaData,
    Table,
    Integer,
    String,
    Column,
    Float,
    DateTime,
    ForeignKey,
)


def build_recipes_table(metadata: MetaData) -> tuple[MetaData, Table]:
    table = Table(
        "recipe",
        metadata,
        Column("recipe_id", Integer, primary_key=True),
        Column("name", String, nullable=False),
        Column("author", String, nullable=False),
        Column("rating", Integer),
        Column("prep_time", Float),
        Column("cook_time", Float),
        Column("created_at", DateTime, nullable=False),
        Column("modified_at", DateTime, nullable=False),
        Column("instructions", String),
    )
    return (metadata, table)


def build_ingredients_table(metadata: MetaData) -> tuple[MetaData, Table]:
    table = Table(
        "ingredient",
        metadata,
        Column("ingred_id", Integer, primary_key=True),
        Column(
            "recipe_id",
            ForeignKey("recipe.recipe_id", ondelete="CASCADE"),
        ),
        Column("ingred_name", String),
        Column("amount", Float),
        Column("unit", String),
        Column("notes", String),
        Column("group", String),
        # Column("created_at", DateTime, nullable=False),
        # Column("modified_at", DateTime, nullable=False),
    )
    return (metadata, table)
