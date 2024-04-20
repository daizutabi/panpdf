#!/usr/bin/env bash
set -e

apt-get update
apt-get install -y --no-install-recommends poppler-utils
apt-get clean
rm -rf /var/lib/apt/lists/*
