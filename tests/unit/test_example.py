"""
Example Unit Tests for Agent Zero

This module demonstrates unit testing patterns for Agent Zero components.
These tests are fast, isolated, and don't require external dependencies.
"""

import json
import pytest
from unittest.mock import Mock, patch


# =============================================================================
# Test: dirty_json.py - JSON Parsing Utilities
# =============================================================================

class TestDirtyJsonParsing:
    """
    Test the dirty_json module for handling malformed JSON.

    The dirty_json module is critical for parsing LLM outputs which
    often contain JSON with minor formatting issues.
    """

    @pytest.fixture
    def dirty_json(self):
        """Import the dirty_json module."""
        try:
            from python.helpers.dirty_json import DirtyJson
            return DirtyJson
        except ImportError:
            pytest.skip("dirty_json module not available")

    @pytest.mark.unit
    def test_parse_valid_json(self, dirty_json):
        """Valid JSON should parse correctly."""
        input_json = '{"key": "value", "number": 42}'
        result = dirty_json.parse_string(input_json)

        assert result == {"key": "value", "number": 42}

    @pytest.mark.unit
    def test_parse_json_with_trailing_comma(self, dirty_json):
        """Should handle trailing commas in objects."""
        input_json = '{"key": "value",}'
        result = dirty_json.parse_string(input_json)

        assert result == {"key": "value"}

    @pytest.mark.unit
    def test_parse_json_with_single_quotes(self, dirty_json):
        """Should handle single quotes instead of double quotes."""
        input_json = "{'key': 'value'}"
        result = dirty_json.parse_string(input_json)

        assert result == {"key": "value"}

    @pytest.mark.unit
    def test_parse_nested_json(self, dirty_json):
        """Should handle nested JSON structures."""
        input_json = '{"outer": {"inner": "value"}}'
        result = dirty_json.parse_string(input_json)

        assert result == {"outer": {"inner": "value"}}

    @pytest.mark.unit
    def test_parse_json_array(self, dirty_json):
        """Should handle JSON arrays."""
        input_json = '[1, 2, 3, "four"]'
        result = dirty_json.parse_string(input_json)

        assert result == [1, 2, 3, "four"]

    @pytest.mark.unit
    @pytest.mark.parametrize("invalid_input,expected_type", [
        ("", type(None)),  # Empty string returns None
        ("not json at all", str),  # Plain text returns as string
        ("{incomplete", dict),  # Incomplete object returns partial dict
        ("[1, 2, 3", list),  # Incomplete array returns partial list
    ])
    def test_parse_invalid_json_handles_gracefully(self, dirty_json, invalid_input, expected_type):
        """dirty_json handles malformed JSON gracefully without raising exceptions.

        The dirty_json module is designed to be fault-tolerant for parsing
        LLM outputs which often contain malformed JSON. Instead of raising
        exceptions, it returns None, strings, or partial results.
        """
        result = dirty_json.parse_string(invalid_input)
        if expected_type is type(None):
            assert result is None, f"Expected None for empty input, got {result}"
        else:
            assert isinstance(result, expected_type), f"Expected {expected_type.__name__} for {repr(invalid_input)}, got {type(result).__name__}"


# =============================================================================
# Test: Response Format Validation
# =============================================================================

class TestResponseFormatValidation:
    """
    Test that agent responses conform to expected JSON format.

    Agent Zero responses must contain specific fields:
    - thoughts: array of reasoning steps
    - tool_name: string identifying the tool to use
    - tool_args: object with tool arguments
    """

    @pytest.mark.unit
    def test_valid_response_format(self, assertions):
        """Valid response should pass validation."""
        response = json.dumps({
            "thoughts": ["Step 1", "Step 2"],
            "tool_name": "response",
            "tool_args": {"text": "Hello!"}
        })

        data = assertions.assert_valid_json_response(response)
        assert data["tool_name"] == "response"

    @pytest.mark.unit
    def test_response_missing_thoughts_fails(self, assertions):
        """Response without thoughts should fail validation."""
        response = json.dumps({
            "tool_name": "response",
            "tool_args": {"text": "Hello!"}
        })

        with pytest.raises(AssertionError, match="thoughts"):
            assertions.assert_valid_json_response(response)

    @pytest.mark.unit
    def test_response_missing_tool_name_fails(self, assertions):
        """Response without tool_name should fail validation."""
        response = json.dumps({
            "thoughts": ["Step 1"],
            "tool_args": {"text": "Hello!"}
        })

        with pytest.raises(AssertionError, match="tool_name"):
            assertions.assert_valid_json_response(response)


