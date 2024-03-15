from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader

import panpdf

CONFIG_DIR = Path(panpdf.__file__).parent / "configs"


@contextmanager
def defaults_option(metadata: dict[str, Any]) -> Generator[list[str], None, None]:
    paths: list[Path] = []
    defaults = read_defaults()
    text = yaml.dump(defaults)
    path = Path("_defaults.yaml")
    path.write_text(text, encoding="utf8")
    extra_args = ["--defaults", str(path)]
    paths.append(path)
    for name in ["include-in-header", "include-before-body", "include-after-body"]:
        text = read_include(name)
        if name == "include-in-header":
            text = "\n".join([text, create_extra_in_header(defaults)])
        elif name == "include-before-body":
            text = "\n".join([text, create_page_header(metadata)])
        text = text.strip()
        path = Path(f"_{name}.tex")
        path.write_text(text, encoding="utf8")
        extra_args += [f"--{name}", f"_{name}.tex"]
        paths.append(path)
    try:
        yield extra_args
    finally:
        for path in paths:
            path.unlink()


def read_defaults(config_dir: bool = False) -> dict[str, Any]:
    if config_dir:
        path = CONFIG_DIR / "defaults.yaml"
    else:
        path = Path("defaults.yaml")
        if not path.exists():
            path = CONFIG_DIR / "defaults.yaml"
    with path.open(encoding="utf8") as f:
        defaults = yaml.safe_load(f)
    if "csl" not in defaults:
        csl_paths = list(Path(".").glob("*.csl"))
        csl_path = csl_paths[0] if csl_paths else next(iter(CONFIG_DIR.glob("*.csl")))
        defaults["csl"] = str(csl_path)
    return defaults


def read_include(name: str, config_dir: bool = False) -> str:
    path = CONFIG_DIR / f"{name}.tex"
    text = path.read_text(encoding="utf-8")
    if CONFIG_DIR:
        return text
    path = Path(f"{name}.tex")
    if path.exists():
        text = "\n".join([text.strip(), path.read_text(encoding="utf-8")])
    return text.strip()


def create_page_header(metadata: dict[str, Any]) -> str:
    security = metadata.get("security", "")
    logo = metadata.get("logo", "")
    headerrulewidth = metadata.get("headerrulewidth", "0.0pt")
    if not security and not logo:
        return ""

    text = f"\\renewcommand{{\\headrulewidth}}{{{headerrulewidth}}}\n"
    text += "\\pagestyle{fancy}\n"
    if security:
        path = str(CONFIG_DIR / f"label/{security}.pdf").replace("\\", "/")
        text += f"\\rhead{{\\includegraphics[width=2cm]{{{path}}}}}\n"
    if logo:
        path = str(CONFIG_DIR / f"label/logotype_{logo}.pdf").replace("\\", "/")
        text += f"\\lhead{{\\includegraphics[width=2cm]{{{path}}}}}\n"
    return text


def create_extra_in_header(defaults: dict) -> str:
    variables: dict = defaults["variables"]
    names = ["section", "subsection", "subsubsection", "paragraph", "subparagraph"]
    extras: list[str] = []
    for name in names:
        arg = ""
        if font := variables.get(f"_{name}font", ""):
            arg += f"font={{{font}}}"
        if option := variables.get(f"_{name}option", ""):
            arg += f",{option}"
        if not arg:
            continue
        heading = f"\\ModifyHeading{{{name}}}{{{arg}}}"
        extras.append(heading)

    if preset := variables.get("_luatexjapreset"):
        fontspec = ",".join(preset)
        my_preset = f"\\ltjnewpreset{{my-preset}}{{{fontspec}}}\n"
        my_preset += "\\ltjapplypreset{my-preset}"
        extras.append(my_preset)

    return "\n".join(extras)


def create_standalone() -> str:
    defaults = read_defaults()
    variables: dict = defaults["variables"]
    params = {}
    for k, v in [
        ("documentclass", "jlreq"),
        ("luatexjapresetoptions", []),
        ("_luatexjapreset", []),
    ]:
        params[k] = variables.get(k, v)
    params["classoption"] = [variables.get("fontsize", "10pt")]
    if o := variables.get("classoption"):
        for i in o:
            if i.startswith("jafontscale"):
                params["classoption"].append(i)
    params["font"] = {}
    params["fontoptions"] = {}
    for f in ["main", "sans", "math", "mono"]:
        if f"{f}font" in variables:
            params["font"][f] = variables[f"{f}font"]
        o = variables.get(f"{f}fontoptions", [])
        params["fontoptions"][f] = [o] if isinstance(o, str) else o

    env = Environment(loader=FileSystemLoader(CONFIG_DIR))
    template = env.get_template("standalone.jinja2")
    return template.render(params)


# Used in main.py
def read_source(filename: str) -> str:
    path = CONFIG_DIR / filename
    return path.read_text(encoding="utf-8")
