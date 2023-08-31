#!/bin/bash
set -ex

# create a folder for GEP
INSTALL_PATH=${XDG_DATA_HOME:-$HOME/.local/share}/GEP
mkdir -p "$INSTALL_PATH"
GDBINIT_GEP_PY=$INSTALL_PATH/gdbinit-gep.py
echo "Installing GEP to $INSTALL_PATH ..."

if [ -d "$INSTALL_PATH/.git" ]; then
    # git pull if exists
    cd "$INSTALL_PATH"
    git pull
else
    # git clone the repo if not exists
    git clone https://github.com/lebr0nli/GEP.git --depth=1 "$INSTALL_PATH"
fi

# find python path
PYVER=$(gdb -batch -q --nx -ex 'pi import platform; print(".".join(platform.python_version_tuple()[:2]))')
PYTHON=$(gdb -batch -q --nx -ex 'pi import sys; print(sys.executable)')
if ! uname -a | grep -q Darwin > /dev/null; then
    PYTHON+="${PYVER}"
fi

# create venv and install prompt_toolkit
VENV_PATH=$INSTALL_PATH/.venv
echo "Creating virtualenv in path: ${VENV_PATH}"
"$PYTHON" -m venv "$VENV_PATH"
PYTHON=$VENV_PATH/bin/python
"$PYTHON" -m pip install -U pip
"$VENV_PATH/bin/pip" install --no-cache-dir -U prompt_toolkit

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
