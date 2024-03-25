import base64
import io

import matplotlib as mpl
import matplotlib.pyplot as plt
from IPython.lib.pretty import RepresentationPrinter

mpl.use("agg")


def test_matplotlib_figure(fmt):
    from panpdf.formatters import FUNCTIONS

    if fmt == "png":
        return

    functions = FUNCTIONS.get(("matplotlib.figure", "Figure"))
    assert functions
    function = functions.get(fmt)
    assert function

    fig, ax = plt.subplots()
    ax.plot([-1, 1], [-1, 1])

    if fmt == "pgf":
        out = io.StringIO()
        rp = RepresentationPrinter(out)

        function(fig, rp, None)
        text = out.getvalue()
        assert text.startswith("%% Creator: Matplotlib, PGF backend")
        assert text.endswith("\\endgroup%\n")

    elif fmt == "pdf":
        data = function(fig)
        assert isinstance(data, bytes)
        assert base64.b64encode(data).decode().startswith("JVBER")

    elif fmt == "svg":
        xml = function(fig)
        assert isinstance(xml, str)
        assert xml.startswith('<?xml version="1.0"')
