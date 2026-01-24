"""Unit tests for python/helpers/files.py

Tests file handling utilities used throughout Agent Zero.
Focuses on pure functions that don't require filesystem access.
"""

import pytest
import os
import tempfile


class TestFilePathUtilities:
    """Test file path manipulation utilities."""

    @pytest.fixture
    def files_module(self):
        """Import the files module."""
        try:
            from python.helpers import files
            return files
        except ImportError:
            pytest.skip("files module not available")

    @pytest.mark.unit
    def test_get_abs_path_relative(self, files_module):
        """Relative path should be converted to absolute."""
        result = files_module.get_abs_path("test.txt")
        assert os.path.isabs(result)

    @pytest.mark.unit
    def test_get_abs_path_already_absolute(self, files_module):
        """Absolute path should remain unchanged."""
        abs_path = "/root/test.txt"
        result = files_module.get_abs_path(abs_path)
        assert result == abs_path or result.endswith("test.txt")

    @pytest.mark.unit
    def test_basename_simple(self, files_module):
        """Should extract filename from path."""
        result = files_module.basename("/path/to/file.txt")
        assert result == "file.txt"

    @pytest.mark.unit
    def test_basename_with_extension_removal(self, files_module):
        """Should remove extension when specified."""
        result = files_module.basename("/path/to/file.txt", ".txt")
        assert result == "file"

    @pytest.mark.unit
    def test_dirname_simple(self, files_module):
        """Should extract directory from path."""
        result = files_module.dirname("/path/to/file.txt")
        assert result == "/path/to"

    @pytest.mark.unit
    def test_exists_nonexistent(self, files_module):
        """Non-existent file should return False."""
        result = files_module.exists("/nonexistent/path/file.txt")
        assert result is False

    @pytest.mark.unit
    def test_exists_real_file(self, files_module):
        """Existing file should return True."""
        # Use a file we know exists
        result = files_module.exists("/a0/tests/conftest.py")
        assert result is True


class TestFileReadWrite:
    """Test file read/write operations."""

    @pytest.fixture
    def files_module(self):
        from python.helpers import files
        return files

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing."""
        fd, path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    @pytest.mark.unit
    def test_write_and_read_file(self, files_module, temp_file):
        """Should write and read file content correctly."""
        content = "Hello, World!"
        files_module.write_file(temp_file, content)
        result = files_module.read_file(temp_file)
        assert result == content

    @pytest.mark.unit
    def test_write_file_creates_directories(self, files_module):
        """Should create parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = os.path.join(tmpdir, "nested", "dir", "file.txt")
            files_module.write_file(nested_path, "test content")
            assert os.path.exists(nested_path)
            assert files_module.read_file(nested_path) == "test content"

    @pytest.mark.unit
    def test_read_nonexistent_file(self, files_module):
        """Reading non-existent file should raise or return empty."""
        try:
            result = files_module.read_file("/nonexistent/file.txt")
            # If it doesn't raise, it should return empty or None
            assert result in ["", None]
        except (FileNotFoundError, IOError):
            pass  # Expected behavior


class TestPlaceholderReplacement:
    """Test placeholder replacement in file content."""

    @pytest.fixture
    def files_module(self):
        from python.helpers import files
        return files

    @pytest.mark.unit
    def test_replace_placeholders_simple(self, files_module):
        """Simple placeholders should be replaced."""
        content = "Hello, {{name}}!"
        result = files_module.replace_placeholders_text(content, name="World")
        assert result == "Hello, World!"

    @pytest.mark.unit
    def test_replace_placeholders_multiple(self, files_module):
        """Multiple placeholders should all be replaced."""
        content = "{{greeting}}, {{name}}! Today is {{day}}."
        result = files_module.replace_placeholders_text(
            content, greeting="Hello", name="World", day="Monday"
        )
        assert result == "Hello, World! Today is Monday."

    @pytest.mark.unit
    def test_replace_placeholders_missing(self, files_module):
        """Missing placeholders should remain or be handled gracefully."""
        content = "Hello, {{name}}!"
        result = files_module.replace_placeholders_text(content)
        # Should either keep placeholder or replace with empty
        assert "Hello" in result


class TestCodeFenceRemoval:
    """Test removal of markdown code fences."""

    @pytest.fixture
    def files_module(self):
        from python.helpers import files
        return files

    @pytest.mark.unit
    def test_remove_code_fences_simple(self, files_module):
        """Simple code fence should be removed."""
        content = """```python
print("hello")
```"""
        result = files_module.remove_code_fences(content)
        assert "```" not in result
        assert "print" in result

    @pytest.mark.unit
    def test_remove_code_fences_with_language(self, files_module):
        """Code fence with language specifier should be removed."""
        content = """```json
{"key": "value"}
```"""
        result = files_module.remove_code_fences(content)
        assert "```" not in result
        assert "key" in result

    @pytest.mark.unit
    def test_remove_code_fences_no_fences(self, files_module):
        """Content without code fences should remain unchanged."""
        content = "Just plain text"
        result = files_module.remove_code_fences(content)
        assert result == content


class TestMimeTypeDetection:
    """Test MIME type detection for files."""

    @pytest.fixture
    def files_module(self):
        from python.helpers import files
        return files

    @pytest.mark.unit
    @pytest.mark.parametrize("filename,expected_contains", [
        ("test.txt", "text"),
        ("test.json", "json"),
        ("test.py", "python"),
        ("test.html", "html"),
        ("test.pdf", "pdf"),
        ("test.png", "image"),
        ("test.jpg", "image"),
    ])
    def test_get_mime_type(self, files_module, filename, expected_contains):
        """MIME type should be detected correctly for common extensions."""
        if hasattr(files_module, 'get_mime_type'):
            result = files_module.get_mime_type(filename)
            assert expected_contains in result.lower()
        else:
            pytest.skip("get_mime_type not available")
