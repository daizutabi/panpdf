import panflute as pf
import pytest

TEXT = """
# section {#sec:section}

## subsection {#sec:subsection}

![caption pgf](pgf.ipynb){#fig:pgf}

![caption png](png.ipynb){#fig:png}

![caption pdf](pdf.ipynb){#fig:pdf}

|a|b|
|-|-|
|1|2|

: table caption 1 {#tbl:markdown}

$$y=f(x)$$ {#eq:markdown}

[@sec:section] [@sec:subsection]
[@fig:pgf] [@fig:png] [@fig:pdf]
[@tbl:markdown]
[@eq:markdown]
"""


@pytest.fixture
def doc(store):
    from panpdf.filters.attributes import Attributes
    from panpdf.filters.jupyter import Jupyter

    attributes = Attributes()
    jupyter = Jupyter(store=store)
    doc = pf.convert_text(TEXT, standalone=True)
    doc = attributes.run(doc)  # type:ignore
    return jupyter.run(doc)
