"""Ticket Validator 单元测试"""

import pytest
import json
from jsonschema import ValidationError

from app.services.ticket_validator import validate_and_merge_params


@pytest.mark.unit
class TestTicketValidator:
    """测试 Ticket 参数验证"""

    def test_merge_params_no_defaults(self):
        """测试无默认参数时的合并"""
        user_params = {"key": "value"}
        result = validate_and_merge_params(None, None, user_params)

        assert result == {"key": "value"}

    def test_merge_params_with_defaults(self):
        """测试带默认参数的合并"""
        default_params = json.dumps({"repo": "default_repo", "branch": "main"})
        user_params = {"branch": "dev"}

        result = validate_and_merge_params(default_params, None, user_params)

        assert result == {"repo": "default_repo", "branch": "dev"}

    def test_validation_success(self):
        """测试参数验证成功"""
        schema = json.dumps(
            {
                "type": "object",
                "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
                "required": ["name"],
            }
        )

        user_params = {"name": "Alice", "age": 30}
        result = validate_and_merge_params(None, schema, user_params)

        assert result == user_params

    def test_validation_failure_missing_required(self):
        """测试缺少必需字段时验证失败"""
        schema = json.dumps(
            {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            }
        )

        user_params = {"age": 30}

        with pytest.raises(ValidationError) as exc_info:
            validate_and_merge_params(None, schema, user_params)

        assert "'name' is a required property" in str(exc_info.value)

    def test_validation_failure_wrong_type(self):
        """测试类型错误时验证失败"""
        schema = json.dumps(
            {"type": "object", "properties": {"age": {"type": "integer"}}}
        )

        user_params = {"age": "not_a_number"}

        with pytest.raises(ValidationError):
            validate_and_merge_params(None, schema, user_params)

    def test_merge_and_validate(self):
        """测试合并和验证同时进行"""
        default_params = json.dumps({"repo": "default_repo"})
        schema = json.dumps(
            {
                "type": "object",
                "properties": {
                    "repo": {"type": "string"},
                    "branch": {"type": "string"},
                },
                "required": ["repo", "branch"],
            }
        )

        user_params = {"branch": "main"}
        result = validate_and_merge_params(default_params, schema, user_params)

        assert result == {"repo": "default_repo", "branch": "main"}

    def test_empty_params(self):
        """测试空参数"""
        result = validate_and_merge_params(None, None, None)
        assert result == {}
