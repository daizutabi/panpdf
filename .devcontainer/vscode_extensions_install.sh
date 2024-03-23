#!/bin/sh

# https://iret.media/78241

code_server_bin=$(ps -aux | grep "bin/code-server" | awk '{print $12}' | head -n 1)
code_bin=$(dirname "$code_server_bin")/remote-cli/code
$code_bin --list-extensions
extensions=`cat .devcontainer/devcontainer.json | sed 's/^ *\/\/.*//' | jq -r .customizations.vscode.extensions[]`

echo
echo "Manual install of code extensions"
echo

for extension in $extensions
do
  echo $extension
  $code_bin --install-extension $extension
done