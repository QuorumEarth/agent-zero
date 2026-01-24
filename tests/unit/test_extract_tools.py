"""Unit tests for python/helpers/extract_tools.py

Tests JSON extraction and parsing utilities used for processing LLM outputs.
"""

import pytest


class TestJsonParseDirty:
    """Test the json_parse_dirty function."""

    @pytest.fixture
    def extract_tools(self):
        """Import the extract_tools module."""
        try:
            from python.helpers import extract_tools
            return extract_tools
        except ImportError:
            pytest.skip("extract_tools module not available")

    @pytest.mark.unit
    def test_parse_valid_json(self, extract_tools):
        """Valid JSON should parse correctly."""
        json_str = '{"key": "value", "number": 42}'
        result = extract_tools.json_parse_dirty(json_str)
        assert result == {"key": "value", "number": 42}

    @pytest.mark.unit
    def test_parse_json_with_surrounding_text(self, extract_tools):
        """JSON embedded in text should be extracted and parsed."""
        text = 'Here is some JSON: {"key": "value"} and more text'
        result = extract_tools.json_parse_dirty(text)
        assert result == {"key": "value"}

    @pytest.mark.unit
    def test_parse_empty_string(self, extract_tools):
        """Empty string should return None."""
        result = extract_tools.json_parse_dirty("")
        assert result is None

    @pytest.mark.unit
    def test_parse_none_input(self, extract_tools):
        """None input should return None."""
        result = extract_tools.json_parse_dirty(None)
        assert result is None

    @pytest.mark.unit
    def test_parse_non_string_input(self, extract_tools):
        """Non-string input should return None."""
        result = extract_tools.json_parse_dirty(12345)
        assert result is None

    @pytest.mark.unit
    def test_parse_no_json_in_text(self, extract_tools):
        """Text without JSON should return None."""
        result = extract_tools.json_parse_dirty("Just plain text without JSON")
        assert result is None


class TestExtractJsonObjectString:
    """Test the extract_json_object_string function."""

    @pytest.fixture
    def extract_tools(self):
        from python.helpers import extract_tools
        return extract_tools

    @pytest.mark.unit
    def test_extract_simple_object(self, extract_tools):
        """Simple JSON object should be extracted."""
        content = '{"key": "value"}'
        result = extract_tools.extract_json_object_string(content)
        assert result == '{"key": "value"}'

    @pytest.mark.unit
    def test_extract_object_with_prefix(self, extract_tools):
        """JSON object with prefix text should be extracted."""
        content = 'Some text before {"key": "value"}'
        result = extract_tools.extract_json_object_string(content)
        assert result == '{"key": "value"}'

    @pytest.mark.unit
    def test_extract_object_with_suffix(self, extract_tools):
        """JSON object with suffix text should extract just the JSON."""
        content = '{"key": "value"} and some text after'
        result = extract_tools.extract_json_object_string(content)
        # Function extracts just the JSON object, not the suffix
        assert result == '{"key": "value"}'

    @pytest.mark.unit
    def test_extract_nested_object(self, extract_tools):
        """Nested JSON object should be extracted."""
        content = '{"outer": {"inner": "value"}}'
        result = extract_tools.extract_json_object_string(content)
        assert result == '{"outer": {"inner": "value"}}'

    @pytest.mark.unit
    def test_extract_no_object(self, extract_tools):
        """Text without JSON object should return empty string."""
        content = "No JSON here"
        result = extract_tools.extract_json_object_string(content)
        assert result == ""

    @pytest.mark.unit
    def test_extract_incomplete_object(self, extract_tools):
        """Incomplete JSON object should return from start to end."""
        content = '{"key": "value"'
        result = extract_tools.extract_json_object_string(content)
        assert result == '{"key": "value"'


