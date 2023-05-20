from RecipeAlchemy.smarts.recipe_finder import RecipeFinder


def test_recipe_finder_sorts_recipes(joined_recipe_records, db_conn):
    # arrange
    rfinder = RecipeFinder(conn=db_conn)
    query = set(["garlic", "ginger"])

    # act
    scored_recipes = rfinder.find(query, None)

    # assert
    print(f"Number of found recipes: {len(scored_recipes)}")
    for r in scored_recipes:
        has_ingredient = False
        matches = set()
        for ingredient in r.recipe.ingredients:
            for query_value in query:
                if query_value in ingredient.ingred_name:
                    has_ingredient = True
                    matches.add(query_value)
        print(f"{r.recipe.name}, with count: {len(matches)}")

        assert has_ingredient is True
        assert r.score == len(matches)
