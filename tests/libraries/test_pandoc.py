from panflute.tools import pandoc_version


def test_pandoc():
    v = str(pandoc_version)
    assert v.split(".")[:2] == ["3", "1"]
