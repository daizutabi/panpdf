FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     texlive-xetex texlive-luatex texlive-latex-recommended texlive-fonts-recommended \
#     texlive-latex-extra texlive-lang-japanese texlive-fonts-extra \
#     libcairo2 pipx

RUN apt-get update && apt-get install -y --no-install-recommends libcairo2 pipx

WORKDIR /tmp

RUN wget http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz && \
    tar xvf install-tl-unx.tar.gz && \
    cd install-tl-2* && \
    echo "selected_scheme scheme-full" > ./texlive.profile && \
    echo "option_doc 0" >> ./texlive.profile && \
    echo "option_src 0" >> ./texlive.profile && \
    ./install-tl -profile ./texlive.profile && \
    cd .. && \
    rm -rf install-tl-*

ARG pandoc_version=3.1.12.3
RUN wget https://github.com/jgm/pandoc/releases/download/${pandoc_version}/pandoc-${pandoc_version}-1-amd64.deb && \
    dpkg -i pandoc-${pandoc_version}-1-amd64.deb

ENV PATH=/usr/local/texlive/2024/bin/x86_64-linux:$PATH

USER vscode
RUN pipx install hatch
USER root

# RUN wget https://texlive.texjp.org/2023/tlnet/install-tl-unx.tar.gz && \

# RUN apt-get update && apt-get install -y \
#   curl \
#   && rm -rf /var/lib/apt/lists/*

# ENV DOCKER_CLIENT_VERSION=latest

# RUN curl -fsSL https://get.docker.com/builds/Linux/x86_64/docker-${DOCKER_CLIENT_VERSION}.tgz \
#   | tar -xzC /usr/local/bin --strip=1 docker/docker