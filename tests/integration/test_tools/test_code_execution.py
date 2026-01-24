"""
Integration Tests for Code Execution Tool

These tests verify the code_execution_tool works correctly with
various runtimes (Python, terminal, Node.js).
"""

import pytest
import asyncio
from unittest.mock import MagicMock


# =============================================================================
# Test: Python Code Execution
# =============================================================================

class TestPythonExecution:
    """
    Test Python code execution through the code_execution_tool.
    """

    @pytest.fixture
    def mock_context(self, mock_agent_context, tool_test_session):
        """Create context with unique session for test isolation."""
        mock_agent_context.test_session = tool_test_session
        return mock_agent_context

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_python_print_output(self, mock_context):
        """
        Python print statements should be captured in output.
        """
        try:
            from python.tools.code_execution_tool import Tool as CodeExecutionTool

            tool = CodeExecutionTool()
            result = await tool.execute(
                agent=mock_context,
                runtime="python",
                code="print('Hello from Python!')",
                session=mock_context.test_session
            )

            assert "Hello from Python!" in result
        except ImportError:
            pytest.skip("code_execution_tool not available")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_python_variable_output(self, mock_context):
        """
        Python expressions should return their values.
        """
        try:
            from python.tools.code_execution_tool import Tool as CodeExecutionTool

            tool = CodeExecutionTool()
            result = await tool.execute(
                agent=mock_context,
                runtime="python",
                code="x = 5 * 7\nprint(f'Result: {x}')",
                session=mock_context.test_session
            )

            assert "35" in result or "Result: 35" in result
        except ImportError:
            pytest.skip("code_execution_tool not available")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_python_import_standard_library(self, mock_context):
        """
        Should be able to import standard library modules.
        """
        try:
            from python.tools.code_execution_tool import Tool as CodeExecutionTool

            tool = CodeExecutionTool()
            result = await tool.execute(
                agent=mock_context,
                runtime="python",
                code="import os\nprint(os.getcwd())",
                session=mock_context.test_session
            )

            # Should return a path
            assert "/" in result or "\\" in result
        except ImportError:
            pytest.skip("code_execution_tool not available")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_python_error_handling(self, mock_context):
        """
        Python errors should be captured and returned.
        """
        try:
            from python.tools.code_execution_tool import Tool as CodeExecutionTool

            tool = CodeExecutionTool()
            result = await tool.execute(
                agent=mock_context,
                runtime="python",
                code="raise ValueError('Test error message')",
                session=mock_context.test_session
            )

            assert "ValueError" in result or "error" in result.lower()
        except ImportError:
            pytest.skip("code_execution_tool not available")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_python_syntax_error(self, mock_context):
        """
        Python syntax errors should be reported.
        """
        try:
            from python.tools.code_execution_tool import Tool as CodeExecutionTool

            tool = CodeExecutionTool()
            result = await tool.execute(
                agent=mock_context,
                runtime="python",
                code="def broken(",
                session=mock_context.test_session
            )

            assert "SyntaxError" in result or "error" in result.lower()
        except ImportError:
            pytest.skip("code_execution_tool not available")


# =============================================================================
# Test: Terminal Command Execution
# =============================================================================

class TestTerminalExecution:
    """
    Test terminal/shell command execution.
    """

    @pytest.fixture
    def mock_context(self, mock_agent_context, tool_test_session):
        """Create context with unique session for test isolation."""
        mock_agent_context.test_session = tool_test_session
        return mock_agent_context

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_terminal_echo(self, mock_context):
        """
        Terminal echo command should return output.
        """
        try:
            from python.tools.code_execution_tool import Tool as CodeExecutionTool

            tool = CodeExecutionTool()
            result = await tool.execute(
                agent=mock_context,
                runtime="terminal",
                code="echo 'Hello from terminal'",
                session=mock_context.test_session
            )

            assert "Hello from terminal" in result
        except ImportError:
            pytest.skip("code_execution_tool not available")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_terminal_pwd(self, mock_context):
        """
        Terminal pwd command should return current directory.
        """
        try:
            from python.tools.code_execution_tool import Tool as CodeExecutionTool

            tool = CodeExecutionTool()
            result = await tool.execute(
                agent=mock_context,
                runtime="terminal",
                code="pwd",
                session=mock_context.test_session
            )

            assert "/" in result
        except ImportError:
            pytest.skip("code_execution_tool not available")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_terminal_ls(self, mock_context):
        """
        Terminal ls command should list files.
        """
        try:
            from python.tools.code_execution_tool import Tool as CodeExecutionTool

            tool = CodeExecutionTool()
            result = await tool.execute(
                agent=mock_context,
                runtime="terminal",
                code="ls -la /tmp",
                session=mock_context.test_session
            )

            # Should contain typical ls output
            assert "total" in result.lower() or "drwx" in result or "." in result
        except ImportError:
            pytest.skip("code_execution_tool not available")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_terminal_command_not_found(self, mock_context):
        """
        Non-existent commands should report error.
        """
        try:
            from python.tools.code_execution_tool import Tool as CodeExecutionTool

            tool = CodeExecutionTool()
            result = await tool.execute(
                agent=mock_context,
                runtime="terminal",
                code="nonexistentcommand12345",
                session=mock_context.test_session
            )

            assert "not found" in result.lower() or "error" in result.lower()
        except ImportError:
            pytest.skip("code_execution_tool not available")


