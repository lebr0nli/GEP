#!/bin/bash
# This is modified from https://github.com/pwndbg/pwndbg/blob/dev/lint.sh

set -o errexit

help_and_exit() {
    echo "Usage: $0 [-f|--fix]"
    echo "  -f,  --fix         Apply fixes instead of just checking"
    exit 1
}

if [[ $# -gt 1 ]]; then
    help_and_exit
fi

FIX=0

while [[ $# -gt 0 ]]; do
    case $1 in
        -f | --fix)
            FIX=1
            shift
            ;;
        *)
            help_and_exit
            ;;
    esac
done

set -o xtrace

cd "$(dirname "${BASH_SOURCE[0]}")"
GEP_BASE=$(pwd)
# shellcheck disable=SC1091
source "$GEP_BASE/.venv/bin/activate"

VERMIN_TARGETS=(
    "gdbinit-gep.py"
    "example/geprc.py"
    "tests/"
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

ty check

if [[ $FIX == 1 ]]; then
    shfmt -i 4 -bn -ci -sr -w "${LINT_SHELL_FILES[@]}"
else
    shfmt -i 4 -bn -ci -sr -d "${LINT_SHELL_FILES[@]}"
fi

shellcheck "${LINT_SHELL_FILES[@]}"

vermin -vvv --no-tips -q -t=3.8- --violations "${VERMIN_TARGETS[@]}"
