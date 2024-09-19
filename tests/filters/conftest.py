from pathlib import Path

import pytest


@pytest.fixture
def defaults():
    path = Path("tests/examples/defaults.yaml")
    assert path.exists()
    return path
