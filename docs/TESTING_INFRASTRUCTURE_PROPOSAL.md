# Agent Zero Testing Infrastructure Proposal

## Executive Summary

This document proposes a comprehensive testing infrastructure for Agent Zero, based on research of 39+ open-source agent frameworks and industry best practices. The proposal addresses the critical gap where deterministic components receive ~70% of test coverage while LLM-based components receive <5%.

**Key Recommendations:**
- Adopt pytest as the foundation with specialized plugins for AI agent testing
- Implement VCR.py-based HTTP mocking for deterministic, cost-effective LLM tests
- Use DeepEval for LLM-specific evaluation metrics
- Deploy a two-tier CI/CD strategy: fast mocked tests on PRs, full tests on main
- Target 60% code coverage for deterministic components within 30 days

---

## 1. Directory Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── pytest.ini                  # Pytest configuration
├── requirements-test.txt       # Test dependencies
│
├── unit/                       # Fast, isolated tests (~70% of tests)
│   ├── __init__.py
│   ├── test_dirty_json.py      # JSON parsing utilities
│   ├── test_extract_tools.py   # Tool extraction logic
│   ├── test_strings.py         # String utilities
│   ├── test_memory_ops.py      # Memory CRUD operations
│   ├── test_history.py         # History management
│   └── test_prompts.py         # Prompt template rendering
│
├── integration/                # Component integration tests (~20% of tests)
│   ├── __init__.py
│   ├── test_tools/
│   │   ├── test_code_execution.py
│   │   ├── test_memory_tools.py
│   │   ├── test_search_engine.py
│   │   └── test_document_query.py
│   ├── test_mcp/
│   │   ├── test_mcp_handler.py
│   │   └── test_sequential_thinking.py
│   └── cassettes/              # VCR.py recorded HTTP responses
│       └── *.yaml
│
├── e2e/                        # End-to-end agent tests (~5% of tests)
│   ├── __init__.py
│   ├── test_conversations.py   # Full conversation flows
│   ├── test_multi_agent.py     # Subordinate delegation
│   └── test_specialized_agents.py  # Quorum agents
│
├── behavioral/                 # Agent instruction compliance (~5% of tests)
│   ├── __init__.py
│   ├── test_response_format.py # JSON response structure
│   ├── test_tool_selection.py  # Correct tool usage
│   └── test_safety.py          # Safety constraints
│
├── performance/                # Benchmarks (optional)
│   ├── __init__.py
│   ├── test_latency.py
│   └── test_memory_perf.py
│
├── fixtures/                   # Test data and helpers
│   ├── __init__.py
│   ├── agents.py               # Agent factory fixtures
│   ├── conversations.py        # Conversation test cases
│   ├── mocks.py                # Mock objects
│   └── data/
│       ├── test_cases.yaml     # Parameterized test data
│       └── sample_files/       # Test documents
│
└── data/                       # Test datasets
    ├── prompts/                # Test prompts
    └── expected_outputs/       # Expected responses for snapshots
```

---

## 2. Test Categories with Examples

### 2.1 Unit Tests

**Purpose:** Test deterministic components in isolation. These should be fast (<1s each) and require no external dependencies.

**What to Test:**

| Component | File | Test Focus |
|-----------|------|------------|
| JSON Parsing | `helpers/dirty_json.py` | Malformed JSON handling, edge cases |
| Tool Extraction | `helpers/extract_tools.py` | Tool call parsing from LLM output |
| String Utilities | `helpers/strings.py` | Text manipulation functions |
| Memory Operations | `helpers/memory.py` | CRUD operations (mocked storage) |
| History Management | `helpers/history.py` | Message history operations |
| Prompt Templates | `prompts/` | Variable substitution |

**Example: Testing dirty_json.py**

```python
# tests/unit/test_dirty_json.py
import pytest
from python.helpers.dirty_json import DirtyJson

