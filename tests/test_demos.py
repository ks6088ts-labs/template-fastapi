"""Tests for demos router."""

from fastapi.testclient import TestClient

from template_fastapi.app import app

client = TestClient(app)


def test_roll_dice():
    """Test the roll dice endpoint."""
    response = client.get("/demos/roll_dice")
    assert response.status_code == 200
    result = response.json()
    # Should return a number between 1 and 6
    assert isinstance(result, int)
    assert 1 <= result <= 6


def test_flaky_endpoint_success():
    """Test flaky endpoint with 0% failure rate (should always succeed)."""
    response = client.get("/demos/flaky/0")
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Request succeeded"


def test_flaky_endpoint_failure():
    """Test flaky endpoint with 100% failure rate (should always fail)."""
    response = client.get("/demos/flaky/100")
    assert response.status_code == 500
    result = response.json()
    assert "Simulated failure" in result["detail"]


def test_flaky_endpoint_invalid_rate():
    """Test flaky endpoint with invalid failure rate."""
    response = client.get("/demos/flaky/150")
    assert response.status_code == 400
    result = response.json()
    assert "Failure rate must be between 0 and 100" in result["detail"]


def test_flaky_endpoint_negative_rate():
    """Test flaky endpoint with negative failure rate."""
    response = client.get("/demos/flaky/-10")
    assert response.status_code == 400
    result = response.json()
    assert "Failure rate must be between 0 and 100" in result["detail"]


def test_flaky_exception():
    """Test the flaky exception endpoint."""
    response = client.get("/demos/flaky/exception")
    assert response.status_code == 500
    result = response.json()
    assert "Simulated exception" in result["detail"]


def test_heavy_sync_valid():
    """Test heavy sync endpoint with valid sleep time."""
    response = client.get("/demos/heavy_sync/10")
    assert response.status_code == 200
    result = response.json()
    assert "Slept for 10 milliseconds" in result["message"]


def test_heavy_sync_zero():
    """Test heavy sync endpoint with zero sleep time."""
    response = client.get("/demos/heavy_sync/0")
    assert response.status_code == 200
    result = response.json()
    assert "Slept for 0 milliseconds" in result["message"]


def test_heavy_sync_negative():
    """Test heavy sync endpoint with negative sleep time."""
    response = client.get("/demos/heavy_sync/-5")
    assert response.status_code == 400
    result = response.json()
    assert "Sleep time must be a non-negative integer" in result["detail"]
