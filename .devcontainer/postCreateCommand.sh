#!/bin/sh

sudo chown -R vscode:vscode .
pipx install hatch
hatch config set dirs.env.virtual .hatch
echo 'export PATH=/usr/local/texlive/2024/bin/x86_64-linux:$PATH' >> ~/.bashrc