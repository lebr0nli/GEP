#!/bin/sh
set -eu

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

while [ $# -gt 0 ]; do
    case $1 in
        -d | --dev)
            DEV=1
            ;;
        --skip-venv)
            SKIP_VENV=1
            ;;
        --skip-gdbinit)
            SKIP_GDBINIT=1
            ;;
        *)
            echo "Unknown option: $1"
            help_and_exit
            ;;
    esac
    shift
done

cd "$(dirname "$0")"
GEP_BASE=$(pwd)
GDBINIT_GEP_PY=$GEP_BASE/gdbinit-gep.py
echo "GEP installation path: $GEP_BASE"

if [ "$DEV" -eq 1 ]; then
    uv sync --group dev
else
    if [ "$SKIP_VENV" -eq 1 ]; then
        echo "Skipping virtualenv creation"
    else
        # find python path
        PYVER=$(gdb -batch -q --nx -ex 'pi import platform; print(".".join(platform.python_version_tuple()[:2]))')
        PYTHON=$(gdb -batch -q --nx -ex 'pi import sys; print(sys.executable)')
        if ! uname -a | grep -q Darwin > /dev/null; then
            PYTHON="${PYTHON}${PYVER}"
        fi
        VENV_PATH=$GEP_BASE/.venv
        echo "Creating virtualenv in path: ${VENV_PATH}"
        "$PYTHON" -m venv "$VENV_PATH"
        PYTHON=$VENV_PATH/bin/python
        echo "Installing dependencies"
        "$PYTHON" -m pip install -U pip
        "$VENV_PATH/bin/pip" install --no-cache-dir -e .
    fi
fi

echo "Copying default config to $GEP_BASE if not exists"
for file in "$GEP_BASE"/example/*; do
    [ -f "$file" ] || continue
    filename=$(basename "$file")
    dest="$GEP_BASE/$filename"
    if [ -e "$dest" ]; then
        :
    else
        cp "$file" "$dest"
        echo "  Copied: $filename"
    fi
done

if [ "$SKIP_GDBINIT" -eq 1 ]; then
    echo "Skipping gdbinit setup"
else
    if [ -f "$HOME/.gdbinit" ] && grep -q '^[^#]*source.*/gdbinit-gep.py' "$HOME/.gdbinit"; then
        :
    else
        echo "Appending GEP to ~/.gdbinit"
        {
            echo
            echo "# Comment out the following line to disable GEP"
            echo "source $GDBINIT_GEP_PY"
        } >> "$HOME/.gdbinit"
    fi
fi

echo "Installation complete!"
exit 0
