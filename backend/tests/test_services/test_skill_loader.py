"""SkillLoader Service 单元测试"""

import pytest
from pathlib import Path

from app.services.skill_loader import SkillLoader, Skill


@pytest.mark.unit
class TestSkillLoader:
    """测试 SkillLoader 服务"""

    def test_load_skills_from_directory(self, tmp_path):
        """测试从目录加载所有 skills"""
        # 创建测试 skill 文件
        skill_dir = tmp_path / "skills"
        skill_dir.mkdir()

        skill1 = skill_dir / "analyst.md"
        skill1.write_text("""---
name: analyst
description: Data analysis
tools: [python, read_file]
---

You are an analyst.""")

        skill2 = skill_dir / "reviewer.md"
        skill2.write_text("""---
name: reviewer
description: Code review
tools: [read_file, search]
---

You are a reviewer.""")

        # 加载 skills
        loader = SkillLoader(skill_dir)
        skills = loader.list_skills()

        assert len(skills) == 2
        assert "analyst" in [s.name for s in skills]
        assert "reviewer" in [s.name for s in skills]

    def test_get_skill_by_name(self, tmp_path):
        """测试通过名称获取 skill"""
        skill_dir = tmp_path / "skills"
        skill_dir.mkdir()

        skill_file = skill_dir / "test_skill.md"
        skill_file.write_text("""---
name: test_skill
description: Test skill
tools: [tool1, tool2]
---

This is test content.""")

        loader = SkillLoader(skill_dir)
        skill = loader.get_skill("test_skill")

        assert skill is not None
        assert skill.name == "test_skill"
        assert skill.description == "Test skill"
        assert skill.tools == ["tool1", "tool2"]
        assert "This is test content." in skill.content

    def test_get_nonexistent_skill(self, tmp_path):
        """测试获取不存在的 skill 返回 None"""
        skill_dir = tmp_path / "skills"
        skill_dir.mkdir()

        loader = SkillLoader(skill_dir)
        skill = loader.get_skill("nonexistent")

        assert skill is None

    def test_skill_caching(self, tmp_path):
        """测试 skill 缓存机制"""
        skill_dir = tmp_path / "skills"
        skill_dir.mkdir()

        skill_file = skill_dir / "cached.md"
        skill_file.write_text("""---
name: cached
description: Cached skill
tools: []
---

Content.""")

        loader = SkillLoader(skill_dir)

        # 第一次加载
        skill1 = loader.get_skill("cached")
        # 第二次应该从缓存读取
        skill2 = loader.get_skill("cached")

        assert skill1 is skill2  # 同一个对象实例

    def test_invalid_frontmatter(self, tmp_path):
        """测试处理无效的 FrontMatter"""
        skill_dir = tmp_path / "skills"
        skill_dir.mkdir()

        skill_file = skill_dir / "invalid.md"
        skill_file.write_text("""Invalid content without frontmatter""")

        loader = SkillLoader(skill_dir)
        skill = loader.get_skill("invalid")

        # 应该跳过无效文件或返回 None
        assert skill is None

    def test_skill_dataclass(self):
        """测试 Skill 数据类"""
        skill = Skill(
            name="test",
            description="Test description",
            tools=["tool1"],
            content="Test content",
        )

        assert skill.name == "test"
        assert skill.description == "Test description"
        assert skill.tools == ["tool1"]
        assert skill.content == "Test content"
