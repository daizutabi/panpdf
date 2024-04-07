#!/bin/sh

hatch config set dirs.env.virtual .hatch
echo 'eval "$(starship init bash)"' >> ~/.bashrc
echo "alias ll='ls -alF'" >> ~/.bashrc
mkdir -p ~/.config
cp .devcontainer/starship.toml ~/.config