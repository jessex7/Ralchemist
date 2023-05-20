from fastapi.testclient import TestClient
from sqlalchemy import Connection
from RecipeAlchemy.app import app
from RecipeAlchemy.db.operations import (
    delete_recipe_by_id,
    insert_recipe,
    insert_ingredients,
)


def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200


def test_create_recipe(client: TestClient, db_conn: Connection):
    # arrange
    data = {
        "name": "Mac & cheese",
        "author": "Joe",
        "rating": 8,
        "ingredients": [
            {"ingred_name": "Cheddar cheese", "amount": 2, "unit": "cup(s)"},
            {"ingred_name": "milk", "amount": 1, "unit": "cup(s)"},
            {"ingred_name": "macaroni pasta", "amount": 4, "unit": "cup(s)"},
        ],
    }

    # act
    response = client.post("/recipes/", json=data)

    # assert
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["name"] == "Mac & cheese"

    # cleanup
    recipe_id = response_data["recipe_id"]
    delete_recipe_by_id(recipe_id=recipe_id, conn=db_conn)
    db_conn.commit()


def test_read_recipe(client: TestClient):
    # arrange - see conftest

    # act
    response = client.get("/recipes/1")

    # assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["recipe_id"] == 1

    # clean up - none required


def test_read_recipes(client: TestClient):
    # arrange - see conftest

    # act
    response = client.get("/recipes")

    # assert
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) > 0


def test_read_recipes_from_query(client: TestClient):
    # arrange - see conftest

    # act
    params = {
        "name": "Spicy Vodka Chicken Parmesan",
    }
    response = client.get(
        "/recipes",
        params=params,
    )

    # assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data[0]["name"] == "Spicy Vodka Chicken Parmesan"


def test_update_recipe(client: TestClient):
    # arrange
    initial_response = client.get("/recipes/1")
    recipe_dict = initial_response.json()
    recipe_dict["author"] = "a different author"

    # act
    response = client.put("/recipes/1", json=recipe_dict)

    # assert
    assert response.status_code == 200
    updated_recipe = response.json()
    assert updated_recipe["author"] == "a different author"


def test_delete_recipe(client: TestClient):
    # arrange - see conftest

    # act
    response = client.delete("/recipes/1")

    # assert
    assert response.status_code == 204
    confirmation = client.get("/recipes/1")
    assert confirmation.status_code == 404
