"""
Agent Zero Test Configuration and Shared Fixtures

This module provides shared fixtures and configuration for all tests.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Optional
from unittest.mock import AsyncMock, Mock, patch

import pytest
import vcr

# Add the project root to the path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# Pytest Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests (may use mocks)")
    config.addinivalue_line("markers", "e2e: End-to-end tests (may use real LLM)")
    config.addinivalue_line("markers", "behavioral: Behavioral compliance tests")
    config.addinivalue_line("markers", "performance: Performance benchmarks")
    config.addinivalue_line("markers", "slow: Tests that take > 10 seconds")


# =============================================================================
# VCR Configuration for HTTP Mocking
# =============================================================================

CASSETTE_DIR = Path(__file__).parent / "integration" / "cassettes"

vcr_config = vcr.VCR(
    cassette_library_dir=str(CASSETTE_DIR),
    record_mode='once',  # Record once, replay forever
    match_on=['uri', 'method', 'body'],
    filter_headers=[
        'authorization',
        'x-api-key',
        'openai-api-key',
        'anthropic-api-key',
        'api-key',
    ],
    filter_post_data_parameters=['api_key', 'key'],
    decode_compressed_response=True,
)


@pytest.fixture(scope='module')
def vcr_cassette_dir():
    """Return the directory for VCR cassettes."""
    return str(CASSETTE_DIR)


# =============================================================================
# Mock Agent Context Fixtures
# =============================================================================

@pytest.fixture
def mock_config():
    """Create a mock configuration object."""
    config = Mock()
    config.code_exec_docker_enabled = False
    config.code_exec_timeout = 30
    config.memory_subdir = "test_memory"
    config.chat_model = "gpt-4"
    config.utility_model = "gpt-3.5-turbo"
    config.embeddings_model = "text-embedding-3-small"
    return config


@pytest.fixture
def mock_log():
    """Create a mock logger."""
    log = Mock()
    log.log = Mock()
    log.error = Mock()
    log.warning = Mock()
    log.info = Mock()
    log.debug = Mock()
    return log


@pytest.fixture
def mock_memory():
    """Create a mock memory system."""
    memory = Mock()
    memory.save = AsyncMock(return_value="mem-uuid-test-123")
    memory.load = AsyncMock(return_value=[])
    memory.delete = AsyncMock(return_value=True)
    memory.forget = AsyncMock(return_value=0)
    return memory


@pytest.fixture
def mock_agent_context(mock_config, mock_log, mock_memory):
    """
    Create a comprehensive mock agent context.

    This fixture provides a fully mocked agent context suitable for
    testing tools and components in isolation.
    """
    ctx = Mock()
    ctx.id = "test-agent-001"
    ctx.number = 0
    ctx.config = mock_config
    ctx.log = mock_log
    ctx.memory = mock_memory
    ctx.subordinate = None
    ctx.history = []
    ctx.streaming = Mock()
    ctx.streaming.stream = Mock()
    return ctx


# =============================================================================
# LLM Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_llm_response():
    """
    Factory fixture for creating mock LLM responses.

    Usage:
        def test_something(mock_llm_response):
            response = mock_llm_response(content="Hello!")
    """
    def _create_response(
        content: str = "Mock response",
        tool_calls: Optional[list] = None,
        finish_reason: str = "stop"
    ):
        response = Mock()
        response.choices = [Mock()]
        response.choices[0].message = Mock()
        response.choices[0].message.content = content
        response.choices[0].message.tool_calls = tool_calls or []
        response.choices[0].finish_reason = finish_reason
        return response

    return _create_response


@pytest.fixture
def mock_openai_client(mock_llm_response):
    """Create a mock OpenAI client."""
    client = Mock()
    client.chat = Mock()
    client.chat.completions = Mock()
    client.chat.completions.create = AsyncMock(
        return_value=mock_llm_response("Mock OpenAI response")
    )
    return client


# =============================================================================
# Tool Testing Fixtures
# =============================================================================

@pytest.fixture
def tool_test_session():
    """
    Provide a unique session number for tool tests.

    This ensures test isolation when testing tools that use sessions
    (like code_execution_tool).
    """
    import random
    return random.randint(1000, 9999)


@pytest.fixture
def temp_test_dir(tmp_path):
    """
    Create a temporary directory for test files.

    The directory is automatically cleaned up after the test.
    """
    test_dir = tmp_path / "agent_zero_test"
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir


# =============================================================================
# Conversation Testing Fixtures
# =============================================================================

@pytest.fixture
def conversation_history():
    """
    Factory fixture for creating conversation histories.

    Usage:
        def test_conversation(conversation_history):
            history = conversation_history([
                ("user", "Hello"),
                ("assistant", "Hi there!")
            ])
    """
    def _create_history(messages: list):
        history = []
        for role, content in messages:
            msg = Mock()
            msg.role = role
            msg.content = content
            history.append(msg)
        return history

    return _create_history


# =============================================================================
# Async Testing Helpers
# =============================================================================

@pytest.fixture
def event_loop_policy():
    """Provide event loop policy for async tests."""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()


# =============================================================================
# Environment Fixtures
# =============================================================================

@pytest.fixture
def clean_env():
    """
    Provide a clean environment for tests.

    Saves and restores environment variables.
    """
    original_env = os.environ.copy()
    yield os.environ
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_env_vars(clean_env):
    """
    Set mock environment variables for testing.
    """
    clean_env['OPENAI_API_KEY'] = 'test-key-not-real'
    clean_env['ANTHROPIC_API_KEY'] = 'test-key-not-real'
    return clean_env


# =============================================================================
# Assertion Helpers
# =============================================================================

class AssertionHelpers:
    """Collection of custom assertion helpers."""

    @staticmethod
    def assert_valid_json_response(response: str):
        """Assert that response is valid JSON with required fields."""
        import json
        data = json.loads(response)
        assert 'thoughts' in data, "Response missing 'thoughts' field"
        assert 'tool_name' in data, "Response missing 'tool_name' field"
        assert 'tool_args' in data, "Response missing 'tool_args' field"
        return data

    @staticmethod
    def assert_contains_any(text: str, substrings: list):
        """Assert that text contains at least one of the substrings."""
        text_lower = text.lower()
        found = any(s.lower() in text_lower for s in substrings)
        assert found, f"Text does not contain any of: {substrings}"

    @staticmethod
    def assert_tool_called(mock_context, tool_name: str):
        """Assert that a specific tool was called."""
        # Implementation depends on how tools are tracked
        pass


@pytest.fixture
def assertions():
    """Provide assertion helpers."""
    return AssertionHelpers()
