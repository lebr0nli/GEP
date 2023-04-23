#!/bin/bash
set -ex

# install prompt_toolkit
if [ "$(which python3)" ]; then
    python3 -m pip install --no-cache-dir prompt_toolkit
elif [ "$(which python)" ]; then
    python -m pip install --no-cache-dir prompt_toolkit
elif [ "$(which pip)" ]; then
    pip install --no-cache-dir prompt_toolkit
else
    echo "Can't find pip in your env, please install it and run again"
    exit 1
fi

# create a folder for GEP
INSTALL_PATH=${XDG_DATA_HOME:-$HOME/.local/share}/GEP
mkdir -p "$INSTALL_PATH"
GDBINIT_GEP_PY=$INSTALL_PATH/gdbinit-gep.py
echo "Installing GEP to $INSTALL_PATH ..."

# git clone the repo
git clone https://github.com/lebr0nli/GEP.git --depth=1 "$INSTALL_PATH"

if [ -f ~/.gdbinit ]; then
    # backup gdbinit if exists
    cp ~/.gdbinit ~/.gdbinit.old
else
    # create gdbinit if not exists
    touch ~/.gdbinit
fi

# append gep to gdbinit
if ! grep -q gep ~/.gdbinit; then
    printf '\nsource%s\n' "$GDBINIT_GEP_PY" >> ~/.gdbinit
fi

exit 0
