"""Unit tests for python/helpers/strings.py

Tests string manipulation utilities used throughout Agent Zero.
"""

import pytest


class TestSanitizeString:
    """Test the sanitize_string function."""

    @pytest.fixture
    def strings_module(self):
        """Import the strings module."""
        try:
            from python.helpers import strings
            return strings
        except ImportError:
            pytest.skip("strings module not available")

    @pytest.mark.unit
    def test_sanitize_normal_string(self, strings_module):
        """Normal ASCII strings should pass through unchanged."""
        result = strings_module.sanitize_string("Hello World")
        assert result == "Hello World"

    @pytest.mark.unit
    def test_sanitize_unicode_string(self, strings_module):
        """Unicode strings should be preserved."""
        result = strings_module.sanitize_string("Hello 世界 🌍")
        assert "Hello" in result
        assert "世界" in result

    @pytest.mark.unit
    def test_sanitize_non_string_input(self, strings_module):
        """Non-string inputs should be converted to string."""
        result = strings_module.sanitize_string(12345)
        assert result == "12345"

    @pytest.mark.unit
    def test_sanitize_empty_string(self, strings_module):
        """Empty string should return empty string."""
        result = strings_module.sanitize_string("")
        assert result == ""


class TestFormatKey:
    """Test the format_key function for converting keys to readable format."""

    @pytest.fixture
    def strings_module(self):
        from python.helpers import strings
        return strings

    @pytest.mark.unit
    @pytest.mark.parametrize("input_key,expected", [
        ("camelCase", "Camel Case"),
        ("snake_case", "Snake Case"),
        ("PascalCase", "Pascal Case"),
        ("simple", "Simple"),
        ("ALLCAPS", "Allcaps"),
        ("with-dashes", "With Dashes"),
        ("with.dots", "With Dots"),
    ])
    def test_format_key_conversions(self, strings_module, input_key, expected):
        """Various key formats should be converted to Title Case."""
        result = strings_module.format_key(input_key)
        assert result == expected


class TestDictToText:
    """Test the dict_to_text function."""

    @pytest.fixture
    def strings_module(self):
        from python.helpers import strings
        return strings

    @pytest.mark.unit
    def test_simple_dict(self, strings_module):
        """Simple dict should be formatted correctly."""
        d = {"name": "John", "age": 30}
        result = strings_module.dict_to_text(d)
        assert "Name:" in result
        assert "John" in result
        assert "Age:" in result
        assert "30" in result

    @pytest.mark.unit
    def test_empty_dict(self, strings_module):
        """Empty dict should return empty string."""
        result = strings_module.dict_to_text({})
        assert result == ""


class TestTruncateText:
    """Test the truncate_text function."""

    @pytest.fixture
    def strings_module(self):
        from python.helpers import strings
        return strings

    @pytest.mark.unit
    def test_no_truncation_needed(self, strings_module):
        """Short text should not be truncated."""
        result = strings_module.truncate_text("Hello", 10)
        assert result == "Hello"

    @pytest.mark.unit
    def test_truncate_at_end(self, strings_module):
        """Long text should be truncated at end with ellipsis."""
        result = strings_module.truncate_text("Hello World", 5, at_end=True)
        assert result == "Hello..."

    @pytest.mark.unit
    def test_truncate_at_start(self, strings_module):
        """Long text should be truncated at start with ellipsis."""
        result = strings_module.truncate_text("Hello World", 5, at_end=False)
        assert result == "...World"

    @pytest.mark.unit
    def test_custom_replacement(self, strings_module):
        """Custom replacement string should be used."""
        result = strings_module.truncate_text("Hello World", 5, replacement="[...]")
        assert result == "Hello[...]"

    @pytest.mark.unit
    def test_exact_length(self, strings_module):
        """Text exactly at length should not be truncated."""
        result = strings_module.truncate_text("Hello", 5)
        assert result == "Hello"


class TestTruncateTextByRatio:
    """Test the truncate_text_by_ratio function."""

    @pytest.fixture
    def strings_module(self):
        from python.helpers import strings
        return strings

    @pytest.mark.unit
    def test_no_truncation_under_threshold(self, strings_module):
        """Text under threshold should not be truncated."""
        result = strings_module.truncate_text_by_ratio("Hello", 100)
        assert result == "Hello"

    @pytest.mark.unit
    def test_truncate_ratio_zero(self, strings_module):
        """Ratio 0 should truncate from start."""
        result = strings_module.truncate_text_by_ratio(
            "Hello World This Is Long", 15, ratio=0.0
        )
        assert result.startswith("...")

    @pytest.mark.unit
    def test_truncate_ratio_one(self, strings_module):
        """Ratio 1 should truncate from end."""
        result = strings_module.truncate_text_by_ratio(
            "Hello World This Is Long", 15, ratio=1.0
        )
        assert result.endswith("...")

    @pytest.mark.unit
    def test_truncate_ratio_middle(self, strings_module):
        """Ratio 0.5 should truncate in middle."""
        result = strings_module.truncate_text_by_ratio(
            "Hello World This Is Long", 15, ratio=0.5
        )
        assert "..." in result
        assert not result.startswith("...")
        assert not result.endswith("...")


class TestCalculateValidMatchLengths:
    """Test the calculate_valid_match_lengths function."""

    @pytest.fixture
    def strings_module(self):
        from python.helpers import strings
        return strings

    @pytest.mark.unit
    def test_identical_strings(self, strings_module):
        """Identical strings should match fully."""
        first = "Hello World"
        second = "Hello World"
        len1, len2 = strings_module.calculate_valid_match_lengths(first, second)
        assert len1 == len(first)
        assert len2 == len(second)

    @pytest.mark.unit
    def test_completely_different_strings(self, strings_module):
        """Completely different strings should have minimal match."""
        first = "AAAAAAA"
        second = "BBBBBBB"
        len1, len2 = strings_module.calculate_valid_match_lengths(first, second)
        # Should stop early due to deviation threshold
        assert len1 < len(first)
        assert len2 < len(second)

    @pytest.mark.unit
    def test_partial_match(self, strings_module):
        """Strings with common prefix should match that prefix."""
        first = "Hello World"
        second = "Hello There"
        len1, len2 = strings_module.calculate_valid_match_lengths(first, second)
        # Should match at least "Hello "
        assert len1 >= 6
        assert len2 >= 6
