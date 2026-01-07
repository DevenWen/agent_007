"""Skill Loader Service

Loads and parses Skill files from the filesystem.
Skills are defined as Markdown files with YAML FrontMatter.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """Skill 数据类"""

    name: str
    description: str
    tools: List[str]
    content: str


class SkillLoader:
    """Skill 文件加载器"""

    def __init__(self, skill_dir: Path | str):
        """初始化 SkillLoader

        Args:
            skill_dir: Skill 文件所在目录
        """
        self.skill_dir = Path(skill_dir)
        self._cache: Dict[str, Skill] = {}
        self._load_all()

    def _load_all(self):
        """加载所有 skill 文件到缓存"""
        if not self.skill_dir.exists():
            logger.warning(f"Skill directory does not exist: {self.skill_dir}")
            return

        for skill_file in self.skill_dir.glob("*.md"):
            try:
                skill = self._parse_skill_file(skill_file)
                if skill:
                    self._cache[skill.name] = skill
            except Exception as e:
                logger.error(f"Failed to load skill {skill_file.name}: {e}")

    def _parse_skill_file(self, file_path: Path) -> Optional[Skill]:
        """解析单个 skill 文件

        Args:
            file_path: Skill 文件路径

        Returns:
            解析后的 Skill 对象，如果解析失败返回 None
        """
        try:
            content = file_path.read_text(encoding="utf-8")

            # 解析 FrontMatter
            if not content.startswith("---"):
                logger.warning(f"Skill file {file_path.name} missing FrontMatter")
                return None

            # 分离 FrontMatter 和 Content
            parts = content.split("---", 2)
            if len(parts) < 3:
                logger.warning(f"Invalid FrontMatter in {file_path.name}")
                return None

            frontmatter_text = parts[1]
            content_text = parts[2].strip()

            # 解析 YAML
            metadata = yaml.safe_load(frontmatter_text)

            if not isinstance(metadata, dict):
                logger.warning(f"Invalid metadata in {file_path.name}")
                return None

            # 验证必需字段
            required_fields = ["name", "description", "tools"]
            for field in required_fields:
                if field not in metadata:
                    logger.warning(
                        f"Missing required field '{field}' in {file_path.name}"
                    )
                    return None

            return Skill(
                name=metadata["name"],
                description=metadata["description"],
                tools=metadata["tools"] if isinstance(metadata["tools"], list) else [],
                content=content_text,
            )

        except Exception as e:
            logger.error(f"Error parsing skill file {file_path}: {e}")
            return None

    def list_skills(self) -> List[Skill]:
        """列出所有已加载的 skills

        Returns:
            Skill 列表
        """
        return list(self._cache.values())

    def get_skill(self, name: str) -> Optional[Skill]:
        """通过名称获取 skill

        Args:
            name: Skill 名称

        Returns:
            Skill 对象，如果不存在返回 None
        """
        return self._cache.get(name)
