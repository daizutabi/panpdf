# import panflute as pf

# from panpdf.filters.outputcell import OutputCell


# def test_outputcell_fenced_code():
#     text = "```julia\na = 1\n```\n\n```output\n1\n```\n"
#     code = pf.convert_text(text)[1]  # type:ignore
#     code = OutputCell().action(code, None)  # type:ignore
#     tex = pf.convert_text(code, input_format="panflute", output_format="latex")
#     assert "\\vspace{-0.5\\baselineskip}\\definecolor" in tex  # type:ignore
#     assert "\\definecolor{shadecolor}{RGB}{240,240,250}" in tex  # type:ignore
