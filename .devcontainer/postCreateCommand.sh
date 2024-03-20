#!/bin/sh

sudo chown -R vscode:vscode .
pipx install hatch
hatch config set dirs.env.virtual .hatch