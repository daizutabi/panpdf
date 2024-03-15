import panflute as pf

from panpdf.core.filter import Filter


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
