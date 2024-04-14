#!/bin/bash
# This is modified from https://github.com/pwndbg/pwndbg/blob/dev/lint.sh

set -o errexit

help_and_exit() {
    echo "Usage: ./lint.sh [-f|--filter]"
    echo "  -f,  --filter         format code instead of just checking the format"
    exit 1
}

if [[ $# -gt 1 ]]; then
    help_and_exit
fi

FIX=0

while [[ $# -gt 0 ]]; do
    case $1 in
        -f | --format)
            FIX=1
            shift
            ;;
        *)
            help_and_exit
            ;;
    esac
done

set -o xtrace

LINT_PYTHON_FILES=(
    "gdbinit-gep.py"
    "example/geprc.py"
)
LINT_SHELL_FILES=(
    "install.sh"
    "lint.sh"
)

if [[ $FIX == 1 ]]; then
    ruff check --fix
    ruff format
else
    ruff check
    ruff format --diff
fi

if [[ $FIX == 1 ]]; then
    shfmt -i 4 -bn -ci -sr -w "${LINT_SHELL_FILES[@]}"
else
    shfmt -i 4 -bn -ci -sr -d "${LINT_SHELL_FILES[@]}"
fi

shellcheck "${LINT_SHELL_FILES[@]}"

vermin -vvv --no-tips -q -t=3.7 --violations "${LINT_PYTHON_FILES[@]}"
