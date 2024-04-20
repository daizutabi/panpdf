import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def test_matplotlib_raster(tmp_path: Path):
    data = np.random.randn(50, 50)
    fig, ax = plt.subplots(figsize=(3, 2))
    m = ax.imshow(data, interpolation="nearest", aspect=1)
    ax.set(xlabel="あ", ylabel="α")
    fig.colorbar(m)

    filename = tmp_path / "a.pgf"
    fig.savefig(filename, format="pgf", bbox_inches="tight")
    text = filename.read_text(encoding="utf-8")
    assert "あ" in text
    assert "α" in text
    filenames = os.listdir(tmp_path)
    assert len(filenames) == 3
    assert "a-img0.png" in filenames
    assert "a-img1.png" in filenames
