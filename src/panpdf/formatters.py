# from __future__ import annotations

# import io

# from IPython.core.getipython import get_ipython
# from typing import TYPE_CHECKING


# if TYPE_CHECKING:
#     from matplotlib.figure import Figure

# def set_formatter(module:str,fmt:str)->None:

#     pass


# def matplotlib_figure_to_pgf(fig: Figure, p, cycle):
#     with io.StringIO() as fp:
#         fig.savefig(fp, format="pgf", bbox_inches="tight")
#         text = fp.getvalue()
#         p.text(text)


# def set_formatter():
#     if ip := get_ipython():
#         formatter = ip.display_formatter.formatters["text/plain"]  # type:ignore
#         formatter.for_type_by_name("matplotlib.figure", "Figure", matplotlib_figure_to_pgf)


# set_formatter()
