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

import asyncio

from python.helpers.dotenv import get_dotenv_value, load_dotenv
from python.helpers.email_client import read_messages


@pytest.mark.skip(reason="This test is disabled as it has external dependencies and tests nothing automatically, please move it to a script or a manual test")
@pytest.mark.asyncio
async def test():
    load_dotenv()
    messages = await read_messages(
        account_type=get_dotenv_value("TEST_SERVER_TYPE", "imap"),
        server=get_dotenv_value("TEST_EMAIL_SERVER"),
        port=int(get_dotenv_value("TEST_EMAIL_PORT", 993)),
        username=get_dotenv_value("TEST_EMAIL_USERNAME"),
        password=get_dotenv_value("TEST_EMAIL_PASSWORD"),
    )
    print(messages)
