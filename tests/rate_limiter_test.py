import pytest

# Skip if heavy ML dependencies are not installed
pytest.importorskip('sentence_transformers', reason='sentence_transformers not installed')
pytest.importorskip('litellm', reason='litellm not installed')

import os

# Skip in CI environment - these tests require runtime environment
if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
    pytest.skip('Skipping tests requiring runtime environment in CI', allow_module_level=True)

import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import models


@pytest.mark.skip(reason="This test requires external API access and rate limiting setup")
@pytest.mark.asyncio
async def test_rate_limiter():
    """Test rate limiter functionality with model calls."""
    provider = "openrouter"
    name = "deepseek/deepseek-r1"

    model = models.get_chat_model(
        provider=provider,
        name=name,
        model_config=models.ModelConfig(
            type=models.ModelType.CHAT,
            provider=provider,
            name=name,
            limit_requests=5,
            limit_input=15000,
            limit_output=1000,
        )
    )

    response, reasoning = await model.unified_call(
        user_message="Tell me a joke"
    )
    print("Response: ", response)
    print("Reasoning: ", reasoning)
    assert response is not None
