import inspect

import panflute as pf
import pytest
from panflute import Element


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
    from panpdf.filters.filter import Filter

    filter_ = Filter(types=Element)
    filter_.run(doc)
    assert len(filter_.elements) == 9

    filter_ = Filter(types=pf.Str)
    filter_.run(doc)
    assert len(filter_.elements) == 2

    filter_ = Filter(types=pf.Code | pf.CodeBlock)
    filter_.run(doc)
    assert len(filter_.elements) == 2


def test_repr():
    from panpdf.filters.filter import Filter

    f = Filter(Element)
    assert repr(f) == "Filter()"
