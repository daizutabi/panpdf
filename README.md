# panpdf

[![PyPI Version][pypi-v-image]][pypi-v-link]
[![Python Version][python-v-image]][python-v-link]
[![Build Status][GHAction-image]][GHAction-link]
[![Coverage Status][codecov-image]][codecov-link]

**panpdf** is a powerful toolkit that bridges the gap between
data science and academic publishing by seamlessly converting
Jupyter Notebooks into high-quality PDF documents.

## Key Features

- **High-Fidelity Visualizations**: Render matplotlib, seaborn, and holoviews
  plots in stunning PGF format for perfect LaTeX integration
- **Scientific Excellence**: Produce publication-ready documents with
  beautiful mathematical formulas and professional-looking figures
- **Streamlined Workflow**: Integrate with existing Jupyter-based data
  analysis pipelines

## Getting Started

```bash
pip install panpdf
```

## Usage

```bash
panpdf src -o a.pdf -n ../notebooks -d defaults.yaml -C
```

For more details, use `panpdf --help`.

```bash
panpdf --help
```

## Why panpdf?

As data science and academic research become increasingly intertwined,
the need for tools that can produce professional publications directly
from analysis code has never been greater. panpdf empowers researchers,
data scientists, and technical writers to maintain a single source
of truth — your Jupyter Notebook — while generating beautiful PDF
documents suitable for:

- Academic papers and research articles
- Technical reports and documentation
- Data analysis presentations
- Educational materials and tutorials

## Community & Contribution

panpdf is an open-source project that thrives on community contribution.
Whether you're reporting bugs, suggesting features, or contributing code,
your involvement helps make scientific publishing more accessible to everyone.

Join us in revolutionizing how data science meets academic publishing!

<!-- Badges -->
[pypi-v-image]: https://img.shields.io/pypi/v/panpdf.svg
[pypi-v-link]: https://pypi.org/project/panpdf/
[python-v-image]: https://img.shields.io/pypi/pyversions/panpdf.svg
[python-v-link]: https://pypi.org/project/panpdf
[GHAction-image]: https://github.com/daizutabi/panpdf/actions/workflows/ci.yaml/badge.svg?branch=main&event=push
[GHAction-link]: https://github.com/daizutabi/panpdf/actions?query=event%3Apush+branch%3Amain
[codecov-image]: https://codecov.io/github/daizutabi/panpdf/coverage.svg?branch=main
[codecov-link]: https://codecov.io/github/daizutabi/panpdf?branch=main
