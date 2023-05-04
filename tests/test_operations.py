from magicoffastapi.db.operations import _combine_joined_recipe_records
from magicoffastapi.schemas.recipe import Recipe


def test_combined_joined_recipe_records(joined_recipe_records):
    # arrange
    records = joined_recipe_records

    # act
    combined_records = _combine_joined_recipe_records(records)

    # assert
    assert isinstance(combined_records[0], Recipe)