"""Tests for additional routers - basic endpoint availability tests."""

import pytest
from fastapi.testclient import TestClient

from template_fastapi.app import app

client = TestClient(app)


class TestChatsRouter:
    """Test chats router basic functionality."""

    def test_get_chat_page_exists(self):
        """Test that the chat page endpoint exists."""
        response = client.get("/chats/")
        # Should not return 404 - either 200 (success) or 500 (template issue)
        assert response.status_code != 404


class TestFilesRouter:
    """Test files router basic functionality."""

    def test_list_files_endpoint_exists(self):
        """Test that the list files endpoint exists."""
        response = client.get("/files/")
        # Should not return 404 - may return 500 due to missing dependencies
        assert response.status_code != 404

    def test_get_file_info_endpoint_exists(self):
        """Test that the get file info endpoint exists."""
        response = client.get("/files/test.txt/info")
        # Should not return 404 - may return 500 due to missing file
        assert response.status_code != 404


class TestFoodiesRouter:
    """Test foodies router basic functionality."""

    def test_list_restaurants_endpoint_exists(self):
        """Test that the list restaurants endpoint exists."""
        response = client.get("/foodies/restaurants/")
        # Should not return 404 - may return 500 due to missing dependencies
        assert response.status_code != 404

    def test_search_restaurants_endpoint_exists(self):
        """Test that the search restaurants endpoint exists."""
        response = client.get("/foodies/restaurants/search/?query=test")
        # Should not return 404 - may return 500 due to missing dependencies
        assert response.status_code != 404

    def test_find_nearby_restaurants_endpoint_exists(self):
        """Test that the find nearby restaurants endpoint exists."""
        response = client.get("/foodies/restaurants/near/?latitude=35.6762&longitude=139.6503")
        # Should not return 404 - may return 500 due to missing dependencies
        assert response.status_code != 404


class TestSpeechesRouter:
    """Test speeches router basic functionality."""

    def test_list_transcription_jobs_endpoint_exists(self):
        """Test that the list transcription jobs endpoint exists."""
        response = client.get("/speeches/transcriptions/")
        # Should not return 404 - may return 500 due to missing dependencies
        assert response.status_code != 404

    def test_get_transcription_job_endpoint_exists(self):
        """Test that the get transcription job endpoint exists."""
        response = client.get("/speeches/transcriptions/test-job-id")
        # Should not return 404 - may return 500 due to missing job
        assert response.status_code != 404


class TestAgentsRouter:
    """Test agents router basic functionality."""

    def test_langgraph_tools_endpoint_exists(self):
        """Test that the langgraph tools endpoint exists."""
        response = client.get("/agents/langgraph/tools")
        assert response.status_code == 200

    def test_azure_ai_foundry_agents_endpoint_exists(self):
        """Test that the Azure AI Foundry agents endpoint exists."""
        response = client.get("/agents/azure-ai-foundry/")
        # Should not return 404 - may return 500 due to missing dependencies
        assert response.status_code != 404

    def test_azure_ai_foundry_threads_endpoint_exists(self):
        """Test that the Azure AI Foundry threads endpoint exists."""
        response = client.get("/agents/azure-ai-foundry/threads/")
        # Should not return 404 - may return 500 due to missing dependencies
        assert response.status_code != 404