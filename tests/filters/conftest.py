from pathlib import Path

import pytest


@pytest.fixture
def defaults():
    path = Path("examples/defaults.yaml")
    assert path.exists()
    return path
