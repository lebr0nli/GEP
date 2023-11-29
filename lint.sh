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

FORMAT=0

while [[ $# -gt 0 ]]; do
    case $1 in
        -f | --format)
            FORMAT=1
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

if [[ $FORMAT == 1 ]]; then
    isort "${LINT_PYTHON_FILES[@]}"
    black "${LINT_PYTHON_FILES[@]}"
else
    isort --check-only --diff "${LINT_PYTHON_FILES[@]}"
    black --check --diff "${LINT_PYTHON_FILES[@]}"
fi

if [[ $FORMAT == 1 ]]; then
    shfmt -i 4 -bn -ci -sr -w "${LINT_SHELL_FILES[@]}"
else
    shfmt -i 4 -bn -ci -sr -d "${LINT_SHELL_FILES[@]}"
fi

shellcheck "${LINT_SHELL_FILES[@]}"

vermin -vvv --no-tips -q -t=3.7 --violations "${LINT_PYTHON_FILES[@]}"

flake8 --show-source "${LINT_PYTHON_FILES[@]}"
