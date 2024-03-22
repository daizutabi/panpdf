#!/bin/sh

sudo chown -R vscode:vscode .
pipx install hatch
hatch config set dirs.env.virtual .hatch
curl -sS https://starship.rs/install.sh | sh -s -- --yes
echo 'eval "$(starship init bash)"' >> ~/.bashrc