# =============================================================================
# Test: Session Management
# =============================================================================

class TestSessionManagement:
    """
    Test session isolation and management.
    """

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_sessions_are_isolated(self, mock_agent_context):
        """
        Different sessions should be isolated from each other.
        """
        try:
            from python.tools.code_execution_tool import Tool as CodeExecutionTool

            tool = CodeExecutionTool()

            # Set variable in session 1001
            await tool.execute(
                agent=mock_agent_context,
                runtime="python",
                code="test_var = 'session_1001'",
                session=1001
            )

            # Try to access in session 1002 - should fail
            result = await tool.execute(
                agent=mock_agent_context,
                runtime="python",
                code="print(test_var)",
                session=1002
            )

            # Should get NameError since variable doesn't exist in session 1002
            assert "NameError" in result or "not defined" in result
        except ImportError:
            pytest.skip("code_execution_tool not available")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_session_persistence(self, mock_agent_context):
        """
        Variables should persist within the same session.
        """
        try:
            from python.tools.code_execution_tool import Tool as CodeExecutionTool

            tool = CodeExecutionTool()
            session_id = 1003

            # Set variable
            await tool.execute(
                agent=mock_agent_context,
                runtime="python",
                code="persistent_var = 42",
                session=session_id
            )

            # Access in same session
            result = await tool.execute(
                agent=mock_agent_context,
                runtime="python",
                code="print(f'Value: {persistent_var}')",
                session=session_id
            )

            assert "42" in result
        except ImportError:
            pytest.skip("code_execution_tool not available")


# =============================================================================
# Test: Timeout Handling
# =============================================================================

class TestTimeoutHandling:
    """
    Test that long-running code is handled appropriately.
    """

    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_infinite_loop_timeout(self, mock_agent_context):
        """
        Infinite loops should be terminated by timeout.
        """
        try:
            from python.tools.code_execution_tool import Tool as CodeExecutionTool

            tool = CodeExecutionTool()

            # This should timeout, not hang forever
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(
                    tool.execute(
                        agent=mock_agent_context,
                        runtime="python",
                        code="while True: pass",
                        session=9999
                    ),
                    timeout=5.0
                )
        except ImportError:
            pytest.skip("code_execution_tool not available")


# =============================================================================
# Test: Security Considerations
# =============================================================================

class TestSecurityConsiderations:
    """
    Test security-related aspects of code execution.
    """

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_file_system_access(self, mock_agent_context, temp_test_dir):
        """
        Code should be able to access the file system.
        """
        try:
            from python.tools.code_execution_tool import Tool as CodeExecutionTool

            tool = CodeExecutionTool()
            test_file = temp_test_dir / "test_file.txt"

            # Create a file
            result = await tool.execute(
                agent=mock_agent_context,
                runtime="python",
                code=f"with open('{test_file}', 'w') as f: f.write('test content')\nprint('File created')",
                session=2001
            )

            assert "File created" in result
            assert test_file.exists()
        except ImportError:
            pytest.skip("code_execution_tool not available")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_environment_variable_access(self, mock_agent_context):
        """
        Code should be able to access environment variables.
        """
        try:
            from python.tools.code_execution_tool import Tool as CodeExecutionTool

            tool = CodeExecutionTool()

            result = await tool.execute(
                agent=mock_agent_context,
                runtime="python",
                code="import os\nprint(os.environ.get('PATH', 'NO_PATH'))",
                session=2002
            )

            # Should have some PATH value
            assert "NO_PATH" not in result or "/" in result
        except ImportError:
            pytest.skip("code_execution_tool not available")