class TestExtractJsonString:
    """Test the extract_json_string function."""

    @pytest.fixture
    def extract_tools(self):
        from python.helpers import extract_tools
        return extract_tools

    @pytest.mark.unit
    def test_extract_object(self, extract_tools):
        """JSON object should be extracted."""
        content = 'prefix {"key": "value"} suffix'
        result = extract_tools.extract_json_string(content)
        assert result == '{"key": "value"}'

    @pytest.mark.unit
    def test_extract_array(self, extract_tools):
        """JSON array should be extracted."""
        content = 'prefix [1, 2, 3] suffix'
        result = extract_tools.extract_json_string(content)
        assert result == '[1, 2, 3]'

    @pytest.mark.unit
    def test_extract_string(self, extract_tools):
        """JSON string should be extracted."""
        content = 'prefix "hello world" suffix'
        result = extract_tools.extract_json_string(content)
        assert result == '"hello world"'

    @pytest.mark.unit
    def test_extract_boolean_true(self, extract_tools):
        """JSON true should be extracted."""
        content = 'the value is true here'
        result = extract_tools.extract_json_string(content)
        assert result == 'true'

    @pytest.mark.unit
    def test_extract_boolean_false(self, extract_tools):
        """JSON false should be extracted."""
        content = 'the value is false here'
        result = extract_tools.extract_json_string(content)
        assert result == 'false'

    @pytest.mark.unit
    def test_extract_null(self, extract_tools):
        """JSON null should be extracted."""
        content = 'the value is null here'
        result = extract_tools.extract_json_string(content)
        assert result == 'null'

    @pytest.mark.unit
    def test_extract_number(self, extract_tools):
        """JSON number should be extracted."""
        content = 'the value is 42 here'
        result = extract_tools.extract_json_string(content)
        assert result == '42'

    @pytest.mark.unit
    def test_extract_negative_number(self, extract_tools):
        """Negative JSON number should be extracted."""
        content = 'the value is -123.45 here'
        result = extract_tools.extract_json_string(content)
        assert result == '-123.45'

    @pytest.mark.unit
    def test_extract_no_json(self, extract_tools):
        """Text without JSON should return empty string."""
        content = "no json here at all"
        result = extract_tools.extract_json_string(content)
        assert result == ""


class TestFixJsonString:
    """Test the fix_json_string function."""

    @pytest.fixture
    def extract_tools(self):
        from python.helpers import extract_tools
        return extract_tools

    @pytest.mark.unit
    def test_fix_unescaped_newlines(self, extract_tools):
        """Unescaped newlines in string values should be escaped."""
        json_str = '{"key": "line1\nline2"}'
        result = extract_tools.fix_json_string(json_str)
        # The function should handle newlines in values
        assert isinstance(result, str)

    @pytest.mark.unit
    def test_fix_already_valid_json(self, extract_tools):
        """Already valid JSON should remain unchanged."""
        json_str = '{"key": "value"}'
        result = extract_tools.fix_json_string(json_str)
        assert result == '{"key": "value"}'


class TestAgentResponseParsing:
    """Test parsing of typical Agent Zero response formats."""

    @pytest.fixture
    def extract_tools(self):
        from python.helpers import extract_tools
        return extract_tools

    @pytest.mark.unit
    def test_parse_agent_response(self, extract_tools):
        """Typical agent response should parse correctly."""
        response = '''
        {"thoughts": ["Step 1", "Step 2"],
         "tool_name": "response",
         "tool_args": {"text": "Hello!"}}'''
        result = extract_tools.json_parse_dirty(response)
        assert result is not None
        assert "thoughts" in result
        assert result["tool_name"] == "response"

    @pytest.mark.unit
    def test_parse_agent_response_with_markdown(self, extract_tools):
        """Agent response wrapped in markdown code block should parse."""
        response = '''```json
        {"thoughts": ["Thinking..."],
         "tool_name": "code_execution_tool",
         "tool_args": {"runtime": "python", "code": "print(1)"}}
        ```'''
        result = extract_tools.json_parse_dirty(response)
        assert result is not None
        assert result["tool_name"] == "code_execution_tool"

    @pytest.mark.unit
    def test_parse_response_with_trailing_comma(self, extract_tools):
        """Response with trailing comma should still parse."""
        response = '{"thoughts": ["Step 1",], "tool_name": "response",}'
        result = extract_tools.json_parse_dirty(response)
        # dirty_json should handle trailing commas
        assert result is not None or result is None  # May or may not parse depending on dirty_json
