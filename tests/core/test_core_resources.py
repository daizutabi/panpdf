from pathlib import Path

import yaml

from panpdf.core.config import (
    CONFIG_DIR,
    create_extra_in_header,
    create_standalone,
    defaults_option,
    read_defaults,
)


def test_CONFIG_DIR():
    assert CONFIG_DIR.exists()


def test_read_defaults():
    defaults = read_defaults(CONFIG_DIR=True)
    defaults_ = read_defaults()
    assert defaults == defaults_
    assert isinstance(defaults, dict)
    assert "pdf-engine" in defaults
    assert "pdf-engine-opts" in defaults
    assert "variables" in defaults
    variables = defaults["variables"]
    assert isinstance(variables, dict)
    assert "documentclass" in variables
    assert "fontsize" in variables
    assert "classoption" in variables
    assert "mainfont" in variables
    assert "sansfont" in variables
    assert "mathfont" in variables
    assert "monofont" in variables
    assert "luatexjapresetoptions" in variables


def test_create_extra_in_header():
    defaults = read_defaults(CONFIG_DIR=True)
    variables = defaults["variables"]
    assert isinstance(variables, dict)
    names = ["section", "subsection", "subsubsection", "paragraph", "subparagraph"]
    extra = create_extra_in_header(defaults)
    for name in names:
        assert f"_{name}font" in variables
        assert f"\\ModifyHeading{{{name}}}" in extra
        if "section" in name:
            assert f"_{name}option" in variables


def test_default_option_latex():
    names = ["include-in-header", "include-before-body", "include-after-body"]
    paths = [Path(f"_{name}.tex") for name in names]
    for path in paths:
        assert not path.exists()
    with defaults_option({}) as extra_args:
        for path in paths:
            assert path.exists()
        path = extra_args[1]
        with Path(path).open(encoding="utf8") as f:
            defaults = yaml.safe_load(f)
        assert defaults["wrap"] == "preserve"
        text = paths[0].read_text(encoding="utf-8")
        assert "\\ModifyHeading{section}" in text
        assert "\\ModifyHeading{subparagraph}" in text
        assert "\\ltjnewpreset{my-preset}" in text
        assert "\\ltjapplypreset{my-preset}" in text
    for path in paths:
        assert not path.exists()


def test_create_standalone():
    text = create_standalone()
    for f in ["main", "sans", "mono", "math"]:
        assert f"set{f}font" in text
    assert "ltjnewpreset" in text
