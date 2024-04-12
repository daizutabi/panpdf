#!/usr/bin/env bash
set -e

apt-get update
apt-get install -y sudo
curl -sL https://raw.githubusercontent.com/retorquere/zotero-deb/master/install.sh | sudo bash
apt-get update
apt-get install -y zotero
apt-get clean
rm -rf /var/lib/apt/lists/*
