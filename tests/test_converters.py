# from pathlib import Path
# from typing import TYPE_CHECKING

# import panflute as pf

# from panpdf.core.converter import Converter

# if TYPE_CHECKING:
#     from panpdf.filters.jupyter import Jupyter


# def test_convert_text(convert_text):
#     text = "# section {#zz}\n\na\nb\nあ\nい\n"
#     doc = convert_text(text)
#     assert isinstance(doc, pf.Doc)
#     assert isinstance(doc.content[0], pf.Header)
#     para = doc.content[1]
#     assert isinstance(para, pf.Para)
#     text = convert_text(text, output_format="latex")
#     o = "\\hypertarget{zz}{%\n\\section{section}\\label{zz}}\n\na b あ い"
#     assert text == o
#     text = convert_text(doc, output_format="panflute")
#     assert isinstance(text, pf.Doc)


# def test_convert_text_image(convert_text):
#     text = "![caption](tests/test.ipynb){#fig:tikz}"
#     doc = convert_text(text)
#     assert isinstance(doc, pf.Doc)
#     para = doc.content[0]
#     assert isinstance(para, pf.Para)
#     image = para.content[0]
#     assert isinstance(image, pf.RawInline)


# def test_convert(convert, tmpdir):
#     directory = Path(tmpdir)
#     path = directory / "a.md"
#     path.write_text("# section {#zz}\n\na\nb\nあ\nい\n", encoding="utf8")
#     tex = convert(path, output_format="latex")
#     o = "\\hypertarget{zz}{%\n\\section{section}\\label{zz}}\n\na\nb\nあ\nい"
#     assert o in tex
#     doc = convert(path)
#     assert isinstance(doc, pf.Doc)
#     convert(path, output=".tex")
#     path_ = Path(".") / "a.tex"
#     assert path_.exists()
#     path_.unlink()
#     convert(path, output="xxx.tex")
#     path_ = Path(".") / "xxx.tex"
#     assert path_.exists()
#     path_.unlink()


# def test_converter_fields():
#     converter = Converter(citeproc=True, notebook_dir="abc")
#     assert "zotero" in converter.filters
#     jupyter: Jupyter = converter.filters["jupyter"]  # type:ignore
#     assert str(jupyter.store.path[0]).endswith("abc")
