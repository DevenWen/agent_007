"""Agents Router Integration Test"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.integration
class TestAgentsRouter:
    """Test Agents Router API"""

    @pytest.fixture
    async def async_client(self):
        """Create test client"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    async def test_get_agent(self, async_client):
        """Test Get Agent Detail"""
        # Create an agent first
        create_data = {"name": "Test Get Agent", "prompt": "Test Prompt"}
        res = await async_client.post("/api/agents", json=create_data)
        assert res.status_code == 201
        agent = res.json()
        agent_id = agent["id"]

        # Test GET /api/agents/{id}
        res_get = await async_client.get(f"/api/agents/{agent_id}")
        assert res_get.status_code == 200
        data = res_get.json()
        assert data["id"] == agent_id
        assert data["name"] == "Test Get Agent"

        # Test 404
        res_404 = await async_client.get("/api/agents/non-existent-id")
        assert res_404.status_code == 404
