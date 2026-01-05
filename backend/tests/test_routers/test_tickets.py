"""Tickets Router 集成测试"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.integration
class TestTicketsRouter:
    """测试 Tickets Router API"""

    @pytest.fixture
    async def async_client(self):
        """创建测试客户端"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    async def test_list_tickets(self, async_client):
        """测试获取 Ticket 列表"""
        response = await async_client.get("/api/tickets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_create_and_get_ticket(self, async_client):
        """测试创建和获取 Ticket"""
        # 首先创建一个 Agent
        agent_data = {
            "name": "Test Agent",
            "prompt": "You are a test assistant",
        }
        agent_response = await async_client.post("/api/agents", json=agent_data)
        assert agent_response.status_code == 201
        agent = agent_response.json()

        # 创建 Ticket
        ticket_data = {
            "agent_id": agent["id"],
            "params": {"task": "test task"},
        }
        create_response = await async_client.post("/api/tickets", json=ticket_data)
        assert create_response.status_code == 201
        ticket = create_response.json()
        assert ticket["agent_id"] == agent["id"]
        assert ticket["status"] == "pending"

        # 获取 Ticket
        get_response = await async_client.get(f"/api/tickets/{ticket['id']}")
        assert get_response.status_code == 200
        fetched_ticket = get_response.json()
        assert fetched_ticket["id"] == ticket["id"]

    async def test_delete_ticket(self, async_client):
        """测试删除 Ticket"""
        # 创建 Agent
        agent_data = {
            "name": "Test Agent",
            "prompt": "Test prompt",
        }
        agent_response = await async_client.post("/api/agents", json=agent_data)
        agent = agent_response.json()

        # 创建 Ticket
        ticket_data = {"agent_id": agent["id"]}
        create_response = await async_client.post("/api/tickets", json=ticket_data)
        ticket = create_response.json()

        # 删除 Ticket
        delete_response = await async_client.delete(f"/api/tickets/{ticket['id']}")
        assert delete_response.status_code == 204

        # 验证已删除
        get_response = await async_client.get(f"/api/tickets/{ticket['id']}")
        assert get_response.status_code == 404

    async def test_create_ticket_with_nonexistent_agent(self, async_client):
        """测试使用不存在的 Agent 创建 Ticket"""
        ticket_data = {"agent_id": "nonexistent-agent-id"}
        response = await async_client.post("/api/tickets", json=ticket_data)
        assert response.status_code == 404
