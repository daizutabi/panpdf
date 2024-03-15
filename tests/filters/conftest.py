import panflute as pf
import pytest

from panpdf.filters.attributes import Attributes
from panpdf.filters.jupyter import Jupyter

TEXT = """
# section {#sec:section}

## subsection {#sec:subsection}

![figure caption 1](tests/test.ipynb){#fig:matplotlib}

![figure caption 2](){#fig:tikz}

|a|b|
|-|-|
|1|2|

: table caption 1 {#tbl:markdown}

![table caption 2](){#tbl:pandas}

$$y=f(x)$$ {#eq:markdown}

$$.$$ {#eq:sympy}

[@sec:section] [@sec:subsection]
[@fig:matplotlib] [@fig:tikz]
[@tbl:markdown] [@tbl:pandas]
[@eq:markdown] [@eq:sympy]
"""


@pytest.fixture(scope="session")
def doc(store):
    attributes = Attributes()
    jupyter = Jupyter(store=store)
    doc = pf.convert_text(TEXT, standalone=True)
    doc = attributes.run(doc)  # type:ignore
    return jupyter.run(doc)
