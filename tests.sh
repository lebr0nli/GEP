#!/bin/bash

set -o errexit

cd "$(dirname "${BASH_SOURCE[0]}")"
GEP_BASE=$(pwd)
# shellcheck disable=SC1091
source "$GEP_BASE/.venv/bin/activate"

make -C "$GEP_BASE/tests/fixtures" all

pytest -v "$@"
