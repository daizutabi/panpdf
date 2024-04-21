import holoviews as hv
import polars as pl
import pytest
from holoviews.core.dimension import LabelledData
from holoviews.core.options import Store
from holoviews.ipython.display_hooks import display_hook, image_display


@display_hook
def pgf_display(element, max_frames):
    """Used to render elements to PGF if requested in the display formats."""
    return image_display(element, max_frames, fmt="pgf")


@pytest.fixture(scope="module", autouse=True)
def obj():
    hv.extension("matplotlib")  # type: ignore
    display_formats = Store.display_formats.copy()
    Store.display_formats = ["pgf"]
    Store.set_display_hook("pgf", LabelledData, pgf_display)
    df = pl.DataFrame({"x": [1, 2], "y": [3, 4]})
    a = hv.Scatter(df, "x", "y")
    b = hv.Scatter(2 * df, "x", "y")
    yield a + b
    Store.display_formats = display_formats


def test_renderer(obj):
    renderer = Store.renderers["matplotlib"]
    plot = renderer.get_plot(obj)
    data, metadata = renderer(plot, fmt="pgf")
    assert isinstance(data, bytes)
    assert data.startswith(b"%% Creator: Matplotlib, PGF backend\n%")
    assert isinstance(metadata, dict)
    assert metadata["mime_type"] == "text/pgf"
