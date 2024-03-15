import inspect

import panflute as pf
import pytest

from panpdf.filters.filter import Filter


@pytest.fixture
def doc():
    text = """# section

    abc

    `a = 1`

    ``` {#block .python .qt a=1}
    a = 1
    ```
    """
    text = inspect.cleandoc(text)
    return pf.convert_text(text, standalone=True)


def test_filter_types(doc):
    filter = Filter()  # noqa: A001
    filter.run(doc)
    assert len(filter.elements) == 9

    filter = Filter(types=pf.Str)  # noqa: A001
    filter.run(doc)
    assert len(filter.elements) == 2

    filter = Filter(types=(pf.Code, pf.CodeBlock))  # noqa: A001
    filter.run(doc)
    assert len(filter.elements) == 2
