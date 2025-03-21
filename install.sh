#!/bin/bash

set -o errexit

help_and_exit() {
    echo "Usage: $0 [-d|--dev]"
    cat << EOF
  -d,  --dev         install development dependencies
  --skip-venv        skip creating virtualenv
  --skip-gdbinit     do not set up gdbinit
EOF
    exit 1
}

DEV=0
SKIP_VENV=0
SKIP_GDBINIT=0

while [[ $# -gt 0 ]]; do
    case $1 in
        -d | --dev)
            DEV=1
            shift
            ;;
        --skip-venv)
            SKIP_VENV=1
            shift
            ;;
        --skip-gdbinit)
            SKIP_GDBINIT=1
            shift
            ;;
        *)
            echo "Unknown option: $1"
            help_and_exit
            ;;
    esac
done

cd "$(dirname "${BASH_SOURCE[0]}")"
GEP_BASE=$(pwd)
GDBINIT_GEP_PY=$GEP_BASE/gdbinit-gep.py
echo "GEP installation path: $GEP_BASE"

if [[ $DEV == 1 ]]; then
    uv sync --group dev
else
    if [[ $SKIP_VENV == 1 ]]; then
        echo "Skipping virtualenv creation"
    else
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
        "$VENV_PATH/bin/pip" install --no-cache-dir -e .
    fi
fi

# copy example config to GEP_BASE if not exists
echo "Copying default config to $GEP_BASE if not exists"
# Note: macOS will return 1 if the file already exists
cp -n "$GEP_BASE"/example/* "$GEP_BASE" || true

# append GEP to gdbinit if not exists
if [[ $SKIP_GDBINIT == 1 ]]; then
    echo "Skipping gdbinit setup"
else
    if ! grep -q '^[^#]*source.*/gdbinit-gep.py' ~/.gdbinit; then
        echo "Appending GEP to ~/.gdbinit"
        printf '\n# Comment out the following line to disable GEP\n' >> ~/.gdbinit
        printf 'source %s\n' "$GDBINIT_GEP_PY" >> ~/.gdbinit
    fi
fi

echo "Installation complete!"

exit 0