class TestDirtyJson:
    """Test JSON parsing with malformed input."""

    def test_parse_valid_json(self):
        """Valid JSON should parse correctly."""
        result = DirtyJson.parse_string('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parse_json_with_trailing_comma(self):
        """Should handle trailing commas."""
        result = DirtyJson.parse_string('{"key": "value",}')
        assert result == {"key": "value"}

    @pytest.mark.parametrize("invalid_input", [
        "",
        "not json at all",
        "{incomplete",
    ])
    def test_parse_invalid_json_raises(self, invalid_input):
        """Invalid JSON should raise appropriate error."""
        with pytest.raises(Exception):
            DirtyJson.parse_string(invalid_input)
```

### 2.2 Integration Tests

**Purpose:** Test component interactions with mocked external dependencies.

**Mocking Strategy:**
- Use VCR.py to record/replay HTTP calls to LLM APIs
- Use Docker sandbox for code execution tests
- Mock file system operations where needed

**Example: Testing code_execution_tool**

```python
# tests/integration/test_tools/test_code_execution.py
import pytest
from unittest.mock import Mock, patch

class TestCodeExecutionTool:
    """Test code execution tool."""

    @pytest.fixture
    def mock_context(self):
        """Create mock agent context."""
        ctx = Mock()
        ctx.config = Mock()
        ctx.config.code_exec_docker_enabled = False
        return ctx

    def test_python_execution_success(self, mock_context):
        """Should execute Python code and return output."""
        from python.tools.code_execution_tool import execute

        result = execute(
            context=mock_context,
            runtime="python",
            code="print('hello world')",
            session=0
        )

        assert "hello world" in result.lower()

    def test_terminal_execution_success(self, mock_context):
        """Should execute terminal commands."""
        from python.tools.code_execution_tool import execute

        result = execute(
            context=mock_context,
            runtime="terminal",
            code="echo 'test output'",
            session=0
        )

        assert "test output" in result

    def test_python_execution_error_handling(self, mock_context):
        """Should handle Python errors gracefully."""
        from python.tools.code_execution_tool import execute

        result = execute(
            context=mock_context,
            runtime="python",
            code="raise ValueError('test error')",
            session=0
        )

        assert "error" in result.lower() or "ValueError" in result
```

**Example: Testing with VCR.py for HTTP mocking**

```python
# tests/integration/test_tools/test_search_engine.py
import pytest
import vcr

# VCR configuration for this module
my_vcr = vcr.VCR(
    cassette_library_dir='tests/integration/cassettes',
    record_mode='once',
    match_on=['uri', 'method'],
    filter_headers=['authorization', 'x-api-key'],
)

class TestSearchEngine:
    """Test search engine tool with recorded responses."""

    @my_vcr.use_cassette('search_python_testing.yaml')
    def test_search_returns_results(self, mock_context):
        """Should return search results."""
        from python.tools.search_engine import execute

        result = execute(
            context=mock_context,
            query="python testing best practices"
        )

        assert len(result) > 0
        assert any('python' in r.lower() for r in result)
```

### 2.3 End-to-End Tests

**Purpose:** Test complete agent conversation flows.

**Example: Testing full conversation**

```python
# tests/e2e/test_conversations.py
import pytest
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ConversationTurn:
    user_input: str
    expected_tool_calls: Optional[List[str]] = None
    expected_response_contains: Optional[List[str]] = None
    max_iterations: int = 10

@dataclass
class ConversationFixture:
    name: str
    description: str
    turns: List[ConversationTurn]

# Test fixtures
BASIC_MATH = ConversationFixture(
    name="basic_math",
    description="Test basic mathematical operations",
    turns=[
        ConversationTurn(
            user_input="What is 15 * 7?",
            expected_response_contains=["105"],
        ),
    ]
)

@pytest.mark.e2e
@pytest.mark.vcr()
class TestConversations:
    """End-to-end conversation tests."""

    @pytest.mark.parametrize("conversation", [BASIC_MATH], ids=lambda c: c.name)
    def test_conversation(self, agent, conversation):
        """Run conversation and verify expectations."""
        for turn in conversation.turns:
            result = agent.run(turn.user_input)

            if turn.expected_response_contains:
                for expected in turn.expected_response_contains:
                    assert expected.lower() in result.response.lower()
```

### 2.4 Behavioral Tests

**Purpose:** Verify agent follows instructions and maintains expected behavior.

**Example: Testing with LLM-as-Judge (DeepEval)**

```python
# tests/behavioral/test_response_quality.py
import pytest
from deepeval import assert_test
from deepeval.metrics import GEval, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

class TestResponseQuality:
    """Test response quality using LLM-as-judge."""

    def test_response_is_helpful(self, agent):
        """Response should be helpful and relevant."""
        result = agent.run("How do I create a Python virtual environment?")

        test_case = LLMTestCase(
            input="How do I create a Python virtual environment?",
            actual_output=result.response
        )

        helpfulness = GEval(
            name="Helpfulness",
            criteria="The response provides clear, actionable instructions",
            evaluation_params=["actual_output"],
            threshold=0.7
        )

        assert_test(test_case, [helpfulness])

    def test_response_relevancy(self, agent):
        """Response should be relevant to the query."""
        query = "What is the capital of France?"
        result = agent.run(query)

        test_case = LLMTestCase(
            input=query,
            actual_output=result.response,
            retrieval_context=["Paris is the capital of France"]
        )

        relevancy = AnswerRelevancyMetric(threshold=0.7)
        assert_test(test_case, [relevancy])
```

---

## 3. Recommended Dependencies

### 3.1 Core Testing Stack

Create `tests/requirements-test.txt`:

```
# Core testing framework
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
pytest-xdist>=3.5.0        # Parallel test execution
pytest-timeout>=2.2.0      # Test timeouts
pytest-mock>=3.12.0        # Enhanced mocking

# HTTP mocking and recording
vcrpy>=6.0.0               # Record/replay HTTP calls
pytest-recording>=0.13.0   # VCR.py pytest integration
responses>=0.25.0          # HTTP mocking

# LLM evaluation
deepeval>=0.21.0           # LLM evaluation metrics

# Snapshot testing
syrupy>=4.6.0              # Snapshot assertions

# Property-based testing
hypothesis>=6.100.0        # Property-based testing

# Utilities
dirty-equals>=0.7.0        # Flexible assertions
freezegun>=1.4.0           # Time mocking
faker>=24.0.0              # Test data generation

# Performance testing (optional)
pytest-benchmark>=4.0.0    # Benchmarking
```

### 3.2 Installation

```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Or add to main requirements.txt with [test] extra
pip install -e ".[test]"
```

---

## 4. CI/CD Integration

### 4.1 Updated GitHub Actions Workflow

Replace `.github/workflows/ci.yml` with:

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [quorum, main]
  pull_request:
    branches: [quorum, main]
  workflow_dispatch:
    inputs:
      run_e2e:
        description: 'Run E2E tests with real LLM'
        required: false
        default: 'false'
        type: boolean

env:
  PYTHON_VERSION: '3.11'

jobs:
  # Stage 1: Fast checks (< 2 min)
  lint:
    name: Lint & Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install linting tools
        run: pip install flake8 black isort mypy

      - name: Run flake8
        run: flake8 python/ --count --show-source --statistics --max-line-length=120

      - name: Check formatting with black
        run: black --check python/ tests/

      - name: Check import sorting
        run: isort --check-only python/ tests/

  # Stage 2: Unit tests (< 3 min)
  unit-tests:
    name: Unit Tests
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r tests/requirements-test.txt

      - name: Run unit tests
        run: |
          pytest tests/unit -v \
            --tb=short \
            --cov=python \
            --cov-report=xml:coverage-unit.xml \
            --cov-report=term-missing \
            --junitxml=junit-unit.xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage-unit.xml
          flags: unit
          fail_ci_if_error: false

  # Stage 3: Integration tests (< 5 min)
  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r tests/requirements-test.txt

      - name: Run integration tests (mocked)
        run: |
          pytest tests/integration -v \
            --tb=short \
            --vcr-record=none \
            --junitxml=junit-integration.xml

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-integration
          path: junit-integration.xml

  # Stage 4: E2E tests (optional, on main or manual)
  e2e-tests:
    name: E2E Tests
    runs-on: ubuntu-latest
    needs: integration-tests
    if: |
      github.ref == 'refs/heads/main' ||
      github.ref == 'refs/heads/quorum' ||
      github.event.inputs.run_e2e == 'true'
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r tests/requirements-test.txt

      - name: Run E2E tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          pytest tests/e2e -v \
            --tb=short \
            --timeout=120 \
            --junitxml=junit-e2e.xml

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-e2e
          path: junit-e2e.xml

  # Security scanning (parallel)
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install security tools
        run: pip install bandit safety

      - name: Run Bandit
        run: bandit -r python/ -x ./venv,./tests --severity-level medium -f json -o bandit-report.json || true

      - name: Upload security report
        uses: actions/upload-artifact@v4
        with:
          name: security-report
          path: bandit-report.json
```

### 4.2 Two-Tier Testing Strategy

| Tier | Trigger | Tests Run | LLM Calls | Duration |
|------|---------|-----------|-----------|----------|
| **Fast** | Every PR | Unit + Integration (mocked) | None | < 5 min |
| **Full** | Main branch, manual | All including E2E | Real API | < 15 min |

### 4.3 Cost Optimization

1. **VCR Cassettes**: Record LLM responses once, replay forever
2. **Cheaper Models in CI**: Use `gpt-3.5-turbo` instead of `gpt-4` for tests
3. **Token Limits**: Cap max_tokens in test configurations
4. **Test Sampling**: Run subset of E2E tests on PRs, full suite nightly

---

## 5. Implementation Phases

### Phase 1: Foundation Setup (1-2 days)

**Goals:**
- Set up test directory structure
- Install dependencies
- Create shared fixtures
- Write first unit tests

**Tasks:**
- [ ] Create `tests/` directory structure
- [ ] Create `tests/requirements-test.txt`
- [ ] Create `tests/conftest.py` with shared fixtures
- [ ] Create `tests/pytest.ini` configuration
- [ ] Write 5-10 unit tests for `dirty_json.py`
- [ ] Write 5-10 unit tests for `strings.py`
- [ ] Update CI workflow to run tests

**Success Criteria:**
- `pytest tests/unit` runs successfully
- CI pipeline passes with unit tests
- Coverage report generated

### Phase 2: Integration Tests (2-3 days)

**Goals:**
- Test tool execution
- Set up VCR.py for HTTP mocking
- Test memory operations

**Tasks:**
- [ ] Create integration test fixtures
- [ ] Write tests for `code_execution_tool`
- [ ] Write tests for `memory_*` tools
- [ ] Write tests for `search_engine` with VCR cassettes
- [ ] Write tests for `document_query`
- [ ] Set up cassette recording workflow

**Success Criteria:**
- Integration tests run without external API calls
- VCR cassettes recorded for HTTP-dependent tests
- 50% coverage on tools directory

### Phase 3: E2E and Behavioral Tests (3-5 days)

**Goals:**
- Test full agent conversations
- Test subordinate delegation
- Test specialized Quorum agents
- Implement LLM-as-judge evaluation

**Tasks:**
- [ ] Create conversation test fixtures
- [ ] Write E2E tests for basic conversations
- [ ] Write tests for `call_subordinate`
- [ ] Write tests for specialized agents (Data_Architect, ProForma_Agent, etc.)
- [ ] Integrate DeepEval for response quality testing
- [ ] Create behavioral test suite

**Success Criteria:**
- E2E tests pass with mocked LLM responses
- Behavioral tests verify response format compliance
- DeepEval metrics integrated

### Phase 4: Performance Benchmarks (Optional, 2-3 days)

**Goals:**
- Establish performance baselines
- Identify bottlenecks
- Set up regression tracking

**Tasks:**
- [ ] Write latency benchmarks for tool execution
- [ ] Write memory operation benchmarks
- [ ] Set up benchmark comparison in CI
- [ ] Document performance baselines

**Success Criteria:**
- Benchmark suite runs in CI
- Performance regressions detected automatically

---

## 6. Agent Zero-Specific Testing

### 6.1 Testing Tool Execution

```python
# tests/integration/test_tools/test_code_execution.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

class TestCodeExecutionTool:
    """Test the code_execution_tool."""

    @pytest.fixture
    def mock_agent_context(self):
        """Create a mock agent context."""
        ctx = Mock()
        ctx.id = "test-agent-001"
        ctx.config = Mock()
        ctx.config.code_exec_docker_enabled = False
        ctx.log = Mock()
        return ctx

    @pytest.mark.asyncio
    async def test_python_print_output(self, mock_agent_context):
        """Python code should capture print output."""
        # Import the actual tool
        import sys
        sys.path.insert(0, '/a0')
        from python.tools import code_execution_tool

        result = await code_execution_tool.execute(
            agent=mock_agent_context,
            runtime="python",
            code="print('Hello, World!')",
            session=99  # Use unique session for test isolation
        )

        assert "Hello, World!" in result

    @pytest.mark.asyncio
    async def test_terminal_echo(self, mock_agent_context):
        """Terminal should execute shell commands."""
        from python.tools import code_execution_tool

        result = await code_execution_tool.execute(
            agent=mock_agent_context,
            runtime="terminal",
            code="echo 'test123'",
            session=99
        )

        assert "test123" in result

    @pytest.mark.asyncio
    async def test_python_error_captured(self, mock_agent_context):
        """Python errors should be captured and returned."""
        from python.tools import code_execution_tool

        result = await code_execution_tool.execute(
            agent=mock_agent_context,
            runtime="python",
            code="raise ValueError('intentional error')",
            session=99
        )

        assert "ValueError" in result or "error" in result.lower()
```

### 6.2 Testing Memory Operations

```python
# tests/integration/test_tools/test_memory_tools.py
import pytest
from unittest.mock import Mock, patch, AsyncMock

class TestMemoryTools:
    """Test memory save/load/delete operations."""

    @pytest.fixture
    def mock_agent_context(self):
        """Create mock context with memory."""
        ctx = Mock()
        ctx.id = "test-agent-001"
        ctx.log = Mock()
        # Mock the memory system
        ctx.memory = Mock()
        ctx.memory.save = AsyncMock(return_value="mem-uuid-123")
        ctx.memory.load = AsyncMock(return_value=[{"content": "test data"}])
        ctx.memory.delete = AsyncMock(return_value=True)
        return ctx

    @pytest.mark.asyncio
    async def test_memory_save(self, mock_agent_context):
        """Should save text to memory and return ID."""
        from python.tools import memory_save

        result = await memory_save.execute(
            agent=mock_agent_context,
            text="Important information to remember"
        )

        mock_agent_context.memory.save.assert_called_once()
        assert "mem-uuid-123" in result or "saved" in result.lower()

    @pytest.mark.asyncio
    async def test_memory_load(self, mock_agent_context):
        """Should load memories matching query."""
        from python.tools import memory_load

        result = await memory_load.execute(
            agent=mock_agent_context,
            query="important information",
            threshold=0.7,
            limit=5
        )

        mock_agent_context.memory.load.assert_called_once()

    @pytest.mark.asyncio
    async def test_memory_delete(self, mock_agent_context):
        """Should delete memories by ID."""
        from python.tools import memory_delete

        result = await memory_delete.execute(
            agent=mock_agent_context,
            ids="mem-uuid-123, mem-uuid-456"
        )

        mock_agent_context.memory.delete.assert_called()
```

### 6.3 Testing Subordinate Delegation

```python
# tests/integration/test_tools/test_call_subordinate.py
import pytest
from unittest.mock import Mock, AsyncMock, patch

class TestCallSubordinate:
    """Test subordinate agent delegation."""

    @pytest.fixture
    def mock_parent_context(self):
        """Create mock parent agent context."""
        ctx = Mock()
        ctx.id = "parent-agent-001"
        ctx.number = 0
        ctx.log = Mock()
        ctx.config = Mock()
        return ctx

    @pytest.mark.asyncio
    async def test_spawn_new_subordinate(self, mock_parent_context):
        """Should spawn new subordinate with reset=true."""
        with patch('python.tools.call_subordinate.create_subordinate') as mock_create:
            mock_subordinate = AsyncMock()
            mock_subordinate.run = AsyncMock(return_value="Subordinate response")
            mock_create.return_value = mock_subordinate

            from python.tools import call_subordinate

            result = await call_subordinate.execute(
                agent=mock_parent_context,
                message="Analyze this data",
                reset="true",
                profile="researcher"
            )

            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_continue_existing_subordinate(self, mock_parent_context):
        """Should continue with existing subordinate when reset=false."""
        # Set up existing subordinate
        mock_parent_context.subordinate = AsyncMock()
        mock_parent_context.subordinate.run = AsyncMock(return_value="Continued response")

        from python.tools import call_subordinate

        result = await call_subordinate.execute(
            agent=mock_parent_context,
            message="Continue the analysis",
            reset="false"
        )

        mock_parent_context.subordinate.run.assert_called_once()
```

### 6.4 Testing MCP Tool Calls

```python
# tests/integration/test_mcp/test_sequential_thinking.py
import pytest
from unittest.mock import Mock, AsyncMock, patch

class TestSequentialThinkingMCP:
    """Test Sequential Thinking MCP integration."""

    @pytest.fixture
    def mock_mcp_client(self):
        """Create mock MCP client."""
        client = Mock()
        client.call_tool = AsyncMock(return_value={
            "thought": "Step 1 analysis",
            "nextThoughtNeeded": True,
            "thoughtNumber": 1,
            "totalThoughts": 5
        })
        return client

    @pytest.mark.asyncio
    async def test_sequential_thinking_call(self, mock_mcp_client):
        """Should call sequential thinking tool correctly."""
        with patch('python.helpers.mcp_handler.get_client', return_value=mock_mcp_client):
            # Test the MCP tool call
            result = await mock_mcp_client.call_tool(
                "sequential_thinking.sequentialthinking",
                {
                    "thought": "Analyzing the problem",
                    "nextThoughtNeeded": True,
                    "thoughtNumber": 1,
                    "totalThoughts": 5
                }
            )

            assert result["thoughtNumber"] == 1
            assert result["nextThoughtNeeded"] == True
```

### 6.5 Testing Specialized Quorum Agents

```python
# tests/e2e/test_specialized_agents.py
import pytest
from unittest.mock import Mock, AsyncMock

class TestQuorumAgents:
    """Test specialized Quorum Earth agents."""

    @pytest.fixture
    def agent_factory(self):
        """Factory for creating test agents with specific profiles."""
        def create_agent(profile: str):
            # Create agent with specified profile
            agent = Mock()
            agent.profile = profile
            agent.run = AsyncMock()
            return agent
        return create_agent

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_data_architect_creates_import_plan(self, agent_factory):
        """Data_Architect should create structured import plans."""
        agent = agent_factory("Data_Architect")
        agent.run.return_value = Mock(
            response="## Import Plan\n1. Analyze schema\n2. Map columns",
            tool_calls=[Mock(name="sequential_thinking.sequentialthinking")]
        )

        result = await agent.run("Analyze this CSV and create an import plan")

        assert "import plan" in result.response.lower()

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_proforma_agent_financial_analysis(self, agent_factory):
        """ProForma_Agent should identify financial metrics."""
        agent = agent_factory("ProForma_Agent")
        agent.run.return_value = Mock(
            response="Burn rate: $150K/month. Runway: 18 months.",
            tool_calls=[]
        )

        result = await agent.run("Analyze the burn rate")

        assert any(term in result.response.lower()
                   for term in ["burn rate", "runway", "cash"])

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_narrative_agent_concise_output(self, agent_factory):
        """Narrative_Agent should produce concise content."""
        agent = agent_factory("Narrative_Agent")
        agent.run.return_value = Mock(
            response="The climate crisis demands action. We have the solution.",
            tool_calls=[]
        )

        result = await agent.run("Write a problem slide headline")

        # Narrative agent should be concise
        assert len(result.response) < 500

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_khosla_advisor_critique_format(self, agent_factory):
        """Khosla_Advisor should provide structured critique."""
        agent = agent_factory("Khosla_Advisor")
        agent.run.return_value = Mock(
            response="## 5-Second Verdict\nUnclear value prop\n## What to Cut\nSlide 3",
            tool_calls=[]
        )

        result = await agent.run("Critique this pitch deck")

        # Should follow Khosla critique format
        assert "verdict" in result.response.lower() or "cut" in result.response.lower()
```

---

## 7. Configuration Files

### 7.1 pytest.ini

```ini
# tests/pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (may use mocks)
    e2e: End-to-end tests (may use real LLM)
    behavioral: Behavioral compliance tests
    performance: Performance benchmarks
    slow: Tests that take > 10 seconds

# Async mode
asyncio_mode = auto

# Default options
addopts =
    -v
    --tb=short
    --strict-markers
    -ra

# Timeout for individual tests
timeout = 60

# Coverage settings
[coverage:run]
source = python
omit =
    */tests/*
    */__pycache__/*
    */venv/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
```

### 7.2 VCR Configuration

```python
# tests/conftest.py (VCR section)
import vcr

# Global VCR configuration
vcr_config = vcr.VCR(
    cassette_library_dir='tests/integration/cassettes',
    record_mode='once',  # Record once, replay forever
    match_on=['uri', 'method', 'body'],
    filter_headers=[
        'authorization',
        'x-api-key',
        'openai-api-key',
        'anthropic-api-key',
    ],
    filter_post_data_parameters=['api_key'],
    decode_compressed_response=True,
)

@pytest.fixture(scope='module')
def vcr_cassette_dir(request):
    """Return the directory for VCR cassettes."""
    return 'tests/integration/cassettes'
```

---

## 8. Quick Start Commands

```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Run all tests
pytest

# Run only unit tests (fast)
pytest tests/unit -v

# Run integration tests
pytest tests/integration -v

# Run with coverage report
pytest --cov=python --cov-report=html

# Run specific test file
pytest tests/unit/test_dirty_json.py -v

# Run tests matching pattern
pytest -k "memory" -v

# Run tests with specific marker
pytest -m "unit" -v
pytest -m "not e2e" -v  # Skip E2E tests

# Run in parallel (faster)
pytest -n auto

# Record new VCR cassettes
pytest tests/integration --vcr-record=new_episodes

# Generate coverage report
pytest --cov=python --cov-report=html --cov-report=term-missing
open htmlcov/index.html
```

---

## 9. Success Metrics

### Phase 1 Completion Criteria
- [ ] Test directory structure created
- [ ] `pytest tests/unit` runs successfully
- [ ] CI pipeline runs tests on every PR
- [ ] At least 20 unit tests passing

### Phase 2 Completion Criteria
- [ ] Integration tests for 5+ tools
- [ ] VCR cassettes recorded for HTTP-dependent tests
- [ ] 40% code coverage on `python/tools/`

### Phase 3 Completion Criteria
- [ ] E2E tests for 3+ conversation scenarios
- [ ] Behavioral tests verify JSON response format
- [ ] DeepEval metrics integrated
- [ ] 60% overall code coverage

### Long-term Goals
- [ ] 80% code coverage on deterministic components
- [ ] < 5 minute CI pipeline for PRs
- [ ] Zero flaky tests
- [ ] Performance regression detection

---

## 10. References

### Documentation
- [pytest Documentation](https://docs.pytest.org/)
- [VCR.py Documentation](https://vcrpy.readthedocs.io/)
- [DeepEval Documentation](https://docs.confident-ai.com/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

### Research
- AI Agent Testing Research Report: `/root/ai_agent_testing_research_report.md`
- "Testing Practices and Challenges in AI Agent Development" (2024)
- Khosla Ventures: "10 Commandments of Pitch Decks"

### Related Projects
- [awesome-ai-agent-testing](https://github.com/chaosync-org/awesome-ai-agent-testing)
- [AgentBench](https://github.com/THUDM/AgentBench)
- [pytest-evals](https://github.com/AlmogBaku/pytest-evals)

---

## Appendix A: Test Data Management

### YAML-Based Test Cases

```yaml
# tests/fixtures/data/test_cases.yaml
test_cases:
  - id: "math_001"
    category: "calculation"
    input: "What is 15 * 7?"
    expected:
      contains: ["105"]
    tags: ["math", "simple"]

  - id: "code_001"
    category: "code_execution"
    input: "Run Python code to print 'Hello World'"
    expected:
      tool_calls: ["code_execution_tool"]
      contains: ["Hello World"]
    tags: ["python", "execution"]

  - id: "memory_001"
    category: "memory"
    input: "Remember that my favorite color is blue"
    expected:
      tool_calls: ["memory_save"]
    follow_up:
      input: "What is my favorite color?"
      expected:
        contains: ["blue"]
    tags: ["memory", "persistence"]
```

### Loading Test Cases

```python
# tests/fixtures/test_cases.py
import yaml
from pathlib import Path

def load_test_cases(category=None, tags=None):
    """Load test cases from YAML file."""
    path = Path(__file__).parent / "data" / "test_cases.yaml"
    with open(path) as f:
        data = yaml.safe_load(f)

    cases = data["test_cases"]

    if category:
        cases = [c for c in cases if c["category"] == category]
    if tags:
        cases = [c for c in cases if any(t in c.get("tags", []) for t in tags)]

    return cases
```

---

## Appendix B: Handling Non-Deterministic Outputs

### Semantic Similarity Assertions

```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticAssertion:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def assert_similar(self, actual: str, expected: str, threshold: float = 0.7):
        embeddings = self.model.encode([actual, expected])
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        assert similarity >= threshold, f"Similarity {similarity:.2f} < {threshold}"

# Usage
semantic = SemanticAssertion()

def test_response_meaning():
    result = agent.run("Explain what Python is")
    semantic.assert_similar(
        result.response,
        "Python is a high-level programming language",
        threshold=0.6
    )
```

### Statistical Testing

```python
import statistics

def test_response_consistency(agent, n_runs=5):
    """Run same query multiple times and check consistency."""
    query = "What is the capital of Japan?"
    responses = [agent.run(query).response for _ in range(n_runs)]

    # Check that "Tokyo" appears in majority of responses
    tokyo_count = sum(1 for r in responses if "Tokyo" in r)
    assert tokyo_count >= n_runs * 0.8, f"Only {tokyo_count}/{n_runs} contained Tokyo"
```

---

*Document Version: 1.0*
*Created: 2026-01-24*
*Author: Agent Zero Developer Agent*
