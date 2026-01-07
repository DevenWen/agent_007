"""Skills API 路由单元测试"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.unit
class TestSkillsRouter:
    """测试 Skills API 路由"""

    async def test_list_skills(self):
        """测试列出所有 skills"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/skills")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            # 应该包含我们创建的测试 skills
            assert len(data) >= 2

            skill_names = [s["name"] for s in data]
            assert "data_analyst" in skill_names
            assert "code_reviewer" in skill_names

    async def test_get_skill_by_name(self):
        """测试通过名称获取 skill 详情"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/skills/data_analyst")

            assert response.status_code == 200
            data = response.json()

            assert data["name"] == "data_analyst"
            assert data["description"] == "Analyze datasets and produce reports"
            assert "python_interpreter" in data["tools"]
            assert "read_file" in data["tools"]
            assert "You are a data analyst" in data["content"]

    async def test_get_nonexistent_skill(self):
        """测试获取不存在的 skill 返回 404"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/skills/nonexistent_skill")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
