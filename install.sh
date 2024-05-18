#!/bin/bash

set -o errexit

help_and_exit() {
    echo "Usage: $0 [-d|--dev]"
    cat << EOF
  -d,  --dev         install development dependencies
EOF
    exit 1
}

if [[ $# -gt 1 ]]; then
    help_and_exit
fi

DEV=0

while [[ $# -gt 0 ]]; do
    case $1 in
        -d | --dev)
            DEV=1
            shift
            ;;
        *)
            help_and_exit
            ;;
    esac
done

cd "$(dirname "${BASH_SOURCE[0]}")"
GEP_BASE=$(pwd)
GDBINIT_GEP_PY=$GEP_BASE/gdbinit-gep.py
echo "GEP installation path: $GEP_BASE"

# find python path
PYVER=$(gdb -batch -q --nx -ex 'pi import platform; print(".".join(platform.python_version_tuple()[:2]))')
PYTHON=$(gdb -batch -q --nx -ex 'pi import sys; print(sys.executable)')
if ! uname -a | grep -q Darwin > /dev/null; then
    PYTHON+="${PYVER}"
fi

# create venv and install prompt_toolkit
VENV_PATH=$GEP_BASE/.venv
echo "Creating virtualenv in path: ${VENV_PATH}"
"$PYTHON" -m venv "$VENV_PATH"
PYTHON=$VENV_PATH/bin/python
echo "Installing dependencies"
"$PYTHON" -m pip install -U pip
if [[ $DEV == 1 ]]; then
    poetry install --with dev
else
    "$VENV_PATH/bin/pip" install --no-cache-dir -e .
fi

# copy example config to GEP_BASE if not exists
echo "Copying default config to $GEP_BASE if not exists"
cp -n "$GEP_BASE"/example/* "$GEP_BASE"

# append GEP to gdbinit if not exists
if ! grep -q '^[^#]*source.*/gdbinit-gep.py' ~/.gdbinit; then
    echo "Appending GEP to ~/.gdbinit"
    printf '\n# Please make sure the following line is always the last in this file\n' >> ~/.gdbinit
    printf 'source %s\n' "$GDBINIT_GEP_PY" >> ~/.gdbinit
fi

exit 0
