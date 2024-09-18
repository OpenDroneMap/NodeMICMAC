#!/bin/bash

RUNPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -e $RUNPATH/venv ]; then
    source $RUNPATH/venv/bin/activate
fi
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/lib/$(uname -i)-linux-gnu
/usr/bin/python3 $RUNPATH/run.py "$@"
