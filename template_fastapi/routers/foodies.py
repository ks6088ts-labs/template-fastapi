import uuid

from fastapi import APIRouter

from template_fastapi.models.restaurant import Restaurant
from template_fastapi.settings.azure_cosmosdb import get_azure_cosmosdb_settings
from template_fastapi.settings.azure_openai import get_azure_openai_settings

router = APIRouter()
azure_cosmosdb_settings = get_azure_cosmosdb_settings()
azure_openai_settings = get_azure_openai_settings()


@router.get(
    "/foodies/restaurants/",
    response_model=list[Restaurant],
    tags=["foodies"],
    operation_id="list_foodies_restaurants",
)
async def list_foodies_restaurants() -> list[Restaurant]:
    """
    List foodies restaurants.
    """
    return [
        Restaurant(
            id=1,
            name="Foodie Restaurant 1",
            description="A great place for foodies.",
            price=20.0,
            tags=["Italian", "Pizza"],
        ),
        Restaurant(
            id=2,
            name="Foodie Restaurant 2",
            description="Delicious food and great ambiance.",
            price=25.0,
            tags=["Chinese", "Noodles"],
        ),
    ]


@router.get(
    "/foodies/restaurants/{restaurant_id}",
    response_model=Restaurant,
    tags=["foodies"],
    operation_id="get_foodies_restaurant",
)
async def get_foodies_restaurant(restaurant_id: int) -> Restaurant:
    """
    Get a specific foodies restaurant by ID.
    """
    # In a real application, you would fetch the restaurant from a database.
    return Restaurant(
        id=restaurant_id,
        name=f"Foodie Restaurant {restaurant_id}",
        description="A great place for foodies.",
        price=20.0 + restaurant_id,
        tags=["Italian", "Pizza"],
    )


@router.post(
    "/foodies/restaurants/",
    response_model=Restaurant,
    tags=["foodies"],
    operation_id="create_foodies_restaurant",
)
async def create_foodies_restaurant(restaurant: Restaurant) -> Restaurant:
    """
    Create a new foodies restaurant.
    """
    # In a real application, you would save the restaurant to a database.
    return Restaurant(
        id=uuid.uuid4().int,  # Simulating a unique ID generation
        name=restaurant.name,
        description=restaurant.description,
        price=restaurant.price,
        tags=restaurant.tags,
    )


@router.put(
    "/foodies/restaurants/{restaurant_id}",
    response_model=Restaurant,
    tags=["foodies"],
    operation_id="update_foodies_restaurant",
)
async def update_foodies_restaurant(restaurant_id: int, restaurant: Restaurant) -> Restaurant:
    """
    Update an existing foodies restaurant.
    """
    # In a real application, you would update the restaurant in a database.
    return Restaurant(
        id=restaurant_id,
        name=restaurant.name,
        description=restaurant.description,
        price=restaurant.price,
        tags=restaurant.tags,
    )


@router.delete(
    "/foodies/restaurants/{restaurant_id}",
    tags=["foodies"],
    operation_id="delete_foodies_restaurant",
)
async def delete_foodies_restaurant(restaurant_id: int) -> dict:
    """
    Delete a foodies restaurant by ID.
    """
    # In a real application, you would delete the restaurant from a database.
    return {"message": f"Restaurant with ID {restaurant_id} deleted successfully."}


@router.get(
    "/foodies/restaurants/search/",
    response_model=list[Restaurant],
    tags=["foodies"],
    operation_id="search_foodies_restaurants",
)
async def search_foodies_restaurants(query: str) -> list[Restaurant]:
    """
    Search for foodies restaurants by name.
    """
    # In a real application, you would query a database.
    return [
        Restaurant(
            id=1,
            name="Foodie Restaurant 1",
            description="A great place for foodies.",
            price=20.0,
            tags=["Italian", "Pizza"],
        ),
        Restaurant(
            id=2,
            name="Foodie Restaurant 2",
            description="Delicious food and great ambiance.",
            price=25.0,
            tags=["Chinese", "Noodles"],
        ),
    ]