# =============================================================================
# Test: String Utilities
# =============================================================================

class TestStringUtilities:
    """
    Test string manipulation utilities.
    """

    @pytest.mark.unit
    def test_assert_contains_any_success(self, assertions):
        """Should pass when text contains one of the substrings."""
        text = "The quick brown fox jumps over the lazy dog"
        assertions.assert_contains_any(text, ["cat", "fox", "bird"])

    @pytest.mark.unit
    def test_assert_contains_any_case_insensitive(self, assertions):
        """Should be case insensitive."""
        text = "Hello World"
        assertions.assert_contains_any(text, ["HELLO", "WORLD"])

    @pytest.mark.unit
    def test_assert_contains_any_failure(self, assertions):
        """Should fail when text contains none of the substrings."""
        text = "The quick brown fox"
        with pytest.raises(AssertionError):
            assertions.assert_contains_any(text, ["cat", "dog", "bird"])


# =============================================================================
# Test: Mock Agent Context
# =============================================================================

class TestMockAgentContext:
    """
    Test that mock agent context fixtures work correctly.
    """

    @pytest.mark.unit
    def test_mock_context_has_required_attributes(self, mock_agent_context):
        """Mock context should have all required attributes."""
        assert hasattr(mock_agent_context, 'id')
        assert hasattr(mock_agent_context, 'config')
        assert hasattr(mock_agent_context, 'log')
        assert hasattr(mock_agent_context, 'memory')

    @pytest.mark.unit
    def test_mock_config_has_settings(self, mock_config):
        """Mock config should have expected settings."""
        assert hasattr(mock_config, 'code_exec_docker_enabled')
        assert hasattr(mock_config, 'chat_model')

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_mock_memory_save(self, mock_memory):
        """Mock memory save should return UUID."""
        result = await mock_memory.save("test content")
        assert "mem-uuid" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_mock_memory_load(self, mock_memory):
        """Mock memory load should return list."""
        result = await mock_memory.load("query")
        assert isinstance(result, list)


# =============================================================================
# Test: LLM Response Mocking
# =============================================================================

class TestLLMResponseMocking:
    """
    Test LLM response mock fixtures.
    """

    @pytest.mark.unit
    def test_mock_llm_response_default(self, mock_llm_response):
        """Default mock response should have expected structure."""
        response = mock_llm_response()

        assert len(response.choices) == 1
        assert response.choices[0].message.content == "Mock response"
        assert response.choices[0].finish_reason == "stop"

    @pytest.mark.unit
    def test_mock_llm_response_custom_content(self, mock_llm_response):
        """Should be able to customize response content."""
        response = mock_llm_response(content="Custom content here")

        assert response.choices[0].message.content == "Custom content here"

    @pytest.mark.unit
    def test_mock_llm_response_with_tool_calls(self, mock_llm_response):
        """Should be able to add tool calls."""
        tool_call = Mock()
        tool_call.function.name = "code_execution_tool"

        response = mock_llm_response(
            content="",
            tool_calls=[tool_call]
        )

        assert len(response.choices[0].message.tool_calls) == 1


# =============================================================================
# Parameterized Test Examples
# =============================================================================

class TestParameterizedExamples:
    """
    Examples of parameterized tests for comprehensive coverage.
    """

    @pytest.mark.unit
    @pytest.mark.parametrize("input_val,expected", [
        (1, 1),
        (2, 4),
        (3, 9),
        (4, 16),
        (10, 100),
    ])
    def test_square_function(self, input_val, expected):
        """Example parameterized test."""
        result = input_val ** 2
        assert result == expected

    @pytest.mark.unit
    @pytest.mark.parametrize("tool_name,expected_valid", [
        ("response", True),
        ("code_execution_tool", True),
        ("memory_save", True),
        ("invalid_tool", False),
        ("", False),
        (None, False),
    ])
    def test_tool_name_validation(self, tool_name, expected_valid):
        """Test tool name validation logic."""
        valid_tools = {
            "response", "code_execution_tool", "memory_save",
            "memory_load", "memory_delete", "call_subordinate",
            "search_engine", "document_query", "browser_agent"
        }

        is_valid = tool_name in valid_tools if tool_name else False
        assert is_valid == expected_valid
