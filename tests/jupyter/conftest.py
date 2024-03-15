import pytest


@pytest.fixture(scope="session")
def store(notebook_dir):
    from panpdf.jupyter.stores import Store

    return Store([notebook_dir])


@pytest.fixture(params=["png", "pgf", "pdf", "svg"])
def fmt(request):
    return request.param
