#!/bin/bash

# install prompt_toolkit
if [ "$(which python3)" ]; then
    python3 -m pip install --no-cache-dir prompt_toolkit
elif [ "$(which python)" ]; then
    python -m pip install --no-cache-dir prompt_toolkit
elif [ "$(which pip)" ]; then
    pip install --no-cache-dir prompt_toolkit
else
    echo "Can't find pip in your env, please install it and run again"
    exit 1
fi

# create a folder for GEP
mkdir -p ~/GEP/

# check curl or wget
if [ "$(which curl)" ]; then
    curl --silent --location https://raw.githubusercontent.com/lebr0nli/GEP/main/gdbinit-gep --output ~/GEP/.gdbinit-gep
    curl --silent --location https://raw.githubusercontent.com/lebr0nli/GEP/main/gdbinit-gep.py --output ~/GEP/.gdbinit-gep.py
    curl --silent --location https://raw.githubusercontent.com/lebr0nli/GEP/main/geprc.py --output ~/GEP/geprc.py
elif [ "$(which wget)" ]; then
    wget -O ~/GEP/.gdbinit-gep -q https://raw.githubusercontent.com/lebr0nli/GEP/main/gdbinit-gep
    wget -O ~/GEP/.gdbinit-gep.py -q https://raw.githubusercontent.com/lebr0nli/GEP/main/gdbinit-gep.py
    wget -O ~/GEP/geprc.py -q https://raw.githubusercontent.com/lebr0nli/GEP/main/geprc.py
else
    echo "Can't find curl or wget in your env, please install it and run again"
    exit 1
fi

# backup gdbinit
if [ -f ~/.gdbinit ]; then
    cp ~/.gdbinit ~/.gdbinit.old
fi

# append gep to gdbinit
if ! grep -q gep ~/.gdbinit; then
    echo -e '\nsource ~/GEP/.gdbinit-gep\n' >> ~/.gdbinit
fi

exit 0