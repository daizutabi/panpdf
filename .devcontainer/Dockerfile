FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu

RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-xetex texlive-luatex texlive-latex-recommended texlive-fonts-recommended \
    texlive-latex-extra texlive-lang-japanese texlive-fonts-extra \
    libcairo2 pipx

WORKDIR /tmp

ARG pandoc_version=3.1.12.3
RUN wget https://github.com/jgm/pandoc/releases/download/${pandoc_version}/pandoc-${pandoc_version}-1-amd64.deb \
    && dpkg -i pandoc-${pandoc_version}-1-amd64.deb
