FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu

RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-xetex texlive-luatex texlive-latex-recommended texlive-fonts-recommended \
    texlive-latex-extra texlive-lang-japanese texlive-fonts-extra \
    libcairo2 pipx

WORKDIR /tmp

ARG pandoc_version="3.1.12.3"
RUN wget https://github.com/jgm/pandoc/releases/download/${pandoc_version}/pandoc-${pandoc_version}-1-amd64.deb \
    && dpkg -i pandoc-${pandoc_version}-1-amd64.deb

# RUN wget https://github.com/pypa/hatch/releases/download/hatch-v${hatch_version}/hatch-${hatch_version}-x86_64-unknown-linux-gnu.tar.gz \
#     &&
#     && tar -zxvf hatch-${hatch_version}-x86_64-unknown-linux-gnu.tar.gz \
#     && mv hatch-${hatch_version}-x86_64-unknown-linux-gnu /usr/local/bin/hatch \
#     && hatch self update