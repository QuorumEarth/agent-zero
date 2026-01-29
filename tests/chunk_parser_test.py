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

ex1 = "response goes here"
ex2 = "<think>reasoning goes here</thi"


@pytest.mark.parametrize("example", [ex1, ex2])
def test_example(example: str):
    res = models.ChatGenerationResult()
    for i in range(len(example)):
        char = example[i]
        chunk = res.add_chunk({"response_delta": char, "reasoning_delta": ""})
        print(i, ":", chunk)
