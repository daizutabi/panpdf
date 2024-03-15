import pytest


@pytest.fixture(params=["png", "pgf", "pdf", "svg"])
def fmt(request):
    return request.param
