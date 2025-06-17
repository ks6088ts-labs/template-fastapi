"""
Simple example of using FastAPI-MCP to add an MCP server to a FastAPI app.
ref. https://github.com/tadata-org/fastapi_mcp/blob/v0.3.4/examples/shared/apps/items.py
"""

import random
import uuid
from os import getenv

from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi import FastAPI, HTTPException, Query
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.trace import Span
from pydantic import BaseModel

app = FastAPI()

# If APPLICATIONINSIGHTS_CONNECTION_STRING exists, configure Azure Monitor
AZURE_CONNECTION_STRING = getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
if AZURE_CONNECTION_STRING:

    def server_request_hook(span: Span, scope: dict):
        if span and span.is_recording():
            try:
                # Application Insights に送るデータにユーザ ID を追加する
                user_id = uuid.uuid4().hex  # Replace with actual user ID retrieval logic
                span.set_attribute("enduser.id", user_id)
            except KeyError:
                pass

    configure_azure_monitor(
        connection_string=AZURE_CONNECTION_STRING,
    )
    FastAPIInstrumentor.instrument_app(app)


class Item(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    tags: list[str] = []


items_db: dict[int, Item] = {}


@app.get("/items/", response_model=list[Item], tags=["items"], operation_id="list_items")
async def list_items(skip: int = 0, limit: int = 10):
    """
    List all items in the database.

    Returns a list of items, with pagination support.
    """
    return list(items_db.values())[skip : skip + limit]


@app.get("/items/{item_id}", response_model=Item, tags=["items"], operation_id="get_item")
async def read_item(item_id: int):
    """
    Get a specific item by its ID.

    Raises a 404 error if the item does not exist.
    """
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]


@app.post("/items/", response_model=Item, tags=["items"], operation_id="create_item")
async def create_item(item: Item):
    """
    Create a new item in the database.

    Returns the created item with its assigned ID.
    """
    items_db[item.id] = item
    return item


@app.put("/items/{item_id}", response_model=Item, tags=["items"], operation_id="update_item")
async def update_item(item_id: int, item: Item):
    """
    Update an existing item.

    Raises a 404 error if the item does not exist.
    """
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    item.id = item_id
    items_db[item_id] = item
    return item


@app.delete("/items/{item_id}", tags=["items"], operation_id="delete_item")
async def delete_item(item_id: int):
    """
    Delete an item from the database.

    Raises a 404 error if the item does not exist.
    """
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    del items_db[item_id]
    return {"message": "Item deleted successfully"}


@app.get("/items/search/", response_model=list[Item], tags=["search"], operation_id="search_items")
async def search_items(
    q: str | None = Query(None, description="Search query string"),
    min_price: float | None = Query(None, description="Minimum price"),
    max_price: float | None = Query(None, description="Maximum price"),
    tags: list[str] = Query([], description="Filter by tags"),
):
    """
    Search for items with various filters.

    Returns a list of items that match the search criteria.
    """
    results = list(items_db.values())

    if q:
        q = q.lower()
        results = [
            item
            for item in results
            if q in item.name.lower() or (item.description is not None and q in item.description.lower())
        ]

    if min_price is not None:
        results = [item for item in results if item.price >= min_price]
    if max_price is not None:
        results = [item for item in results if item.price <= max_price]

    if tags:
        results = [item for item in results if all(tag in item.tags for tag in tags)]

    return results


sample_items = [
    Item(id=1, name="Hammer", description="A tool for hammering nails", price=9.99, tags=["tool", "hardware"]),
    Item(id=2, name="Screwdriver", description="A tool for driving screws", price=7.99, tags=["tool", "hardware"]),
    Item(id=3, name="Wrench", description="A tool for tightening bolts", price=12.99, tags=["tool", "hardware"]),
    Item(id=4, name="Saw", description="A tool for cutting wood", price=19.99, tags=["tool", "hardware", "cutting"]),
    Item(id=5, name="Drill", description="A tool for drilling holes", price=49.99, tags=["tool", "hardware", "power"]),
]
for item in sample_items:
    items_db[item.id] = item


# Add flaky API which receives percentage of failure
@app.get("/flaky/{failure_rate}", tags=["flaky"], operation_id="flaky")
async def flaky(failure_rate: int):
    """
    A flaky endpoint that simulates a failure based on the provided failure rate.

    The failure rate is a percentage (0-100) that determines the likelihood of failure.
    """
    if not (0 <= failure_rate <= 100):
        raise HTTPException(
            status_code=400,
            detail="Failure rate must be between 0 and 100",
        )

    if random.randint(0, 100) < failure_rate:
        raise HTTPException(
            status_code=500,
            detail="Simulated failure",
        )

    return {
        "message": "Request succeeded",
    }


# Add flaky API which raises an exception
@app.get("/flaky/exception", tags=["flaky"], operation_id="flaky_exception")
async def flaky_exception():
    """
    A flaky endpoint that always raises an exception.
    """
    raise HTTPException(
        status_code=500,
        detail="Simulated exception",
    )
