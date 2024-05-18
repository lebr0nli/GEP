#!/bin/bash

set -o errexit

help_and_exit() {
    echo "Usage: $0"
    exit 1
}

if [[ $# -gt 0 ]]; then
    help_and_exit
fi

set -o xtrace

cd "$(dirname "${BASH_SOURCE[0]}")"
GEP_BASE=$(pwd)
# shellcheck disable=SC1091
source "$GEP_BASE/.venv/bin/activate"
pytest -v tests/
