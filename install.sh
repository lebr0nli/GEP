#!/bin/bash

pip install --target="$HOME/GEP/" prompt_toolkit==2.0.10
cp gdbinit-gep "$HOME/GEP/.gdbinit-gep"
cp gdbinit-gep.py "$HOME/GEP/.gdbinit-gep.py"
cp geprc.py "$HOME/GEP/geprc.py"
