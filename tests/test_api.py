from fastapi.testclient import TestClient

from template_fastapi.app import app

client = TestClient(app)


def test_list_items():
    """Test that the items endpoint returns a list of items."""
    response = client.get("/items/")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) == 5  # We have 5 sample items

    # Check the first item structure
    item = items[0]
    assert "id" in item
    assert "name" in item
    assert "description" in item
    assert "price" in item
    assert "tags" in item


def test_get_item():
    """Test getting a specific item by ID."""
    response = client.get("/items/1")
    assert response.status_code == 200
    item = response.json()
    assert item["id"] == 1
    assert item["name"] == "Hammer"
    assert item["price"] == 9.99


def test_get_nonexistent_item():
    """Test getting a non-existent item returns 404."""
    response = client.get("/items/999")
    assert response.status_code == 404


def test_roll_dice():
    """Test the dice rolling endpoint."""
    response = client.get("/demo/roll_dice")
    assert response.status_code == 404


def test_flaky_endpoint():
    """Test the flaky endpoint with 0% failure rate."""
    response = client.get("/demo/flaky/0")
    assert response.status_code == 404


def test_flaky_exception():
    """Test the flaky exception endpoint."""
    response = client.get("/demo/flaky/exception")
    assert response.status_code == 404


def test_heavy_sync():
    """Test the heavy sync endpoint with minimal sleep."""
    response = client.get("/demo/heavy_sync/10")  # 10 milliseconds
    assert response.status_code == 404


def test_search_items():
    """Test the items search endpoint."""
    response = client.get("/items/search/?q=hammer")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["name"] == "Hammer"
