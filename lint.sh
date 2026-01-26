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

run() {
    echo "+ $*"
    if ! "$@"; then
        echo "FAILED: $*" >&2
        exit 1
    fi
}

if [[ $FIX == 1 ]]; then
    run ruff check --fix
    run ruff format
else
    run ruff check
    run ruff format --diff
fi

run ty check

if [[ $FIX == 1 ]]; then
    run shfmt -i 4 -bn -ci -sr -w "${LINT_SHELL_FILES[@]}"
else
    run shfmt -i 4 -bn -ci -sr -d "${LINT_SHELL_FILES[@]}"
fi

run shellcheck "${LINT_SHELL_FILES[@]}"

run vermin -vvv --no-tips -q -t=3.10- --violations "${VERMIN_TARGETS[@]}"
