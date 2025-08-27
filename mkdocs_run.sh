#!/bin/bash

# Activate the venv
if [ -n "$WINDIR" ] || [ -n "$MSYSTEM" ]; then
    echo "Sorry : you are on Windows"
    source venv_mkdocs/Scripts/activate
else
    source venv_mkdocs/bin/activate
fi

# running mkdocs
mkdocs serve

# Desactivate the venv
deactivate
