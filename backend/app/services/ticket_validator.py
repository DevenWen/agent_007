"""Ticket Validation Service

Handles parameter validation for Ticket creation.
"""

import json
import logging
from typing import Dict, Any, Optional

import jsonschema
from jsonschema import ValidationError

logger = logging.getLogger(__name__)


def validate_and_merge_params(
    agent_default_params: Optional[str],
    agent_params_schema: Optional[str],
    user_params: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """验证并合并 Ticket 参数

    Args:
        agent_default_params: Agent 的默认参数 (JSON 字符串)
        agent_params_schema: Agent 的参数 Schema (JSON 字符串)
        user_params: 用户提供的参数

    Returns:
        合并并验证后的参数

    Raises:
        jsonschema.ValidationError: 如果参数不符合 Schema
    """
    # 1. 解析 default_params
    default_params = {}
    if agent_default_params:
        try:
            default_params = json.loads(agent_default_params)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse agent default_params: {e}")

    # 2. 合并参数: default_params 作为基础，user_params 覆盖
    final_params = {**default_params, **(user_params or {})}

    # 3. 验证参数
    if agent_params_schema:
        try:
            schema = json.loads(agent_params_schema)
            jsonschema.validate(instance=final_params, schema=schema)
            logger.info(f"Params validation passed: {final_params}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid params_schema JSON: {e}")
            raise ValidationError(f"Invalid schema format: {e}")
        except ValidationError as e:
            logger.error(f"Params validation failed: {e.message}")
            raise

    return final_params
